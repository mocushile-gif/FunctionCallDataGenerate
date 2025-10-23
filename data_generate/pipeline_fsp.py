# -*- coding: utf-8 -*-
import json
from datetime import datetime
import sys
import os
from pydantic import BaseModel, Field, SecretStr, model_validator
from typing import List, Dict, Any, Optional
import copy
from collections import defaultdict
import random
from tqdm import tqdm
from colorama import Fore, Style
import concurrent
import threading
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import uuid
import copy
import shutil
import tempfile
import ast
import traceback
import logging
from data_generate.agent.fsp_user_agent import UserAgent
from data_generate.agent.assistant_agent import AssistantAgent
from data_generate.agent.tool_agent import ToolAgent
from data_generate.agent.checker_agent import CheckerAgent
from data_generate.prompt import *
from data_generate.utils import *
from data_generate.utils.log_setting import set_main_logger
import subprocess
import tempfile
lock = threading.Lock()


class Pipeline(BaseModel):
    user: UserAgent = Field(default=None)
    assistant: AssistantAgent = Field(default=None)
    checker: CheckerAgent = Field(default=None)
    tool: ToolAgent = Field(default=None)
    assistant_tools: List = Field(default=None)
    user_tools: List = Field(default=None)
    tools_dict: List = Field(default=None)
    all_tools: List = Field(default=None)
    save_path: str = Field(default=None)
    failed_save_path: str = Field(default=None)
    checker_max_retries: int = 3
    assistant_n_response: int = 1
    assistant_model_name: str = 'gpt4o-ptu-client'
    checker_model_name: str = 'gpt4o-ptu-client'
    user_model_name: str = 'gpt4o-ptu-client'
    tool_model_name: str = 'gpt4o-ptu-client'
    use_persona: bool = False
    tool_response_prompt: str = False
    executable_temp_working_dir: str = None
    tool_defines_path: list = Field(default=None)
    only_virtual_rapidapi_response: bool = False
    file_system_path: str = ''
    temp_file_system_path: str = ''
    file_list: list = Field(default=None)
    provide_file_system_info: str = 'none'
    category_fixed_tools: dict = Field(default=None)
    tool_output_limit: int=4096
    data: Dict = Field(default=None)
    lang: str = 'en'

    class Config:
        arbitrary_types_allowed = True

    @model_validator(mode='after')
    def validate_environment(self):
        # 复制工作区
        project_dir = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))
        # Create temporary directories to store the copied versions
        self.file_list = list(set([file_name for selected_files in self.data['selected_files'] for file_name in selected_files if file_name]))
        tools = list(set([func for turn in self.data["enhanced_fsp"] for func in turn]))

        self.tools_dict, self.user_tools, self.assistant_tools, self.tool_response_prompt = self.init_tools(tools)
        if self.file_list:
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
                for file_name in self.file_list:
                    src_path = os.path.join(self.file_system_path, file_name)
                    dst_path = os.path.join(self.temp_file_system_path, file_name)
                    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                    shutil.copy2(src_path, dst_path)

            self.tool = ToolAgent(
                llm_name=self.tool_model_name,
                file_system_path=self.temp_file_system_path,
                only_virtual_rapidapi_response=self.only_virtual_rapidapi_response,
                tools=self.tools_dict,
                output_limit=self.tool_output_limit,
            )

            self.user = UserAgent(
                llm_name=self.user_model_name,
                use_persona=self.use_persona,
                file_system_path=self.temp_file_system_path,
                lang=self.lang,
            )
        else:
            self.tool = ToolAgent(
                llm_name=self.tool_model_name,
                only_virtual_rapidapi_response=self.only_virtual_rapidapi_response,
                tools=self.tools_dict,
                output_limit=self.tool_output_limit,
            )
            self.user=UserAgent(
                llm_name=self.user_model_name,
                use_persona=self.use_persona,
                lang=self.lang,
            )
        self.assistant = AssistantAgent(llm_name=self.assistant_model_name)
        self.checker = CheckerAgent(llm_name=self.checker_model_name)
        return self

    def init_tools(self, tools):
        if type(tools[0]) is dict:
            tools = [tool['name'] for tool in tools]
        self.all_tools = {}
        for tool_defines_path in self.tool_defines_path:
            self.all_tools.update(load_tool_defines(
                tool_defines_path, recursive=True))
        tool_response_prompt = TOOL_RESPONSE_PROMPT
        tools_dict = {tool_name: tool_define for tool_name,
                      tool_define in self.all_tools.items() if tool_define['name'] in tools}

        fixed_tool_pool=defaultdict(dict)
        for tool_key, tool_item in self.all_tools.items():
            tool_name = tool_key.split('.')[-1]
            tool_category = tool_key.split('.')[0]
            for category, fixed_tools in self.category_fixed_tools.items():
                if tool_name in fixed_tools and tool_category == category:
                    fixed_tool_pool[category][tool_key] = tool_item

        for category,fixed_tools in self.category_fixed_tools.items():
            # if any([category in tool for tool in tools_dict.keys()]):
            #     tools_dict.update(fixed_tool_pool[category])
            #     if category=='database_functions':
            #         tool_response_prompt+=SQL_TOOL_PROMPT
            #     else:
            #         tool_response_prompt+=FILE_TOOL_PROMPT
            if category=='database_functions':
                if any(['database' in file_name for file_name in self.file_list]):
                    tools_dict.update(fixed_tool_pool[category])
                    tool_response_prompt+=SQL_TOOL_PROMPT
            else:
                if any(['database' not in file_name for file_name in self.file_list]):
                    tools_dict.update(fixed_tool_pool[category])
                    tool_response_prompt+=FILE_TOOL_PROMPT

        assistant_tools = list(tools_dict.values())
        user_tools = {tool['name']:tool for tool in assistant_tools}
        self.all_tools = {tool['name']:tool for tool in self.all_tools.values()}
        return tools_dict, user_tools, assistant_tools, tool_response_prompt

    def _get_crowd_voting_assistant_response_and_check(self, dialogs):
        retry_cnt = 0
        checker_flag = False
        dummy_dialogs = copy.deepcopy(dialogs)
        while (not checker_flag) and retry_cnt <= self.checker_max_retries:
            # assistant能看到checker的回复，但checker看不到它上一次的回复（能看到的话会一直重复原来的建议）
            if self.assistant.llm_type == 'chat':
                assistant_messages, error_code = self.assistant._generate(
                    dummy_dialogs, self.assistant_tools, self.assistant_n_response)
                if error_code != 200:
                    raise Exception('Assistant Error: ' +
                                    str(assistant_messages))
                # 众投
                votes = defaultdict(list)
                for message in assistant_messages:
                    if 'tool_calls' in message:
                        tool_calls = tuple(
                            [tool_call['function']['name'] for tool_call in message['tool_calls']])
                        votes[tool_calls].append(message)
                    else:
                        votes[tuple(['llm'])].append(message)

                # 找出投票最多的结果
                max_votes = max(len(messages)
                                for messages in votes.values())  # 获取最大投票数
                most_voted_results = {
                    key: messages for key, messages in votes.items() if len(messages) == max_votes}
                # 最多投票的结果中随机选择一个消息,进行修正
                assistant_message = random.choice(
                    random.choice(list(most_voted_results.values())))
                selected_reasoning = None

            else:  # reasoing model
                assistant_messages, reasonings, error_code = self.assistant._generate(
                    dummy_dialogs, self.assistant_tools, self.assistant_n_response)

                if error_code != 200 and 'Tool call decode error' in str(assistant_messages):
                    # 重试一次看看,reasoning model偶尔会解析不出来
                    dummy_dialogs.append({
                        "role": "user",
                        "content": "Tool call decode error. Please ensure the tool call is a properly structured JSON string."
                    })
                    assistant_messages, reasonings, error_code = self.assistant._generate(
                        dummy_dialogs, self.assistant_tools, self.assistant_n_response)
                    if error_code != 200:
                        raise Exception('Assistant Error: ' +
                                        str(assistant_messages))
                    # raise Exception('Assistant Error: '+str(assistant_messages['content']))
                # 众投
                votes = defaultdict(list)
                for message, reasoning in zip(assistant_messages, reasonings):
                    if 'tool_calls' in message:
                        tool_calls = tuple(
                            tool_call['function']['name'] for tool_call in message['tool_calls'])
                        votes[tool_calls].append((message, reasoning))
                    else:
                        votes[('llm',)].append((message, reasoning))

                # 找出投票最多的结果
                max_votes = max(len(pairs) for pairs in votes.values())
                most_voted_results = {
                    key: pairs for key, pairs in votes.items() if len(pairs) == max_votes}

                # 随机选择其中一个（message, reasoning）对
                assistant_message, selected_reasoning = random.choice(
                    random.choice(list(most_voted_results.values())))

            if self.checker_max_retries == 0:
                return assistant_message, True, None, selected_reasoning

            if 'tool_calls' in assistant_message:
                checker_messages, status_code, checker_flag = self.checker._tool_call_check(
                    assistant_message, dialogs, self.assistant_tools)
            else:
                # llm回复为最终结果,从最多投票的结果中随机选择一个消息，进行修正
                checker_messages, status_code, checker_flag = self.checker._llm_check(
                    assistant_message, dialogs, self.assistant_tools)

            # #checker检查，给出pass为True or False
            # todo:放过checker,即使多次未通过，就选上一次的.
            if status_code == 200:
                if not checker_flag:
                    dummy_dialogs.extend([assistant_message])
                    dummy_dialogs.extend(checker_messages)
                    retry_cnt += 1
                    # todo:放过checker,即使多次未通过，就选上一次的.
                    if retry_cnt > self.checker_max_retries:
                        return assistant_message, True, checker_messages, selected_reasoning
            else:
                logger.error(f'[{self.data["data_id"]}] Checker Error: '+str(checker_messages))
                raise Exception('Checker Error: '+str(checker_messages))
        return assistant_message, checker_flag, checker_messages, selected_reasoning
        
    def get_tool_info_for_specific_turn(self,fsp,n):
        func_list=fsp["enhanced_fsp"][n]
        if func_list[0]=='__miss func__':
            return self.user_tools
        else:
            func_define_list={}
            for func in func_list:
                if func=='__miss params__' and self.file_list:
                    if any(['database' in file_name for file_name in self.file_list]):
                      for tool in self.category_fixed_tools['database_functions']:
                        func_define_list[tool]=self.all_tools[tool]
                    if any(['database' not in file_name for file_name in self.file_list]):
                      for tool in self.category_fixed_tools['file_system_functions']:
                        func_define_list[tool]=self.all_tools[tool]
                    continue
                elif func=='__miss params__':
                    continue
                assert func in self.user_tools
                func_define_list[func]=self.user_tools[func]
            return func_define_list

    def _save(self, generated_dialogs, save_path):
        with open(save_path, "a") as f_target:
            f_target.write(json.dumps(
                generated_dialogs, ensure_ascii=False)+"\n")
                       
    def _generate(self, save=True):
        checker_not_pass_index = []
        task_complete_index = []
        is_task_completable = []
        tasks={}
        assistant_reasonings = {}
        current_task_turn = 0
        # 可执行工具使用实时时间！！！
        today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        SYSTEM_TEMPLET = {"current_time": today[:10]}
        system_message = {'role': 'system', 'content': SYSTEM_PROMPT.format(
            **SYSTEM_TEMPLET)+self.tool_response_prompt}
        dialogs = [system_message]

        # 文件信息
        if self.provide_file_system_info == 'all':
            logger.info(f'{Fore.MAGENTA}已提供文件系统信息。')
            dialogs += self.file_system_info_list
        elif self.provide_file_system_info == 'path':
            logger.info(f'{Fore.MAGENTA}已提供文件系统信息。')
            dialogs += [self.file_system_info_list[0]]

        selected_tools = ','.join([tool['name']
                                    for tool in self.assistant_tools])
        logger.debug(
            f'{Fore.MAGENTA}SYSTEM:{Style.RESET_ALL} {Fore.WHITE}{system_message}{Style.RESET_ALL}')
        logger.info(
            f'{Fore.MAGENTA}TOOLS:{Style.RESET_ALL} {Fore.WHITE}{selected_tools}{Style.RESET_ALL}')

        for n,fsp_current_turn in enumerate(self.data['enhanced_fsp']):
            logger.info(
            f'\n\n{Fore.YELLOW}-----TURN {n}-----{Style.RESET_ALL}\n')

            current_tools=self.get_tool_info_for_specific_turn(self.data,n)
            mode=self.data["fsp_mode"][n]
            user_message, error_code = self.user._init_question(dialogs,current_tools,self.user_tools,fsp_current_turn,mode)
            if error_code!=200:
                raise Exception('User Error: '+user_message['content'])
            tasks[n]=user_message
            last_task_end_index = len(dialogs)-1
            dialogs += [user_message]
            task_complete_flag = 0
            task_history = [user_message]
            clarify_cnt = 0
            try:
                while task_complete_flag not in [1, -1]:
                    task_invalid_flag = 0
                    dummy_dialogs = copy.deepcopy(dialogs)
                    assistant_message, checker_flag, checker_messages, assistant_reasoning = self._get_crowd_voting_assistant_response_and_check(
                        dummy_dialogs)
                    dialogs += [assistant_message]
                    assistant_reasonings[len(dialogs)-1] = assistant_reasoning
                    task_history += [assistant_message]
                    if not checker_flag:
                        # checker连续修正n次后仍不通过，但继续生成（有可能是checker过于严谨或出现幻觉,保留不通过的数据方便后续检查）
                        checker_not_pass_index.append(len(dialogs)-1)
                        error_data = {'error': f"Reach checker max retries",
                                      'assistant_message': assistant_message,
                                      'checker_message': checker_messages,
                                      'data_id': self.data['data_id'],
                                      'messages': dialogs,
                                      'tools': self.assistant_tools,
                                      }
                        # self._save(error_data, self.failed_save_path)
                    while 'tool_calls' in assistant_message:
                        tool_messages = self.tool._run(assistant_message)
                        # tool出错记录，但继续生成（保留部分tool出错的数据，锻炼模型的错误处理）
                        for tool_message in tool_messages:
                            error_message = tool_message['content']
                            if type(error_message) is dict and "status" in error_message and error_message['status'] == 'failed':
                                error_data = {'error': f"Tool error: {error_message}",
                                              'input_assistant_message': assistant_message,
                                              'data_id': self.data['data_id'],
                                              'messages': dialogs,
                                              'tools': self.assistant_tools,
                                              }
                                logger.error(
                                    f'{Fore.RED}[{self.data["data_id"]}] TOOL ERROR:{Style.RESET_ALL} {Fore.WHITE}{error_message}{Style.RESET_ALL}')
                                self._save(error_data, self.failed_save_path)
                                tool_message['content'] = str(
                                    tool_message['content'])
                        dialogs += tool_messages
                        task_history += tool_messages
                        dummy_dialogs = copy.deepcopy(dialogs)
                        assistant_message, checker_flag, checker_messages, assistant_reasoning = self._get_crowd_voting_assistant_response_and_check(
                            dummy_dialogs)
                        dialogs += [assistant_message]
                        assistant_reasonings[len(
                            dialogs)-1] = assistant_reasoning
                        task_history += [assistant_message]
                        if not checker_flag:
                            # checker连续修正n次后仍不通过，但继续生成（有可能是checker过于严谨或出现幻觉,保留不通过的数据方便后续检查）
                            checker_not_pass_index.append(len(dialogs)-1)
                            error_data = {'error': f"Reach checker max retries",
                                          'assistant_message': assistant_message,
                                          'checker_message': checker_messages,
                                          'data_id': self.data['data_id'],
                                          'messages': dialogs,
                                          'tools': self.assistant_tools,
                                          }
                            # self._save(error_data, self.failed_save_path)

                    if len(task_history) > 50:
                        task_complete_flag = -1
                        break
                        
                    # 仅输入当前任务下的对话历史
                    logger.debug(
                        f"_clarify beginning: task_history:{json.dumps(task_history,ensure_ascii=False)}")
                    logger.debug(
                        f"_clarify beginning: assistant_tools:{json.dumps(self.assistant_tools,ensure_ascii=False)}")
                    user_message, task_complete_flag, error_code = self.user._clarify(
                        task_history, self.tools_dict, mode)
                    if error_code != 200:
                        raise Exception('User Error: '+user_message['content'])
                    else:
                        if task_complete_flag == 0:
                            if clarify_cnt < 2:  # 最多澄清两次，如果还没完成，则为不可完成的任务
                                task_history += [user_message]
                                dialogs += [user_message]
                                clarify_cnt += 1
                            else:
                                task_complete_flag = -1
                                break

                # 记录每个任务结束的index，便于之后有需要时拆分
                task_complete_index.append(len(dialogs)-1)  # 记录任务完成index
                is_task_completable.append(task_complete_flag)  # 记录任务可完成性
                current_task_turn += 1
            except Exception as e:
                logger.error(
                    f'{Fore.RED}[{self.data["data_id"]}] ERROR:{Style.RESET_ALL} {Fore.WHITE}{str(e)}{Style.RESET_ALL}')
                logger.error(traceback.print_exc())
                error_data = {'error': str(e),
                              'data_id': self.data['data_id'],
                              'messages': dialogs,
                              'tools': self.assistant_tools,
                              'round_cnt': current_task_turn
                              }
                self._save(error_data, self.failed_save_path)

                if self.tool.file_system_path and os.path.exists(self.tool.file_system_path) and self.tool.file_system_path.startswith(self.executable_temp_working_dir):
                    subprocess.run(["sudo", "rm", "-rf", self.tool.file_system_path])
                    logger.info(f"file_system_path:{self.tool.file_system_path} deleted")
                if self.tool.code_session:
                    self.tool.code_session._close()
                return False,self.data['data_id']

        last_index=1
        task_trajectorys={}
        for i,complete_index in enumerate(task_complete_index):
            task_trajectory=[]
            task_messages=dialogs[last_index:complete_index+1]
            last_index=complete_index+1
            for message in task_messages:
                if 'tool_calls' in message:
                    tool_calls=[{"name":tool_call['function']['name'],"arguments":tool_call['function']['arguments']} for tool_call in message['tool_calls']]
                    task_trajectory.append(tool_calls)
            task_trajectorys[i]=task_trajectory

        final_data = {
            'data_id': self.data.get('data_id', str(uuid.uuid4())),
            'messages': dialogs,
            'tools': self.assistant_tools,
            'assistant_reasonings': assistant_reasonings,
            "tasks": tasks,
            "task_trajectorys": task_trajectorys,
            'fsp': self.data.get('enhanced_fsp', None),
            'dialog_mode': self.data.get('fsp_mode', None),
            'selected_files': list(set([file_name for selected_files in self.data['selected_files'] for file_name in selected_files if file_name])),
            'task_complete_index': task_complete_index,
            'is_task_completable': is_task_completable,
            'round_cnt': current_task_turn
        }
        if save:
            with lock:
                self._save(final_data, self.save_path)
        # 清空临时的空间
        if self.tool.file_system_path and os.path.exists(self.tool.file_system_path) and self.tool.file_system_path.startswith(self.executable_temp_working_dir):
            subprocess.run(["sudo", "rm", "-rf", self.temp_file_system_path])
            logger.info(f"file_system_path:{self.tool.file_system_path} deleted")
        if self.tool.code_session:
            self.tool.code_session._close()
        return True,self.data['data_id']


