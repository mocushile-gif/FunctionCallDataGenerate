import os
from pydantic import BaseModel,Field, SecretStr, model_validator
import json
from typing import List, Dict, Any, Optional
from langchain_core.utils import get_from_dict_or_env, convert_to_secret_str
from colorama import Fore, Style
import requests
from datetime import datetime
import re
import random
from collections import namedtuple
from typing import Union
from dotenv import load_dotenv
from data_generate.agent.model import *
from data_generate.prompt.fsp_user_prompt import *
from data_generate.prompt.fsp_fc_mode_prompt import *
from data_generate.utils.file_system_utils import FileSystem
import logging
logger = logging.getLogger(__name__)

load_dotenv()

class UserAgent(BaseModel):
    data_list: list = Field(default_factory=list)
    llm: Union[DOUBAOFunction, ChatGPTFunction,QWen25Function] = Field(default=None)
    llm_name: str = 'gpt4o-ptu-client'
    current_index: int = 0
    use_persona: bool = False
    persona_model: Persona = Field(default=None)
    task_history: list= Field(default_factory=list)
    language_style: str = 'A normal user'
    lang: str = 'en'
    file_system: FileSystem = Field(default=None)
    file_system_path: str = ''
    file_system_info_list: list = Field(default=None)

    class Config:
        arbitrary_types_allowed = True

    @model_validator(mode='after')
    def validate_environment(self):
        if self.use_persona:
            persona_data_path="./agent/model/persona_data/persona.jsonl"
            persona_embeddings_path="./agent/model/persona_data/persona_embeddings.pkl"
            self.persona_model=Persona(persona_data_path,persona_embeddings_path)
       
        if 'gpt' in self.llm_name:
            self.llm = ChatGPTFunction(name='gpt4o-ptu-client',args={'temperature': 1})
        elif 'doubao' in self.llm_name:
            self.llm = DOUBAOFunction()
        elif 'qwen' in self.llm_name:
            self.llm = QWen25Function(args={'temperature': 1})
        elif 'qwq' in self.llm_name:
            self.llm = QwQFunction(args={
                    'max_new_tokens': 13200,
                    'temperature': 0.6, # 更高的随机性
                    'top_p': 0.95,      # 采样更多选项
                    'top_k': 20,
                }
                )
        elif 'deepseek' in self.llm_name:
            self.llm = Deepseek25Function(args={'temperature': 1})
        else:
            raise NameError('not support')
        self.file_system=FileSystem()
        return self

    def _clarify(self,task_history,assistant_tools,mode):
        # 让用户agent看不到 assistant agent与工具交互的过程
        clean_task_history=[]
        for message in task_history:
            if message['role']=='user' or (message['role']=='assistant' and 'tool_calls' not in message):
                clean_task_history.append(message)

        clarify_question_user_prompt=''
        USER_TEMPLET = {
                "history": clean_task_history,
                "language_style":self.language_style,
                "user_question":clean_task_history[0]['content']
        }

        if mode!='miss_func' and self.file_system_info_list:
            File_System = {
                "file_system_info":self.file_system_info_list[0]['content'],
                "file_info":'\n'.join([info['content'] for info in self.file_system_info_list[1:]])
            }
            clarify_question_user_prompt+=FILE_ENVIRONMENT_FOR_CLARITY.format(**File_System) + '\n'
            logger.info(f'{Fore.CYAN}[USER AGENT]: with {len(self.file_system_info_list)} file system info.{Style.RESET_ALL}')

        identify_task_complete_prompt = clarify_question_user_prompt + CLARIFY_USER_PROMPT.format(**{"history": task_history})
        user_agent_message=[{'role':'user','content':identify_task_complete_prompt}]

        res,error_code = self.llm.chat(user_agent_message)
        user_message={'role':'user','content':res['content']}
        if error_code==200:
            if 'Finished' in user_message['content']:
                user_message='This task is completed.'
                task_complete_flag=1
            elif 'Unachievable' in user_message['content']:
                user_message='This task is not completable.'
                task_complete_flag=-1
            else:
                task_complete_flag=0
            logger.debug(f"_clarify function user_message:{json.dumps(user_message,ensure_ascii=False)}")
            logger.debug(f"_clarify function task_complete_flag:{task_complete_flag}")
    
            if task_complete_flag==0:
                clarify_question_user_prompt += CLARIFY_USER_GENERATE_QUERY_PROMPT.format(**USER_TEMPLET)
                user_agent_message=[{'role':'user','content':clarify_question_user_prompt}]
                res,error_code = self._llm_generate_query(user_agent_message,'final_input')
                logger.debug(f"_clarify function user_message generate:{json.dumps(user_message,ensure_ascii=False)}")
                user_message={'role':'user','content':res['content']}
                if error_code != 200:
                    return user_message, 0, 500
            logger.info(f'{Fore.CYAN}USER CLARIFY:{Style.RESET_ALL} {Fore.WHITE}{user_message}{Style.RESET_ALL}')
            return user_message,task_complete_flag,200
        else:
            return user_message,0,500

    def _init_question(self,dialogs,current_tools,fsp_all_tools,fsp_current_turn,mode):
        if self.file_system_path:
            self.file_system_info_list=self.file_system.get_file_system_info_list(self.file_system_path)
        language_mapping = {
            "zh": "中文",
            "en": "English"
        }

        # 语言风格设定
        if self.use_persona:
            self.language_style=random.choice(self.persona_model.get_top_n_personas(list(fsp_all_tools.values()),50))

        SYSTEM_TEMPLET = {"current_time": datetime.now().strftime('%Y-%m-%d'),
                          "language_style": self.language_style,
                          "language": language_mapping[self.lang]}
        init_question_system_prompt = INIT_QUESTION_SYSTEM_PROMPT.format(**SYSTEM_TEMPLET)

        # 让用户agent看不到 assistant agent与工具交互的过程
        clean_dialogs=[]
        for message in dialogs:
            if message['role']=='user' or (message['role']=='assistant' and 'tool_calls' not in message):
                clean_dialogs.append(message)

        
        init_question_user_prompt=''

        if mode!='miss_func' and self.file_system_info_list:
            File_System = {
                "file_system_info":self.file_system_info_list[0]['content'],
                "file_info":'\n'.join([info['content'] for info in self.file_system_info_list[1:]])
            }
            init_question_user_prompt+=FILE_TOOL_ENVIRONMENT.format(**File_System) + '\n'
            logger.info(f'{Fore.CYAN}[USER AGENT]: with {len(self.file_system_info_list)} file system info.{Style.RESET_ALL}')
            for info in self.file_system_info_list:
                logger.debug(f'{Fore.CYAN}[USER FILE SYSTEM INFO]{Style.RESET_ALL}: {str(info["content"])[:100]}')

        mode_mapping = {"parallel":PARALLEL_MODE,
                        "single":SINGLE_MODE,
                        "miss_params":MISS_PARAM_MODE,
                        "multiple_or_dependent":MULTIPLE_OR_DEPENDENT_MODE,
                        "miss_func":MISS_FUNC_MODE,}
        USER_TEMPLET = {"tools": list(current_tools.values()),
                        "fsp_current_turn": fsp_current_turn,
                        "history": clean_dialogs,
                        "mode": mode_mapping[mode],
                        }
        init_question_user_prompt += INIT_QUESTION_USER_PROMPT.format(**USER_TEMPLET)
        user_agent_message = [{'role': 'system', 'content': init_question_system_prompt},
                              {'role': 'user', 'content': init_question_user_prompt}]
        # logger.debug(user_agent_message)
        user_message,error_code = self._llm_generate_query(user_agent_message,'final_query')
        if error_code==200:
            setting = f"\n语言风格:{self.language_style}\nFSP：{fsp_current_turn}\n模式：{mode}\n工具：{list(current_tools.keys())}"
            logger.info(f'{Fore.CYAN}USER MODE:{Style.RESET_ALL} {Fore.WHITE}{setting}{Style.RESET_ALL}')
            logger.info(f'{Fore.CYAN}USER QUESTION:{Style.RESET_ALL} {Fore.WHITE}{user_message}{Style.RESET_ALL}')
            return user_message,200
        else:
            return user_message,500

    def _llm_generate_query(self,dialogs,tag='final_query'):
        try:
            res,error_code=self.llm.chat(dialogs)
            logger.debug(f'{Fore.CYAN}USER AGENT:{Style.RESET_ALL} {Fore.WHITE}{res}{Style.RESET_ALL}')
            res['role']="user"
            if f'<{tag}>' in str(res) and f'</{tag}>' in str(res):
                matches = re.findall(rf'<{tag}>\s*(.*?)\s*</{tag}>', res['content'], re.DOTALL)
                res['content']=matches[0]
                return res,200
            else:
                res['content']=res['content'].replace(f'<{tag}>','').replace(f'</{tag}>','')
                return res,200
        except Exception as e:
            logger.error(f'{Fore.RED}USER AGENT ERROR:{Style.RESET_ALL} {Fore.WHITE}{str(e)}{Style.RESET_ALL}')
            return None,500

