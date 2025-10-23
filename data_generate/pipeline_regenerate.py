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
from data_generate.agent.user_agent import UserAgent
from data_generate.agent.assistant_agent import AssistantAgent
from data_generate.agent.tool_agent import ToolAgent
from data_generate.agent.checker_agent import CheckerAgent
from data_generate.prompt import *
from data_generate.utils import *
lock = threading.Lock()


class Pipeline(BaseModel):
    user: UserAgent = Field(default=None)
    assistant: AssistantAgent = Field(default=None)
    checker: CheckerAgent = Field(default=None)
    tool: ToolAgent = Field(default=None)
    assistant_tools: List = Field(default=None)
    tools_dict: List = Field(default=None)
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
    tool_defines_path: list = Field(default=None),
    only_virtual_rapidapi_response: bool = False
    file_system_path: str = ''
    file_system_info_list: list = Field(default=None)
    provide_file_system_info: str = 'none'
    data: Dict = Field(default=None)

    class Config:
        arbitrary_types_allowed = True

    @model_validator(mode='after')
    def validate_environment(self):
        # 复制工作区
        project_dir = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))
        if not self.file_system_path:
            self.file_system_path = f'{project_dir}/working_dir/shangtang_file_system'
        # Create temporary directories to store the copied versions
        thread_id = threading.get_ident()
        thread_id_file_system_path = f"{self.executable_temp_working_dir}/function_call_file_system_var_{thread_id}"
        # 确保路径存在
        os.makedirs(thread_id_file_system_path, exist_ok=True)
        # Creates a temporary directory for the file_system copy
        temp_file_system_path = tempfile.mkdtemp(
            dir=thread_id_file_system_path)
        logger.info(f"temp_file_system_path:{temp_file_system_path}")
        # todo:多线程中临时文件夹冲突问题
        with lock:
            if os.path.exists(temp_file_system_path):
                shutil.rmtree(temp_file_system_path)
            shutil.copytree(self.file_system_path, temp_file_system_path)
            file_system = FileSystem()
            self.file_system_info_list = file_system.get_file_system_info_list(
                temp_file_system_path)

        self.tools_dict, self.assistant_tools, self.tool_response_prompt = self.init_tools(self.data['tools'])
        self.tool = ToolAgent(
            llm_name=self.tool_model_name,
            file_system_path=temp_file_system_path,
            only_virtual_rapidapi_response=self.only_virtual_rapidapi_response,
            tools=self.tools_dict
        )

        self.user = UserAgent(
            llm_name=self.user_model_name,
            use_persona=self.use_persona,
            file_system_path=temp_file_system_path,
            file_system_info_list=self.file_system_info_list
        )
        self.assistant = AssistantAgent(llm_name=self.assistant_model_name)
        self.checker = CheckerAgent(llm_name=self.checker_model_name)
        return self

    def init_tools(self, tools):
        if type(tools[0]) is dict:
            tools = [tool['name'] for tool in tools]
        all_tools = {}
        for tool_defines_path in self.tool_defines_path:
            all_tools.update(load_tool_defines(
                tool_defines_path, recursive=True))
        tool_response_prompt = TOOL_RESPONSE_PROMPT
        tool_response_prompt += FIXED_TOOL_PROMPT
        # 对于开集工具，可能有tool_response示例
        original_tools = [tool for tool in all_tools.values()
                          if tool['name'] in tools]
        unique_tools = {}
        for tool in original_tools:
            unique_tools[tool['name']+tool['description']] = tool
        original_tools = list(unique_tools.values())

        tools_dict = {tool_name: tool_define for tool_name,
                      tool_define in all_tools.items() if tool_define['name'] in tools}
        assert len(tools) == len(original_tools)
        return tools_dict, original_tools, tool_response_prompt

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
                logger.error(f'[{data["data_id"]}] Checker Error: '+str(checker_messages))
                raise Exception('Checker Error: '+str(checker_messages))
        return assistant_message, checker_flag, checker_messages, selected_reasoning

    def _regenerate(self, save=True):
        checker_not_pass_index = []
        task_complete_index = []
        is_task_completable = []
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

        for task in self.data['task_messages']:
            user_message = {'role': 'user', 'content': task}
            logger.info(f'{Fore.CYAN}USER QUESTION:{Style.RESET_ALL} {Fore.WHITE}{user_message}{Style.RESET_ALL}')
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
                        self._save(error_data, self.failed_save_path)
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
                                    f'{Fore.RED}[{data["data_id"]}] TOOL ERROR:{Style.RESET_ALL} {Fore.WHITE}{error_message}{Style.RESET_ALL}')
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
                            self._save(error_data, self.failed_save_path)

                    # 仅输入当前任务下的对话历史
                    logger.debug(
                        f"_clarify beginning: task_history:{json.dumps(task_history,ensure_ascii=False)}")
                    logger.debug(
                        f"_clarify beginning: assistant_tools:{json.dumps(self.assistant_tools,ensure_ascii=False)}")
                    user_message, task_complete_flag, error_code = self.user._clarify(
                        task_history, self.tools_dict)
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
                    f'{Fore.RED}[{data["data_id"]}] ERROR:{Style.RESET_ALL} {Fore.WHITE}{str(e)}{Style.RESET_ALL}')
                logger.error(traceback.print_exc())
                error_data = {'error': str(e),
                              'data_id': self.data['data_id'],
                              'messages': dialogs,
                              'tools': self.assistant_tools,
                              'round_cnt': current_task_turn
                              }
                self._save(error_data, self.failed_save_path)

                if self.tool.code_session:
                    self.tool.code_session._close()
                return False
        final_data = {
            'data_id': self.data.get('data_id', str(uuid.uuid4())),
            'messages': dialogs,
            'tools': self.assistant_tools,
            'assistant_reasonings': assistant_reasonings,
            'checker_not_pass_index': checker_not_pass_index,
            'task_complete_index': task_complete_index,
            'is_task_completable': is_task_completable,
            'dialog_mode': self.data.get('dialog_mode', None),
            'round_cnt': current_task_turn
        }
        if save:
            with lock:
                self._save(final_data, self.save_path)
        # 清空临时的空间
        if os.path.exists(self.tool.file_system_path):
            shutil.rmtree(self.tool.file_system_path)
            logger.info(f"file_system_path:{self.tool.file_system_path} deleted")

        if self.tool.code_session:
            self.tool.code_session._close()
        return True

    def _save(self, generated_dialogs, save_path):
        with open(save_path, "a") as f_target:
            f_target.write(json.dumps(
                generated_dialogs, ensure_ascii=False)+"\n")


