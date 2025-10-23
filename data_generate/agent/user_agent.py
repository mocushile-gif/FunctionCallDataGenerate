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
from data_generate.agent.tool_agent import ToolAgent
from data_generate.prompt import *
from data_generate.utils import *
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
        
        if self.file_system_path and (not self.file_system_info_list):
            file_system=FileSystem()
            self.file_system_info_list=file_system.get_file_system_info_list(self.file_system_path)
        return self

    def _input(self):
        user_message={'role':'user','content':input('请输入指令（直接回车结束当前对话）:')}
        logger.info(f'{Fore.CYAN}USER QUESTION:{Style.RESET_ALL} {Fore.WHITE}{user_message}{Style.RESET_ALL}')
        return user_message

    def _clarify(self,task_history,assistant_tools):
        # 让用户agent看不到 assistant agent与工具交互的过程
        clean_task_history=[]
        for message in task_history:
            if message['role']=='user' or (message['role']=='assistant' and 'tool_calls' not in message):
                clean_task_history.append(message)

        clarify_question_user_prompt=''
        USER_TEMPLET = {
                "history": clean_task_history,
                "language_style":self.language_style,
        }

        if self.file_system_path and "File System Environment Information" not in clean_task_history[0]:
            File_System = {
                "file_system_info":self.file_system_info_list[0]['content'],
                "file_info":'\n'.join([info['content'] for info in self.file_system_info_list[1:]])
            }
            clarify_question_user_prompt+=FILE_TOOL_ENVIRONMENT.format(**File_System) + '\n'

        identify_task_complete_prompt = clarify_question_user_prompt + CLARIFY_USER_PROMPT.format(**USER_TEMPLET)
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

    def _init_question(self,dialogs,assistant_tools,mode_weights={"single":1, "parallel":1, "multiple":1, "dependent":1, "no_tool_use":1,"miss_param":1}):
        mode_mapping = {
            "single": SINGLE_TOOL_MODE,
            "parallel": PARALLEL_TOOL_MODE,
            "multiple": MULTIPLE_TOOL_MODE,
            "dependent": DEPENDENT_TOOL_MODE,
            "no_tool_use": NO_TOOL_MODE,
            "task": TASK_TOOL_MODE,
            "miss_param": MISS_PARAM_MODE,
        }
        language_mapping = {
            "zh": "中文",
            "en": "English"
        }

        # 语言风格设定
        if self.use_persona:
            self.language_style=random.choice(self.persona_model.get_top_n_personas(list(assistant_tools.values()),50))

        
        mode_key = random.choices(list(mode_weights.keys()),
                                  weights=list(mode_weights.values()),
                                  k=1)[0]
        mode = mode_mapping[mode_key]

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

        # 添加文件系统信息
        if self.file_system_path:
            if not clean_dialogs or (clean_dialogs and "File System Environment Information" not in clean_dialogs[0]):
                File_System = {"file_system_info":self.file_system_info_list[0]['content'],
                "file_info":'\n'.join([info['content'] for info in self.file_system_info_list[1:]])
                }
                init_question_user_prompt+=FILE_TOOL_ENVIRONMENT.format(**File_System) + '\n'
                logger.info(f'{Fore.CYAN}[USER AGENT]: with {len(self.file_system_info_list)} file system info.{Style.RESET_ALL}')
                for info in self.file_system_info_list:
                    logger.debug(f'{Fore.CYAN}[USER FILE SYSTEM INFO]{Style.RESET_ALL}: {str(info["content"])[:100]}')

        USER_TEMPLET = {"assistant_tools": list(assistant_tools.values()),
                        "history": clean_dialogs,
                        "mode": mode,
                        }
        init_question_user_prompt += INIT_QUESTION_USER_PROMPT.format(**USER_TEMPLET)
        user_agent_message = [{'role': 'system', 'content': init_question_system_prompt},
                              {'role': 'user', 'content': init_question_user_prompt}]
        # logger.debug(user_agent_message)
        user_message,error_code = self._llm_generate_query(user_agent_message,'final_query')
        if error_code==200:
            setting = f"\n语言风格:{self.language_style}\n模式:{mode_key}\n工具：{list(assistant_tools.keys())}"
            logger.info(f'{Fore.CYAN}USER MODE:{Style.RESET_ALL} {Fore.WHITE}{setting}{Style.RESET_ALL}')
            logger.info(f'{Fore.CYAN}USER QUESTION:{Style.RESET_ALL} {Fore.WHITE}{user_message}{Style.RESET_ALL}')
            return user_message,200,mode_key
        else:
            return user_message,500,mode_key

    def _llm_generate_query(self,dialogs,tag='final_query'):
        # sql、file任务，在提出问题之前，允许user_agent先去获取相关meta信息，再进行提问。
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

