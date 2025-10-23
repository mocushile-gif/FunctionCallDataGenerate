# -*- coding: utf-8 -*-
import json
from datetime import datetime
import os
from pydantic import BaseModel,Field, SecretStr, model_validator
from typing import List, Dict, Any, Optional
import copy
from collections import defaultdict
import random
from tqdm import tqdm
from colorama import Fore, Style
import concurrent
import threading
from concurrent.futures import ThreadPoolExecutor,TimeoutError
import uuid
import copy
import shutil
import tempfile
import ast
import traceback
import logging
from data_generate.agent.user_agent import UserAgent
from data_generate.agent.assistant_agent import AssistantAgent
from data_generate.agent.tool_agent import ToolAgent
from data_generate.agent.checker_agent import CheckerAgent
from data_generate.prompt import *
from data_generate.utils import *

lock = threading.Lock()

# 跟open_pipeline的区别是：
# 从file_system里随机摘取文件，获取文件信息后直接喂给user_agent来提问
# assistant只有code工具，可以选择是否把文件信息公开给assistant

class Pipeline(BaseModel):
    user: UserAgent = Field(default=None)
    assistant: AssistantAgent = Field(default=None)
    checker: CheckerAgent = Field(default=None)
    tool: ToolAgent = Field(default=None)
    assistant_tools: List = Field(default=None)
    all_tools: List = Field(default=None)
    user_tools: List = Field(default=None)
    save_path: str = Field(default=None)
    failed_save_path: str = Field(default=None)
    max_task_turns: int = 1
    checker_max_retries: int = 3
    assistant_n_response: int = 1
    image_dir: str = Field(default=None)
    assistant_model_name: str = 'gpt4o-ptu-client'
    checker_model_name: str = 'gpt4o-ptu-client'
    user_model_name: str = 'gpt4o-ptu-client'
    tool_model_name: str = 'gpt4o-ptu-client'
    lang: str = 'en'
    use_persona: bool = False
    tool_response_prompt: str = False
    executable_temp_working_dir: str = None
    tool_defines_path: list = Field(default=None),
    use_random_system_time: bool = False
    task_turn_weights: dict = Field(default=None)
    mode_weights: dict = Field(default=None)
    fixed_tools: list = Field(default=None) #固定工具模式
    tool_nums_distribution: dict = Field(default=None) #采样工具模式
    dynamic_adjust_mode_and_task_turn_weight: bool = False
    file_system_path: str = ''
    temp_file_system_path: str = ''
    file_system_info_list: list = Field(default=None)
    selected_files: list = Field(default=None)
    files_num: dict = Field(default=None)
    provide_file_system_info: str = 'none'
    category_fixed_tools: dict = Field(default=None)
    tool_output_limit: int=4096

    class Config:
        arbitrary_types_allowed = True

    @model_validator(mode='after')
    def validate_environment(self):
        # 初始化采样工具，用户生成问题时去除固定工具
        if self.fixed_tools:
            self.user_tools,self.assistant_tools,self.tool_response_prompt=self.init_tools()
            all_tools_dict=self.user_tools
        else:
            self.user_tools,all_tools_dict,self.assistant_tools,self.tool_response_prompt=self.sample_from_tools()
        if any(['display_directory_tree' in tool_name for tool_name in all_tools_dict.keys()]): #只有当涉及文件系统时才采样文件
            unique_id = uuid.uuid4().hex
            thread_temp_dir = os.path.join(self.executable_temp_working_dir, f"session_{unique_id}")
            # 确保路径存在
            os.makedirs(thread_temp_dir, exist_ok=True)
            # Creates a temporary directory for the file_system copy
            self.temp_file_system_path = tempfile.mkdtemp(dir=thread_temp_dir)

            # 全局设置 tempfile.tempdir(duckduckgo会创建tmp文件，多进程下偶尔报错IO错误)
            tempfile.tempdir = os.path.join(self.executable_temp_working_dir, 'tmp')
            os.makedirs(tempfile.tempdir, exist_ok=True)

            logger.info(f"temp_file_system_path:{self.temp_file_system_path}")
        
            with lock:
                if os.path.exists(self.temp_file_system_path):
                    subprocess.run(["sudo", "rm", "-rf", self.temp_file_system_path])
                # shutil.copytree(self.file_system_path, temp_file_system_path)

                file_system=FileSystem()
                file_num = int(random.choices(list(self.files_num.keys()), 
                                                        weights=list(self.files_num.values()),
                                                        k=1)[0])
                self.selected_files=file_system.extract_random_files(self.file_system_path, self.temp_file_system_path, file_num)
                self.file_system_info_list=file_system.get_file_system_info_list(self.temp_file_system_path)

            self.tool = ToolAgent(
                llm_name=self.tool_model_name,
                file_system_path=self.temp_file_system_path,
                tools=all_tools_dict,
                output_limit=self.tool_output_limit
            )

            self.user=UserAgent(
                llm_name=self.user_model_name,
                use_persona=self.use_persona,
                lang=self.lang,
                file_system_path=self.temp_file_system_path,
                file_system_info_list=self.file_system_info_list
            )
        else:
            self.tool = ToolAgent(
                llm_name=self.tool_model_name,
                tools=all_tools_dict
            )

            self.user=UserAgent(
                llm_name=self.user_model_name,
                use_persona=self.use_persona,
                lang=self.lang,
            )
        self.assistant=AssistantAgent(llm_name=self.assistant_model_name)
        self.checker=CheckerAgent(llm_name=self.checker_model_name)
        return self

    def sample_from_tools(self):
        tools_pool={}
        all_tools={}
        for tool_defines_path in self.tool_defines_path:
            tools=load_tool_defines(tool_defines_path,recursive=True)
            tools_pool.update(tools)
            all_tools.update(tools)
        # 固定工具不参与采样

        fixed_tool_pool=defaultdict(dict)
        # 用于记录待删除项
        to_delete = []
        for tool_key, tool_item in tools_pool.items():
            tool_name = tool_key.split('.')[-1]
            tool_category = tool_key.split('.')[0]
            for category, fixed_tools in self.category_fixed_tools.items():
                if tool_name in fixed_tools and tool_category == category:
                    fixed_tool_pool[category][tool_key] = tool_item
                    to_delete.append(tool_key)
        for key in to_delete:
            del tools_pool[key]

        #随机工具
        if self.dynamic_adjust_mode_and_task_turn_weight:
            self.mode_weights, self.task_turn_weights, tools_sample_nums=dynamic_adjust_weights(self.tool_nums_distribution,self.mode_weights, self.task_turn_weights)
        else:
            tools_sample_nums = tools_pool_sample(self.tool_nums_distribution)
        user_tools_dict = dict(random.sample(list(tools_pool.items()), tools_sample_nums))
        
        assistant_tools={}
        assistant_tools.update(user_tools_dict)
        tool_response_prompt=TOOL_RESPONSE_PROMPT

        for category,fixed_tools in self.category_fixed_tools.items():
            if any([category in tool for tool in assistant_tools.keys()]):
                assistant_tools.update(fixed_tool_pool[category])
                if category=='database_functions':
                    tool_response_prompt+=SQL_TOOL_PROMPT
                else:
                    tool_response_prompt+=FILE_TOOL_PROMPT
        all_tools_dict=assistant_tools
        assistant_tools=list(assistant_tools.values())
        return user_tools_dict,all_tools_dict,assistant_tools,tool_response_prompt


    def init_tools(self):
        # 只有固定工具
        all_tools={}
        for tool_defines_path in self.tool_defines_path:
            tools=load_tool_defines(tool_defines_path,recursive=True)
            all_tools.update(tools)
        tools_dict={tool:all_tools[tool] for tool in self.fixed_tools}
        assistant_tools=list(tools_dict.values())

        tool_response_prompt=TOOL_RESPONSE_PROMPT
        tool_response_prompt+=FIXED_TOOL_PROMPT

        return tools_dict,assistant_tools,tool_response_prompt

    def _get_crowd_voting_assistant_response_and_check(self,dialogs):
        retry_cnt=0
        checker_flag=False
        dummy_dialogs=copy.deepcopy(dialogs)
        while (not checker_flag) and retry_cnt<=self.checker_max_retries:
            # assistant能看到checker的回复，但checker看不到它上一次的回复（能看到的话会一直重复原来的建议）
            if self.assistant.llm_type=='chat':
                assistant_messages,error_code=self.assistant._generate(dummy_dialogs,self.assistant_tools,self.assistant_n_response)
                if error_code!=200:
                    raise Exception('Assistant Error: '+str(assistant_messages['content']))
                # 众投
                votes = defaultdict(list)
                for message in assistant_messages:
                    if 'tool_calls' in message:
                        tool_calls = tuple([tool_call['function']['name'] for tool_call in message['tool_calls']])
                        votes[tool_calls].append(message)
                    else:
                        votes[tuple(['llm'])].append(message)

                # 找出投票最多的结果
                max_votes = max(len(messages) for messages in votes.values())  # 获取最大投票数
                most_voted_results = {key: messages for key, messages in votes.items() if len(messages) == max_votes}
                #最多投票的结果中随机选择一个消息,进行修正
                assistant_message = random.choice(random.choice(list(most_voted_results.values())))
                selected_reasoning = None
            
            else: # reasoing model
                assistant_messages,reasonings,error_code=self.assistant._generate(dummy_dialogs,self.assistant_tools,self.assistant_n_response)
                
                if error_code!=200 and 'Tool call decode error' in str(assistant_messages):
                    # 重试一次看看,reasoning model偶尔会解析不出来
                    dummy_dialogs.append({
                    "role":"user",
                    "content": "Tool call decode error. Please ensure the tool call is a properly structured JSON string."
                })
                    assistant_messages,reasonings,error_code=self.assistant._generate(dummy_dialogs,self.assistant_tools,self.assistant_n_response)
                    if error_code!=200:
                        raise Exception('Assistant Error: '+str(assistant_messages))
                    # raise Exception('Assistant Error: '+str(assistant_messages['content']))
                # 众投
                votes = defaultdict(list)
                for message, reasoning in zip(assistant_messages, reasonings):
                    if 'tool_calls' in message:
                        tool_calls = tuple(tool_call['function']['name'] for tool_call in message['tool_calls'])
                        votes[tool_calls].append((message, reasoning))
                    else:
                        votes[('llm',)].append((message, reasoning))

                # 找出投票最多的结果
                max_votes = max(len(pairs) for pairs in votes.values())
                most_voted_results = {key: pairs for key, pairs in votes.items() if len(pairs) == max_votes}

                # 随机选择其中一个（message, reasoning）对
                assistant_message, selected_reasoning = random.choice(random.choice(list(most_voted_results.values())))

            
            if self.checker_max_retries==0:
                return assistant_message, True, None, selected_reasoning

            if 'tool_calls' in assistant_message:
                checker_messages, status_code,checker_flag = self.checker._tool_call_check(assistant_message, dialogs, self.assistant_tools)
            else:
                # llm回复为最终结果,从最多投票的结果中随机选择一个消息，进行修正
                checker_messages, status_code,checker_flag = self.checker._llm_check(assistant_message, dialogs,self.assistant_tools)

            # #checker检查，给出pass为True or False
            # todo:放过checker,即使多次未通过，就选上一次的.
            if status_code==200:
                if not checker_flag:
                    dummy_dialogs.extend([assistant_message])
                    dummy_dialogs.extend(checker_messages)
                    retry_cnt+=1
                    # todo:放过checker,即使多次未通过，就选上一次的.
                    if retry_cnt > self.checker_max_retries:
                        return assistant_message, True, checker_messages, selected_reasoning
            else:
                logger.error(f'[{self.data["data_id"]}] Checker Error: '+str(checker_messages))
                raise Exception('Checker Error: '+str(checker_messages))
        return assistant_message,checker_flag,checker_messages, selected_reasoning

    def _generate(self,data,save=True,test_mode=False):
            checker_not_pass_index=[]
            task_complete_index=[]
            is_task_completable=[]
            task_mode_keys=[]
            assistant_reasonings={}

            current_task_turn=0

            # 使用实时时间！！！
            today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            SYSTEM_TEMPLET = {"current_time": today[:10]}
            system_message = {'role': 'system', 'content': SYSTEM_PROMPT.format(**SYSTEM_TEMPLET)+self.tool_response_prompt}
            dialogs=[system_message]

            #文件信息
            if self.provide_file_system_info=='all':
                logger.info(f'{Fore.MAGENTA}已提供文件系统信息。{Style.RESET_ALL}')
                dialogs+=self.file_system_info_list
            elif self.provide_file_system_info=='path':
                logger.info(f'{Fore.MAGENTA}已提供文件系统信息。{Style.RESET_ALL}')
                dialogs+=[self.file_system_info_list[0]]

            selected_tools=','.join([tool['name'] for tool in self.assistant_tools])
            logger.debug(f'{Fore.MAGENTA}SYSTEM:{Style.RESET_ALL} {Fore.WHITE}{system_message}{Style.RESET_ALL}')
            logger.info(f'{Fore.MAGENTA}TOOLS:{Style.RESET_ALL} {Fore.WHITE}{selected_tools}{Style.RESET_ALL}')
            logger.info(f'{Fore.MAGENTA}Mode Weights:{Style.RESET_ALL} {Fore.WHITE}{self.mode_weights}{Style.RESET_ALL}')
            logger.info(f'{Fore.MAGENTA}Task Turn Weights:{Style.RESET_ALL} {Fore.WHITE}{self.task_turn_weights}{Style.RESET_ALL}')

            self.max_task_turns = int(random.choices(list(self.task_turn_weights.keys()), 
                                                     weights=list(self.task_turn_weights.values()),
                                                     k=1)[0])
            logger.info(f'{Fore.MAGENTA}Max Task Turn:{Style.RESET_ALL} {Fore.WHITE}{self.max_task_turns}{Style.RESET_ALL}')
            while current_task_turn<self.max_task_turns: #业务数据最多生成一轮
                try:
                    if test_mode: # 输入模式
                        user_message=self.user._input()
                        if not user_message['content']:
                            break
                    else:
                        # 问题生成模式
                        # if dialogs[-1]['role']=='user':
                        #     user_message=dialogs[-1]
                        #     dialogs=dialogs[:-1]
                        # else:
                            user_message,error_code,mode_key=self.user._init_question(dialogs,self.user_tools,self.mode_weights)
                            if error_code!=200:
                                raise Exception('User Error: '+user_message['content'])
                    last_task_end_index=len(dialogs)-1
                    dialogs+=[user_message]
                    task_complete_flag=0
                    task_history=[user_message]
                    clarify_cnt=0
                    while task_complete_flag not in [1,-1]:
                        task_invalid_flag=0
                        dummy_dialogs=copy.deepcopy(dialogs)
                        assistant_message,checker_flag,checker_messages,assistant_reasoning=self._get_crowd_voting_assistant_response_and_check(dummy_dialogs)
                        dialogs+=[assistant_message]
                        assistant_reasonings[len(dialogs)-1]=assistant_reasoning
                        task_history+=[assistant_message]
                        if not checker_flag:
                            # checker连续修正n次后仍不通过，但继续生成（有可能是checker过于严谨或出现幻觉,保留不通过的数据方便后续检查）
                            checker_not_pass_index.append(len(dialogs)-1)
                            error_data={'error':f"Reach checker max retries",
                                                'assistant_message':assistant_message,
                                                'checker_message':checker_messages,
                                                'data_id':data['data_id'],
                                                'messages':dialogs,
                                                'tools':self.assistant_tools,}
                            # self._save(error_data,self.failed_save_path)
                        while 'tool_calls' in assistant_message:
                            tool_messages=self.tool._run(assistant_message)
                            # tool出错记录，但继续生成（保留部分tool出错的数据，锻炼模型的错误处理）
                            for tool_message in tool_messages:
                                error_message=tool_message['content']
                                if type(error_message) is dict and "status" in error_message and error_message['status']=='failed':
                                    error_data={'error':f"Tool error: {error_message}",
                                                'input_assistant_message':assistant_message,
                                                'file_system_info':self.file_system_info_list,
                                                'temp_file_system_path':self.temp_file_system_path,
                                                'data_id':data['data_id'],
                                                'messages':dialogs,
                                                'tools':self.assistant_tools,}
                                    logger.error(f'{Fore.RED}[{self.data["data_id"]}] TOOL ERROR:{Style.RESET_ALL} {Fore.WHITE}{error_message}{Style.RESET_ALL}')
                                    self._save(error_data,self.failed_save_path)
                                    tool_message['content']=str(tool_message['content'])
                            dialogs+=tool_messages
                            task_history+=tool_messages
                            dummy_dialogs=copy.deepcopy(dialogs)
                            assistant_message,checker_flag,checker_messages,assistant_reasoning=self._get_crowd_voting_assistant_response_and_check(dummy_dialogs)
                            dialogs+=[assistant_message]
                            assistant_reasonings[len(dialogs)-1]=assistant_reasoning
                            task_history+=[assistant_message]
                            if not checker_flag:
                                # checker连续修正n次后仍不通过，但继续生成（有可能是checker过于严谨或出现幻觉,保留不通过的数据方便后续检查）
                                checker_not_pass_index.append(len(dialogs)-1)
                                error_data={'error':f"Reach checker max retries",
                                            'assistant_message':assistant_message,
                                            'checker_message':checker_messages,
                                            'data_id':data['data_id'],
                                            'messages':dialogs,
                                            'tools':self.assistant_tools,
                                            }
                                # self._save(error_data,self.failed_save_path)
                        
                        # 仅输入当前任务下的对话历史
                        # logger.debug(f"_clarify beginning: task_history:{json.dumps(task_history,ensure_ascii=False)}")
                        # logger.debug(f"_clarify beginning: assistant_tools:{json.dumps(self.assistant_tools,ensure_ascii=False)}")
                        user_message,task_complete_flag,error_code=self.user._clarify(task_history,self.user_tools)
                        if error_code!=200:
                            raise Exception('User Error: '+user_message['content'])
                        else:
                            if task_complete_flag==0:
                                if clarify_cnt<2 and len(task_history)<=30: #最多澄清2次，如果还没完成，则该任务不加入对话历史
                                    task_history+=[user_message]
                                    dialogs+=[user_message]
                                    clarify_cnt+=1
                                else:
                                    dialogs=dialogs[:last_task_end_index+1]
                                    #移除澄清过程中的reasoning
                                    assistant_reasonings={k:v for k,v in assistant_reasonings.items() if k <= len(dialogs)-1}
                                    task_invalid_flag=1
                                    break
                                
                    # 记录每个任务结束的index，便于之后有需要时拆分
                    if not task_invalid_flag: #任务有效
                        task_mode_keys.append(mode_key) #记录任务模式
                        task_complete_index.append(len(dialogs)-1) #记录任务完成index
                        is_task_completable.append(task_complete_flag) #记录任务可完成性
                        if task_complete_flag==-1:
                            error_data={'error':f"Impossible task",
                                                'selected_files':self.selected_files,
                                                'user_message':user_message,
                                                'assistant_message':assistant_message,
                                                'data_id':data['data_id'],
                                                'messages':dialogs,
                                                'tools':self.assistant_tools,
                                                }
                            # self._save(error_data,self.failed_save_path)
                        current_task_turn+=1
                except Exception as e:
                    logger.error(f'{Fore.RED}[{self.data["data_id"]}] ERROR:{Style.RESET_ALL} {Fore.WHITE}{str(e)}{Style.RESET_ALL}')
                    logger.error(traceback.print_exc())
                    error_data={'error':str(e),
                                'traceback': traceback.format_exc(),
                                'data_id':data['data_id'],
                                'messages':dialogs,
                                'tools':self.assistant_tools,
                                'selected_files':self.selected_files,
                                'round_cnt':current_task_turn,
                                }
                    self._save(error_data,self.failed_save_path)
                    #清空临时的空间
                    if self.tool.file_system_path and os.path.exists(self.tool.file_system_path) and self.tool.file_system_path.startswith(self.executable_temp_working_dir):
                        subprocess.run(["sudo", "rm", "-rf", self.tool.file_system_path])
                        logger.info(f"file_system_path:{self.tool.file_system_path} deleted")
                    if self.tool.code_session:
                        self.tool.code_session._close()
                    return False
            data={
                    'data_id':data['data_id'],
                    'messages':dialogs,
                    'tools':self.assistant_tools,
                    'assistant_reasonings':assistant_reasonings,
                    'selected_files':self.selected_files,
                    'checker_not_pass_index':checker_not_pass_index,
                    'task_complete_index':task_complete_index,
                    'is_task_completable':is_task_completable,
                    'dialog_mode': task_mode_keys,
                    'round_cnt':current_task_turn
                    }
            # generated_data[data['data_id']]=1
            if save:
                with lock:
                    self._save(data,self.save_path)
            #清空临时的空间
            if self.tool.file_system_path and os.path.exists(self.tool.file_system_path) and self.tool.file_system_path.startswith(self.executable_temp_working_dir):
                subprocess.run(["sudo", "rm", "-rf", self.tool.file_system_path])
                logger.info(f"file_system_path:{self.tool.file_system_path} deleted")
            if self.tool.code_session:
                self.tool.code_session._close()
            return True
            
    def _save(self,generated_dialogs,save_path):
        with open(save_path,"a") as f_target:
            f_target.write(json.dumps(generated_dialogs,ensure_ascii=False)+"\n")