def generate_one(data, save=True):
    # 每次生成都是一个新的pipeline！不然checker_max_retries会重叠
    pipeline = Pipeline(
        checker_max_retries=args.checker_max_retries,  # checker重试次数
        assistant_n_response=args.assistant_n_response,  # 众投次数
        save_path=args.save_path,
        failed_save_path=args.failed_save_path,
        assistant_model_name=args.assistant_model_name,
        checker_model_name=args.checker_model_name,
        user_model_name=args.user_model_name,
        tool_model_name=args.tool_model_name,
        file_system_path=args.file_system_path,
        use_persona=args.use_persona,
        tool_defines_path=ast.literal_eval(args.tool_defines_path),
        executable_temp_working_dir=args.executable_temp_working_dir,
        only_virtual_rapidapi_response=args.only_virtual_rapidapi_response,
        provide_file_system_info=args.provide_file_system_info,
        category_fixed_tools=json.loads(args.category_fixed_tools),
        tool_output_limit=args.tool_output_limit,
        lang=args.lang,
        data=data,
    )
    return pipeline._generate(save=save)

def init_logger_from_args(args, project_dir, console_level=logging.INFO, file_level=logging.ERROR):
    # 根据 save_path 生成日志文件名
    file_name = os.path.splitext(os.path.basename(args.save_path))[0]
    log_dir = os.path.join(project_dir, "generated_data", "executable_tools", "error_log")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"{file_name}.log")
    logger = set_main_logger(
        log_path=log_file,
        console_level=console_level,
        file_level=file_level
    )
    return logger