def sample_from_tools(n):
    import copy
    all_tools={}
    project_dir=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tools=load_tool_defines(f'{project_dir}/tools/defines/file_system_functions/',recursive=True)
    all_tools.update(tools)
    # sql工具中这三个工具为固定工具，不参与采样
    fixed_sql_tools=['get_all_table_names','get_table_info','get_column_info','get_database_info']
    sql_dirname='database_functions'
    fixed_file_tools=['display_directory_tree','get_file_info','read_file_contents']
    file_dirname='file_system_functions'
    tools_pool=copy.deepcopy(all_tools)
    for tool in fixed_sql_tools:
        if f'{sql_dirname}.{tool}' in tools_pool:
            del tools_pool[f'{sql_dirname}.{tool}']
    for tool in fixed_file_tools:
        if f'{file_dirname}.{tool}' in tools_pool:
            del tools_pool[f'{file_dirname}.{tool}']
    user_tools=dict(random.sample(list(tools_pool.items()),n))
    assistant_tools={}
    assistant_tools.update(user_tools)
    tool_response_prompt=TOOL_RESPONSE_PROMPT
    if any([sql_dirname in tool for tool in user_tools.keys()]):
        # sql工具中总是有这三个工具，便于assistant获取数据库相关信息
        assistant_tools.update({f'{sql_dirname}.{tool}':all_tools[f'{sql_dirname}.{tool}'] for tool in fixed_sql_tools})
        tool_response_prompt+=SQL_TOOL_PROMPT
    if any([file_dirname in tool for tool in user_tools.keys()]):
        # file工具中总是有这个工具，便于assistant获取相关信息
        assistant_tools.update({f'{file_dirname}.{tool}':all_tools[f'{file_dirname}.{tool}'] for tool in fixed_file_tools})
        tool_response_prompt+=FILE_TOOL_PROMPT
    return user_tools,list(assistant_tools.values()),tool_response_prompt

def sample_from_tools(n):
        tools_pool={}
        project_dir=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        tools=load_tool_defines(f'{project_dir}/tools/defines/file_system_functions/',recursive=True)
        tools_pool.update(tools)
        # 固定工具不参与采样

        category_fixed_tools={
                'file_system_functions':['display_directory_tree','get_file_info'],
                'database_functions':['display_directory_tree','get_all_table_names','get_table_info','get_column_info','get_database_info']
                }
        fixed_tool_pool={'file_system_functions':{},
                        'database_functions':{}}
        # 用于记录待删除项
        to_delete = []
        for tool_key, tool_item in tools_pool.items():
            tool_name = tool_key.split('.')[-1]
            tool_category = tool_key.split('.')[0]
            for category, fixed_tools in category_fixed_tools.items():
                if tool_name in fixed_tools and tool_category == category:
                    fixed_tool_pool[category][tool_key] = tool_item
                    to_delete.append(tool_key)
        for key in to_delete:
            del tools_pool[key]

        user_tools_dict = dict(random.sample(list(tools_pool.items()), n))
        
        assistant_tools={}
        assistant_tools.update(user_tools_dict)

        for category,fixed_tools in category_fixed_tools.items():
            if any([category in tool for tool in assistant_tools.keys()]):
                assistant_tools.update(fixed_tool_pool[category])
        assistant_tools=list(assistant_tools.values())
        return user_tools_dict,assistant_tools,None