def generate_one(data=False,save=True,test_mode=True):
    if not data:
        data={'data_id':str(uuid.uuid4())}
    logger.info(args.tool_defines_path)
    #每次生成都是一个新的pipeline！不然checker_max_retries会重叠
    pipeline=Pipeline(max_task_turns=args.max_task_turns,
                    checker_max_retries=args.checker_max_retries,#checker重试次数
                    assistant_n_response=args.assistant_n_response,#众投次数
                    save_path=args.save_path,
                    failed_save_path=args.failed_save_path,
                    assistant_model_name=args.assistant_model_name,
                    checker_model_name=args.checker_model_name,
                    user_model_name=args.user_model_name,
                    tool_model_name=args.tool_model_name,
                    file_system_path=args.file_system_path,
                    lang=args.lang,
                    use_persona=args.use_persona,
                    tool_defines_path=ast.literal_eval(args.tool_defines_path),
                    task_turn_weights=json.loads(args.task_turn_weights),
                    mode_weights=json.loads(args.mode_weights),
                    dynamic_adjust_mode_and_task_turn_weight=args.dynamic_adjust_mode_and_task_turn_weight,
                    executable_temp_working_dir=args.executable_temp_working_dir,
                    fixed_tools=ast.literal_eval(args.fixed_tools),
                    tool_nums_distribution = json.loads(args.tool_nums_distribution),
                    files_num=json.loads(args.files_num),
                    provide_file_system_info=args.provide_file_system_info,
                    category_fixed_tools=json.loads(args.category_fixed_tools),
                    tool_output_limit=args.tool_output_limit,
                    )
    # # pipeline.tools=[file_system_functions.find_large_files]
    # pipeline.tools=[database_functions.select_from_tables,database_functions.get_database_info]
    return pipeline._generate(data=data,save=save,test_mode=test_mode)