def regenerate_one(data, save=True):
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
        data=data
    )
    return pipeline._regenerate(save=save)


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
    parser.add_argument('--assistant_model_name', default='gpt', type=str)
    parser.add_argument('--checker_model_name', default='gpt', type=str)
    parser.add_argument('--user_model_name', default='gpt', type=str)
    parser.add_argument('--tool_model_name', default='gpt', type=str)
    parser.add_argument('--use_persona', action='store_true',
                        default=False, help='Enable persona for use agent')
    parser.add_argument('--only_virtual_rapidapi_response', action='store_true',
                        default=False, help='only use virtual rapidapi response')
    parser.add_argument('--fsp_generate', action='store_true',
                        default=False, help='generate for fsp data')

    parser.add_argument(
        '--file_system_path', default=f"{project_dir}/working_dir/file_system_new", type=str)
    parser.add_argument('--provide_file_system_info',  default='None', type=str,
                        help='provide file and directory info for assistant, all or path or none')
    args = parser.parse_args()

    from data_generate.utils.log_setting import set_main_logger
    file_name=os.path.splitext(os.path.basename(args.save_path))[0]
    logger = set_main_logger(log_path=f'{project_dir}/generated_data/executable_tools/error_log/{file_name}.log',console_level=logging.INFO, file_level=logging.WARNING)
    
    # 基于我们自己的多轮数据再生成（提供任务message和需要的tools）
    null = None
    false = False
    args.save_path=f"{project_dir}/generated_data/executable_tools/generated/v4/generate_executable_all_self_multimode_gpt.jsonl"
    args.file_system_path=f"{project_dir}/working_dir/file_system_self_define"
    args.provide_file_system_info = 'none'
    data = {"data_id": "ea6104c6-c043-4b2b-9da7-0e4df17721c3",
            "task_messages": [
                "Get random 1 dog images and 1 cat images, download the images and save to the image_data directory. Read the images to check their correctness. Then, get the corresponding json data of the images and save them to the json_data directory."
            ],
            "tools": [
                "download_image",
                "get_random_cat_images_info",
                "get_random_dog_images_info",
                "get_cat_image_info_by_id",
                "get_dog_image_info_by_id",
                "get_file_info",
                "display_directory_tree",
                "read_file_contents"
            ],
            "dialog_mode": [
                "dependent"
            ]
            }
    regenerate_one(data, True)

    # # 基于fsp生成！
    # if args.fsp_generate:
    #     existing_data_id=[]
    #     if os.path.exists(args.save_path):
    #         with open(args.save_path,'r',encoding='utf-8') as f:
    #             for line in f.readlines():
    #                 data=json.loads(line)
    #                 existing_data_id.append(data['data_id'])

    #     all_tools={}
    #     for tool_defines_path in ast.literal_eval(args.tool_defines_path):
    #         all_tools.update(load_tool_defines(tool_defines_path,recursive=True))

    #     remaining_data=[]
    #     with open(args.original_data_path,'r',encoding='utf-8') as f:
    #         file_name=args.original_data_path.split('/')[-1]
    #         data=json.load(f)
    #         for item in data:
    #             fsp_phi = item["fsp_phi"]
    #             task_messages= item["rewritten_turns"]
    #             data_id = file_name+'_'+str(item["fsp_id"])

    #             # 匹配tool_define,防重名
    #             prefixes = ['xlam_rapidapi_tools.', 'file_system_functions.', 'python_functions.', 'database_functions.']
    #             tools = list(set(item for sublist in fsp_phi for item in sublist))
    #             selected_tools = []
    #             for tool in tools:
    #                 for prefix in prefixes:
    #                     key = prefix + tool
    #                     if key in all_tools:
    #                         selected_tools.append(all_tools[key])
    #                         break  # 找到就不继续了
    #             if len(selected_tools)!=len(tools):
    #                 print(f'幻觉工具：{[tool for tool in tools if tool not in [tool["name"] for tool in selected_tools]]}')
    #                 continue #不要这条数据了
    #             assert len(selected_tools)==len(tools)

    #             data = {
    #                 "data_id":data_id,
    #                 "task_messages":list(task_messages.values()),
    #                 "tools":selected_tools
    #             }

    #             if data['data_id'] not in existing_data_id:
    #                 remaining_data.append(data)

    # # # 基于已生成的数据再生成！
    # else:
    #     existing_data_id=[]
    #     if os.path.exists(args.save_path):
    #         with open(args.save_path,'r',encoding='utf-8') as f:
    #             for line in f.readlines():
    #                 data=json.loads(line)
    #                 existing_data_id.append(data['data_id'])

    #     remaining_data=[]
    #     with open(args.original_data_path,'r',encoding='utf-8') as f:
    #         for line in f.readlines():
    #             data=json.loads(line)
    #             if data['data_id'] not in existing_data_id:
    #                 remaining_data.append({'data_id':data['data_id'],
    #                         'task_messages':[data['messages'][1]['content']],
    #                         'tools':data['tools'],
    #                         'dialog_mode':data['dialog_mode']})

    # failed_cnt = 0
    # progress_bar = tqdm(total=len(remaining_data)+len(existing_data_id))
    # progress_bar.update(len(existing_data_id))
    # with ThreadPoolExecutor(max_workers=args.num_workers) as executor:
    #     futures = [executor.submit(regenerate_one,data,True) for data in remaining_data]
    #     for future in concurrent.futures.as_completed(futures):
    #         try:
    #             result = future.result()
    #             progress_bar.update(1)
    #             if not result:
    #                 failed_cnt+=1
    #                 print(f"FAILED_CNT:{failed_cnt}/{len(remaining_data)}")
    #         except Exception as e:
    #             print(f"Error: {e}")  # 打印线程内部的异常