if __name__ == '__main__':
    import logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] [%(levelname)s] [Thread:%(threadName)s - %(thread)d]\n%(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger = logging.getLogger(__name__)
    user_agent = UserAgent(llm_name='gpt',use_persona=False,lang='en',file_system_path=f'{os.environ["PROJECT_DIR"]}/working_dir/file_system_self_define')
    # user_agent = UserAgent(llm_name='qwen',use_persona=False,lang='zh')
    tools,_,_=sample_from_tools(5)
    # print(user_agent._get_file_system_info())
    # project_dir=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # all_tools=load_tool_defines(f'{project_dir}/tools/defines/file_system_functions/',recursive=True)
    # tools={tool:all_tools[tool] for tool in ['file_system_functions.code_intepreter']}
    dialogs=[]
    # dialogs=[
    #     {
    #         "content": "How can the boarding passes table in the airlines database be filtered to identify tickets with a specific seat number, assuming I know the seat number in advance?",
    #         "role": "user"
    #     },
    #     {
    #         "content": "To filter the boarding passes table in the airlines database for tickets with a specific seat number, you can use a query with a `WHERE` clause that matches the desired seat number. Here's the process:\n\n1. Retrieve the structure of the boarding passes table to confirm the column name for seat numbers.\n2. Use the column name in the `WHERE` clause to filter rows where the seat number matches the specified value.\n\nLet me first check the structure of the boarding passes table to identify the column name for seat numbers.",
    #         "role": "assistant",
    #         "tool_calls": [
    #             {
    #                 "function": {
    #                     "arguments": "{\"database_name\":\"airlines\"}",
    #                     "name": "get_all_table_names"
    #                 },
    #                 "id": "call_hXEKz3IfDXsBIULNkxPJnFBR",
    #                 "type": "function"
    #             }
    #         ]
    #     },
    #     {
    #         "role": "tool",
    #         "content": "['aircrafts_data', 'airports_data', 'boarding_passes', 'bookings', 'flights', 'seats', 'ticket_flights', 'tickets']",
    #         "tool_call_id": "call_hXEKz3IfDXsBIULNkxPJnFBR"
    #     },
    #     {
    #         "role": "assistant",
    #         "tool_calls": [
    #             {
    #                 "function": {
    #                     "arguments": "{\"database_name\":\"airlines\",\"table_name\":\"boarding_passes\"}",
    #                     "name": "get_table_info"
    #                 },
    #                 "id": "call_2J3ePRfyYfYdZ9vv1cGokG9v",
    #                 "type": "function"
    #             }
    #         ]
    #     },
    #     {
    #         "role": "tool",
    #         "content": "{'table_schema': [{'column_name': 'ticket_no', 'data_type': 'character(13)'}, {'column_name': 'flight_id', 'data_type': 'integer'}, {'column_name': 'boarding_no', 'data_type': 'integer'}, {'column_name': 'seat_no', 'data_type': 'character varying(4)'}], 'record_count': 579686}",
    #         "tool_call_id": "call_2J3ePRfyYfYdZ9vv1cGokG9v"
    #     },
    #     {
    #         "content": "The boarding passes table contains a column named `seat_no` that stores seat numbers. To filter tickets with a specific seat number, you can use the `seat_no` column in the `WHERE` clause of your query.\n\nFor example, if the seat number is \"12A\", the query would look like this:\n```sql\nSELECT * FROM boarding_passes WHERE seat_no = '12A';\n```\n\nPlease provide me a specific seat number.",
    #         "role": "assistant"
    #     }
    # ]
    # dialogs=[{"role": "system", "content": "You are an expert in composing functions. You are given a question and a set of possible functions. \nBased on the question, you may need to make one or more function/tool calls to achieve the purpose. \n\nThe current time is 2024-04-14.\n\n###Note:\n1.The model does not support any functions other than the given tools. If the user's question involves other functions, politely refuse to answer.\n2.The input parameters for the tools should default to the language of the user's input or the language specified by the user.\n3.Before calling a tool, ensure that the input parameters and their content are objectively valid. The data types of the parameters must match the tool's definition. The parameter information should be complete and match the user's requirements.\n4.Pay attention to the timeliness and relevance of the information. Do not provide outdated or incorrect information.\n5.If the tool call results in an empty output, contains errors, is not successfully executed, or is irrelevant (does not match the tool's purpose), you can try modifying the parameters and calling the tool again. After three failed attempts, please provide an appropriate apology response, indicating that there was an error in the tool call.\n6.Ensure that the tool call conforms to the JSON format, without using single quotes. If single quotes must be included, replace them with the escape character \".\n7.The tool call results may be too long, indicated by \"...truncated.\" In this case, only consider the part of the content that is not collapsed. \n"}, 
    # {"role": "user", "content": "Can you help me analyze the distribution of this dataset: [45, 67, 89, 34, 56, 78, 90, 123, 44, 67]?"}, 
    # {"role": "assistant", "tool_calls": [{"function": {"arguments": "{\"data\":[45,67,89,34,56,78,90,123,44,67]}", "name": "calculate percentiles"}, "id": "call_jkcc6dYdWMjjtgG9hrbihOTT", "type": "function"}]}, 
    # {"role": "tool", "content": "{'median': 67.0, 'Q1': 47.75, 'Q3': 86.25, 'IQR': 38.5}", "tool_call_id": "call_jkcc6dYdWMjjtgG9hrbihOTT"}, 
    # {"content": "Here is the analysis of your dataset:\n\n- **Median**: 67.0\n- **Lower Quartile (Q1)**: 47.75\n- **Upper Quartile (Q3)**: 86.25\n- **Interquartile Range (IQR)**: 38.5\n\nThis provides a summary of the dataset's distribution, with the median representing the central value, and the IQR indicating the spread of the middle 50% of the data.", "role": "assistant"},
    # ]
    # tools={"calculate percentiles":{"name": "calculate percentiles", "description": "Calculate the median, lower quartile (Q1), upper quartile (Q3), and interquartile range (IQR) of a dataset.", "parameters": {"type": "object", "properties": {"data": {"type": "array", "items": {"type": "number"}, "description": "A list of numerical values for which to calculate the percentiles."}}, "required": ["data"]}}}

    user_agent._init_question(dialogs,tools,mode_weights={"single":0, "parallel":0, "multiple":0, "dependent":0, "no_tool_use":0, "task":0,"miss_param":1})
    # user_agent._clarify(dialogs,tools)


    