if __name__ == '__main__':
    # 下载图片：./ads-cli cp s3://6E92C79723F44B088D7A5415021BA7E1:1E425F8A0E44401CB0C864A728B694F1@sensechat-badcase.aoss-external.cn-sh-01.sensecoreapi-oss.cn/image 你的路径/
    import argparse
    parser = argparse.ArgumentParser()
    project_dir = os.path.dirname(os.path.abspath(__file__))
    parser.add_argument('--original_data_path',
                        default=f"{project_dir}/generated_data/executable_tools/generated/generate_executable_mix_all_self_tools_hard.jsonl", type=str)
    parser.add_argument(
        '--save_path', default=f"{project_dir}/generated_data/executable_tools/generated/generate_executable_file_system_task_gpt_test.jsonl", type=str)
    parser.add_argument(
        '--failed_save_path', default=f"{project_dir}/generated_data/executable_tools/failed/failed_generate_executable_mix_all_self_tools2.jsonl", type=str)
    parser.add_argument('--executable_temp_working_dir',
                        default=f"{os.environ['HOME_DIR']}/function_call_data_temp", type=str)
    parser.add_argument('--tool_defines_path',
                        default=str([f"{project_dir}/tools/defines"]), type=str)
    parser.add_argument('--num_workers', default=1, type=int)
    parser.add_argument('--checker_max_retries', default=0, type=int)
    parser.add_argument('--assistant_n_response', default=1, type=int)
    parser.add_argument('--assistant_model_name', default='qwq', type=str)
    parser.add_argument('--checker_model_name', default='qwq', type=str)
    parser.add_argument('--user_model_name', default='qwq', type=str)
    parser.add_argument('--tool_model_name', default='qwq', type=str)
    parser.add_argument('--use_persona', action='store_true',
                        default=False, help='Enable persona for use agent')
    parser.add_argument('--lang', default='en', type=str)
    parser.add_argument('--only_virtual_rapidapi_response', action='store_true',
                        default=False, help='only use virtual rapidapi response')
    parser.add_argument(
        '--file_system_path', default=f"{project_dir}/working_dir/file_system_new", type=str)
    parser.add_argument('--provide_file_system_info',  default='None', type=str,
                        help='provide file and directory info for assistant, all or path or none')
    parser.add_argument('--category_fixed_tools',  default=json.dumps({
                'file_system_functions':['display_directory_tree','get_file_info','read_file_contents'],
                'database_functions':['display_directory_tree','get_all_table_names','get_table_info','get_column_info','get_database_info']
                }), type=str, help='some tool category need fixed tools')
    parser.add_argument('--tool_output_limit', default=4096, type=int)
    args = parser.parse_args()

    logger = init_logger_from_args(args, project_dir)

    # one-try
    # null = None
    # false = False
    # args.save_path=f"{project_dir}/generated_data/executable_tools/generated/fsp/test.jsonl"
    # args.file_system_path=f"{project_dir}/working_dir/file_system_new"
    # data = {
    #     "data_id": "2ecb1985-af74-4722-87c6-502fbac370bd",
    #     "enhanced_fsp": [
    #         ["__miss func__"],
    #         ["flatten_list", "extract_patterns_from_text", "delete_from_table"]
    #     ],
    #     "fsp_mode": ["miss_func", "multiple_or_dependent"],
    #     "selected_files": [
    #         [
    #             null
    #         ],
    #         ["txt_data/birth_rate_and_life_expectancy_2010.txt", "database/Pagila.sqlite"],
    #     ]
    # }
    # generate_one(data, True)

    # # fsp生成pipeline
    existing_data_id=[]
    if os.path.exists(args.save_path):
        with open(args.save_path,'r',encoding='utf-8') as f:
            for line in f.readlines():
                data=json.loads(line)
                existing_data_id.append(data['data_id'])

    remaining_data=[]
    with open(args.original_data_path,'r',encoding='utf-8') as f:
        all_data=json.load(f)
        for data in all_data:
            if data['data_id'] not in existing_data_id:
                remaining_data.append(data)

    failed_cnt = 0
    progress_bar = tqdm(total=len(remaining_data)+len(existing_data_id))
    progress_bar.update(len(existing_data_id))
    with ThreadPoolExecutor(max_workers=args.num_workers) as executor:
        futures = [executor.submit(generate_one,data,True) for data in remaining_data]
        for future in concurrent.futures.as_completed(futures):
            try:
                result,data_id = future.result()
                progress_bar.update(1)
                current = progress_bar.n
                total = progress_bar.total
                percent = (current / total) * 100
                logger.info(f"{Fore.GREEN}Progress:{Style.RESET_ALL} {current}/{total} ({percent:.1f}%)")

                if not result:
                    failed_cnt+=1
                    logger.info(f"{Fore.RED}FAILED:{data_id}{Style.RESET_ALL}")
                    logger.info(f"FAILED_CNT:{failed_cnt}/{total}")
            except Exception as e:
                logger.critical(f"Error: {e}")  # 打印线程内部的异常
                logger.critical(traceback.print_exc())