if __name__ == '__main__':
    # 下载图片：./ads-cli cp s3://6E92C79723F44B088D7A5415021BA7E1:1E425F8A0E44401CB0C864A728B694F1@sensechat-badcase.aoss-external.cn-sh-01.sensecoreapi-oss.cn/image 你的路径/
    import argparse
    parser = argparse.ArgumentParser()
    project_dir=os.path.dirname(os.path.abspath(__file__))
    parser.add_argument('--save_path', default=f"{project_dir}/generated_data/generate_executable_python_tools2.jsonl", type=str)
    parser.add_argument('--failed_save_path', default=f"{project_dir}/generated_data/failed_generate_executable_python_tools2.jsonl", type=str)
    parser.add_argument('--executable_temp_working_dir', default=f"{os.environ['HOME_DIR']}/function_call_data_temp", type=str)
    parser.add_argument('--tool_defines_path',default=str([f"{project_dir}/tools/defines/file_system_functions"]),type=str)
    parser.add_argument('--num_workers', default=1, type=int)
    parser.add_argument('--max_task_turns', default=3, type=int)
    parser.add_argument('--checker_max_retries', default=1, type=int)
    parser.add_argument('--assistant_n_response', default=1, type=int)
    parser.add_argument('--assistant_model_name', default='qwq', type=str)
    parser.add_argument('--checker_model_name', default='qwq', type=str)
    parser.add_argument('--user_model_name', default='qwq', type=str)
    parser.add_argument('--tool_model_name', default='qwq', type=str)
    parser.add_argument('--file_system_path', default=f"{project_dir}/working_dir/file_system_new/", type=str)
    parser.add_argument('--lang', default='en', type=str)
    parser.add_argument('--use_persona', action='store_true', default=False,help='Enable persona for use agent')
    parser.add_argument('--target_generate_data_number', default=1, type=int)
    parser.add_argument('--task_turn_weights', type=str, default=json.dumps({1:0.5,2:0.2,3:0.2,4:0.1}))
    parser.add_argument('--mode_weights', default=json.dumps({"single":1, "parallel":1, "multiple":1, "dependent":1, "no_tool_use":1,"miss_param":1}), type=str)
    parser.add_argument('--dynamic_adjust_mode_and_task_turn_weight', action='store_true', default=False,
                        help=(
                            "Enable dynamic adjustment of mode weights and task turn weights based on the randomly selected tool count. "
                        )
                    )
    parser.add_argument('--fixed_tools', default='[]', type=str) #给了固定工具就不会采样了
    parser.add_argument('--tool_nums_distribution', default=json.dumps({9: 20, 8: 30, 7: 40, 6: 60, 5: 90, 4: 100, 3: 120, 2: 140, 1: 200}), type=str)
    parser.add_argument('--files_num', type=str, default=json.dumps({1:0,2:0.2,3:0.3,4:0.3,5:0.2}))
    parser.add_argument('--provide_file_system_info',  default='None', type=str, help='provide file and directory info for assistant, all or path or none')
    parser.add_argument('--category_fixed_tools',  default=json.dumps({
                'file_system_functions':['display_directory_tree','get_file_info'],
                'database_functions':['display_directory_tree','get_all_table_names','get_table_info','get_column_info','get_database_info']
                }), type=str, help='some tool category need fixed tools')
    parser.add_argument('--tool_output_limit', default=4096, type=int)
    args = parser.parse_args()

    from data_generate.utils.log_setting import set_main_logger
    file_name=os.path.splitext(os.path.basename(args.save_path))[0]
    logger = set_main_logger(log_path=f'{project_dir}/generated_data/executable_tools/error_log/{file_name}.log',console_level=logging.INFO, file_level=logging.WARNING)

    # #单线程
    # progress_bar = tqdm(total=len(user.data_list))
    # for sample in user._sample():
    #     result=generate_one(sample)
    #     progress_bar.update(1)
    #     if not result:
    #         failed_cnt+=1
    #         print(f"FAILED_CNT:{failed_cnt}/{len(user.data_list)}")

    #多线程
    # args.only_build_in_tools=True
    # progress_bar = tqdm(total=len(user.data_list))
    # with ThreadPoolExecutor(max_workers=args.num_workers) as executor:
    #     futures = [executor.submit(generate_one,sample) for sample in user._sample()]
    #     for future in concurrent.futures.as_completed(futures):
    #         try:
    #             result = future.result()
    #             progress_bar.update(1)
    #             if not result:
    #                 failed_cnt+=1
    #                 print(f"FAILED_CNT:{failed_cnt}/{len(user.data_list)}")
    #         except Exception as e:
    #             print(f"Error: {e}")  # 打印线程内部的异常

    #单个sample定位debug
    # command='/mnt/nvme0/qinxinyi/function_call_data/data_generate/sampled_data/统计该路径下的每个jsonl文件的行数，以及总行数'
    # command='/mnt/nvme0/qinxinyi/langfuse_report/report/image/统计该路径下不同修改日期的文件数量，以及总数量'
    # command='/mnt/nvme0/qinxinyi/langfuse_report/report/image/统计该路径下不同修改日期的文件数量，以及总数量，然后保存为一个txt文件到/mnt/nvme0/qinxinyi/function_call_data/data_generate/working_dir/目录下'
    # command='/mnt/nvme0/qinxinyi/function_call_data/data_generate/executable_functions/functions/file_system_functions/copy_file_or_directory.py先读取这个函数的内容，然后根据函数内容为它生成openai格式的json格式的函数定义并储存到这个路径下的一个json文件(文件名为函数名）中/mnt/nvme0/qinxinyi/function_call_data/data_generate/executable_functions/defines/file_system_functions'
    # command='/mnt/nvme0/qinxinyi/langfuse_report/report/image/判断该路径下是不是有7360b453.png这个文件'
    # command='列出当前数据库中chinook数据库的数据结构，包括每个表的名字、列名和数据量'
    # command='读取这个文件/mnt/nvme0/qinxinyi/function_call_data/data_generate/working_dir/file_count_by_date.txt并分析'
    # command='用自然语言简单描述sakila数据库的表结构'
    # command='chinook数据库里唱片最多的前三名艺术家是？'
    # command='合并/mnt/nvme0/qinxinyi/function_call_data/data_generate/working_dir/virtual_data路径下的所有excel文件，并保存到/mnt/nvme0/qinxinyi/function_call_data/data_generate/working_dir/virtual_data2下，文件名是total_data'
    
    # args.debug=True #打印信息
    # args.use_persona=True #使用不同人格生成问题
    # test_mode=False #False表示user_agent基于tools采样自动生成问题，True用于自定义问题
    # if os.path.exists(args.failed_save_path):
    #     with open(args.failed_save_path,'r',encoding='utf-8') as f:
    #         for line in tqdm(f.readlines()):
    #             data=json.loads(line,strict=False)
    #             generate_one(data=data,save=True,test_mode=test_mode)

    # for i in range(500):
    #     generate_one(save=True,test_mode=test_mode)

    #单线程test
    # args.provide_file_system_info='none'
    # # args.fixed_tools='["file_system_functions.code_intepreter"]'
    # generate_one(False,True,False)

    failed_cnt = 0
    progress_bar = tqdm(total=args.target_generate_data_number)
    with ThreadPoolExecutor(max_workers=args.num_workers) as executor:
        futures = [executor.submit(generate_one,False,True,False) for _ in range(args.target_generate_data_number)]
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                progress_bar.update(1)

                current = progress_bar.n
                total = progress_bar.total
                percent = (current / total) * 100
                logger.info(f"{Fore.GREEN}Progress:{Style.RESET_ALL} {current}/{total} ({percent:.1f}%)")

                if not result:
                    failed_cnt+=1
                    logger.info(f"FAILED_CNT:{failed_cnt}/{args.target_generate_data_number}")
            except Exception as e:
                logger.critical(f"Error: {e}")  # 打印线程内部的异常
                logger.critical(traceback.print_exc())

    # pipeline=Pipeline(max_task_turns=args.max_task_turns,
    #                 checker_max_retries=args.checker_max_retries,#checker重试次数
    #                 assistant_n_response=args.assistant_n_response,#众投次数
    #                 save_path=args.save_path,
    #                 failed_save_path=args.failed_save_path,
    #                 assistant_model_name=args.assistant_model_name,
    #                 checker_model_name=args.checker_model_name,
    #                 user_model_name=args.user_model_name,
    #                 tool_model_name=args.tool_model_name,
    #                 file_system_path=f'{os.environ["PROJECT_DIR"]}/working_dir/shangtang_file_system/excel_data/',
    #                 lang=args.lang,
    #                 use_persona=args.use_persona,
    #                 tool_defines_path=ast.literal_eval(args.tool_defines_path),
    #                 task_turn_weights=json.loads(args.task_turn_weights),
    #                 mode_weights=json.loads(args.mode_weights),
    #                 dynamic_adjust_mode_and_task_turn_weight=args.dynamic_adjust_mode_and_task_turn_weight,
    #                 executable_temp_working_dir=args.executable_temp_working_dir,
    #                 fixed_tools=ast.literal_eval(args.fixed_tools),
    #                 )
    # # print(pipeline._get_file_system_info())
    # # print(pipeline._get_file_system_info_list()[0])
    # print(len(pipeline._get_file_system_info_list()))