if __name__ == '__main__':
    import logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] [%(levelname)s] [Thread:%(threadName)s - %(thread)d]\n%(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger = logging.getLogger(__name__)
    
    # try
    from data_generate.utils.file_system_utils import FileSystem
    from fsp_generate.utils import *
    import shutil
    import tempfile
    import fsp_generate
    import data_generate
    fsp_dir = os.path.dirname(fsp_generate.__file__)
    project_dir = os.path.dirname(fsp_generate.__file__)
    load_functions(f'{fsp_dir}/tools/all_tools_metadata.json')
    fsps=load_generated_fsps(f'{fsp_dir}/data/generated_fsps_execute_step5_600_enhance.json')
    fsp=fsps[5]
    n=3
    file_system_path=f'{project_dir}/working_dir/file_system_new'
    thread_id_file_system_path = f'{os.environ["HOME_DIR"]}/function_call_data_temp/function_call_file_system_try'
    os.makedirs(thread_id_file_system_path, exist_ok=True)
    temp_file_system_path = tempfile.mkdtemp(
        dir=thread_id_file_system_path)
    file_list = list(set([file_name for selected_files in fsp['selected_files'] for file_name in selected_files if file_name]))
    if os.path.exists(temp_file_system_path):
        shutil.rmtree(temp_file_system_path)
    for file_name in file_list:
        src_path = os.path.join(file_system_path, file_name)
        dst_path = os.path.join(temp_file_system_path, file_name)
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        shutil.copy2(src_path, dst_path)
    file_system = FileSystem()
    file_system_info_list = file_system.get_file_system_info_list(
        temp_file_system_path)
    
    user_agent = UserAgent(llm_name='gpt',use_persona=False,lang='en',file_system_info_list=file_system_info_list)
    dialogs=[]
    current_tools=get_tool_info_for_specific_turn(fsp,n)
    all_tools=get_all_tool_info(fsp)
    mode=fsp["fsp_mode"][n]
    fsp_current_turn=fsp["enhanced_fsp"][n]
    # print(tools)
    print(user_agent._init_question(dialogs,current_tools,all_tools,fsp_current_turn,mode))
    # shutil.rmtree(temp_file_system_path)
    # dialogs=[]
    # print(user_agent._clarify(dialogs,current_tools,mode))


    