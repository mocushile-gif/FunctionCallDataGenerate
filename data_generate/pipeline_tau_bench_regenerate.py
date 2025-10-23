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
from data_generate.agent.tau_bench_tool_agent import ToolAgent
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
    user_tools: List = Field(default=None)
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
    file_system_path: str = ''
    temp_file_system_path: str = ''

    class Config:
        arbitrary_types_allowed = True

    @model_validator(mode='after')
    def validate_environment(self):
        # Create temporary directories to store the copied versions
        thread_id = threading.get_ident()
        thread_id_file_system_path = f"{self.executable_temp_working_dir}/tau_bench_file_system_var_{thread_id}"
        # 确保路径存在
        os.makedirs(thread_id_file_system_path, exist_ok=True)
        self.temp_file_system_path = tempfile.mkdtemp(dir=thread_id_file_system_path)  # Creates a temporary directory for the file_system copy
        logger.info(f"temp_file_system_path: {self.temp_file_system_path}")
        with lock:
            if os.path.exists(self.temp_file_system_path):
                shutil.rmtree(self.temp_file_system_path)
            shutil.copytree(self.file_system_path, self.temp_file_system_path,copy_function=shutil.copy2)  # copy2保留文件属性

        self.user_tools,self.assistant_tools,self.tool_response_prompt=self.init_tools()
        self.tool = ToolAgent(
            llm_name=self.tool_model_name,
            file_system_path=self.temp_file_system_path,
            tools=self.user_tools
        )

        self.user=UserAgent(
            llm_name=self.user_model_name,
            use_persona=self.use_persona,
            file_system_path=self.temp_file_system_path
        )
        self.assistant=AssistantAgent(llm_name=self.assistant_model_name)
        self.checker=CheckerAgent(llm_name=self.checker_model_name)
        return self

    def init_tools(self):
        tools_pool={}
        for tool_defines_path in self.tool_defines_path:
            tools=load_tool_defines(tool_defines_path,recursive=True)
            tools_pool.update(tools)

        tau_bench_retail_dirname='tau_bench_retail'
        tau_bench_airline_dirname='tau_bench_airline'
        # tool_response_prompt=TOOL_RESPONSE_PROMPT
        tool_response_prompt=''

        if any([tau_bench_retail_dirname in tool for tool in tools_pool.keys()]):
            tool_response_prompt+=TAU_BENCH_RETAIL_TOOL_PROMPT
        if any([tau_bench_airline_dirname in tool for tool in tools_pool.keys()]):
            tool_response_prompt+=TAU_BENCH_AIRLINE_TOOL_PROMPT
        assistant_tools = list(tools_pool.values())
        return tools_pool,assistant_tools,tool_response_prompt

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

    def _regenerate(self, data, save=True):
        checker_not_pass_index = []
        task_complete_index = []
        is_task_completable = []
        assistant_reasonings = {}
        current_task_turn = 0
        # 可执行工具使用实时时间！！！
        system_message = {'role': 'system', 'content': self.tool_response_prompt}
        dialogs = [system_message]

        selected_tools = ','.join([tool['name']
                                      for tool in self.assistant_tools])
        logger.debug(
                f'{Fore.MAGENTA}SYSTEM:{Style.RESET_ALL} {Fore.WHITE}{system_message}{Style.RESET_ALL}')
        logger.info(
                f'{Fore.MAGENTA}TOOLS:{Style.RESET_ALL} {Fore.WHITE}{selected_tools}{Style.RESET_ALL}')

        for task in data['task_messages']:
            user_message = {'role': 'user', 'content': task}
            logger.info(
                    f'{Fore.CYAN}USER QUESTION:{Style.RESET_ALL} {Fore.WHITE}{user_message}{Style.RESET_ALL}')
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
                                      'data_id': data['data_id'],
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
                                              'data_id': data['data_id'],
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
                                          'data_id': data['data_id'],
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
                        task_history, self.user_tools)
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
                              'data_id': data['data_id'],
                              'messages': dialogs,
                              'tools': self.assistant_tools,
                              'round_cnt': current_task_turn
                              }
                self._save(error_data, self.failed_save_path)
                return False
        data = {
            'data_id': data.get('data_id', str(uuid.uuid4())),
            'messages': dialogs,
            'tools': self.assistant_tools,
            'assistant_reasonings': assistant_reasonings,
            'checker_not_pass_index': checker_not_pass_index,
            'task_complete_index': task_complete_index,
            'is_task_completable': is_task_completable,
            'dialog_mode': data.get('dialog_mode', None),
            'round_cnt': current_task_turn
        }
        if save:
            with lock:
                self._save(data, self.save_path)
        # 清空临时的空间
        if os.path.exists(self.tool.file_system_path):
            shutil.rmtree(self.tool.file_system_path)
            logger.info(f"file_system_path:{self.tool.file_system_path} deleted")
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
    )
    return pipeline._regenerate(data=data, save=save)


if __name__ == '__main__':
    # 下载图片：./ads-cli cp s3://6E92C79723F44B088D7A5415021BA7E1:1E425F8A0E44401CB0C864A728B694F1@sensechat-badcase.aoss-external.cn-sh-01.sensecoreapi-oss.cn/image 你的路径/
    import argparse
    parser = argparse.ArgumentParser()
    project_dir = os.path.dirname(os.path.abspath(__file__))
    parser.add_argument('--original_data_path',
                        default=f"{project_dir}/generated_data/executable_tools/generated/generate_executable_mix_all_self_tools_hard.jsonl", type=str)
    parser.add_argument('--save_path', default=f"{project_dir}/generated_data/executable_tools/generated/generate_tau_bench.jsonl", type=str)
    parser.add_argument('--failed_save_path', default=f"{project_dir}/generated_data/executable_tools/generated/failed_generate_tau_bench.jsonl", type=str)
    # parser.add_argument('--tool_defines_path',default=str([f"{project_dir}/tools/defines/tau_bench/tau_bench_retail",f"{project_dir}/tools/defines/tau_bench/tau_bench_airline"]),type=str)
    parser.add_argument('--tool_defines_path',default=str([f"{project_dir}/tools/defines/tau_bench/tau_bench_retail"]),type=str)
    parser.add_argument('--executable_temp_working_dir', default=f"/afs_b/qinxinyi/tau_bench_data_temp", type=str)
    parser.add_argument('--num_workers', default=1, type=int)
    parser.add_argument('--checker_max_retries', default=0, type=int)
    parser.add_argument('--assistant_n_response', default=1, type=int)
    parser.add_argument('--assistant_model_name', default='qwq', type=str)
    parser.add_argument('--checker_model_name', default='qwq', type=str)
    parser.add_argument('--user_model_name', default='qwq', type=str)
    parser.add_argument('--tool_model_name', default='qwq', type=str)
    parser.add_argument('--use_persona', action='store_true',
                        default=False, help='Enable persona for use agent')
    parser.add_argument('--file_system_path', default=f"{project_dir}/working_dir/tau_bench", type=str)
    args = parser.parse_args()

    from data_generate.utils.log_setting import set_main_logger
    file_name=os.path.splitext(os.path.basename(args.save_path))[0]
    logger = set_main_logger(log_path=f'{project_dir}/generated_data/executable_tools/error_log/{file_name}.log',console_level=logging.INFO, file_level=logging.WARNING)

    # 我们之前自己的多轮数据 test
    task={
        "user_id": "sofia_hernandez_5364",
        "actions": [],
        "instruction": "You are Sofia Hernandez, and you live in Seattle, WA, 98193. You want to cancel the grill, but if the agent asks you to confirm, you regret and want to keep it. You then want to ask which two t-shirts you have ordered in another order, and what materials are they. Make everything sound very natural and make up reasons.",
        "outputs": [
          "polyester",
          "cotton"
        ]
      }
    data = {'data_id': "eae104c6-c043-4b2b-9da7-0e4df17721c3",
            "task_messages": [
                "You are Sofia Hernandez, and you live in Seattle, WA, 98193. You want to cancel the grill, but if the agent asks you to confirm, you regret and want to keep it. You then want to ask which two t-shirts you have ordered in another order, and what materials are they. Make everything sound very natural and make up reasons.",
            ],
            "dialog_mode": [
                "tau_bench"
            ],
            }
    regenerate_one(data, True)

    task={
        "annotator": 0,
        "user_id": "mia_li_3668",
        "instruction": "Your user id is mia_li_3668. You want to fly from New York to Seattle on May 20 (one way). You do not want to fly before 11am est. You want to fly in economy. You prefer direct flights but one stopover also fine. If there are multiple options, you prefer the one with the lowest price. You have 3 baggages. You do not want insurance. You want to use your two certificates to pay. If only one certificate can be used, you prefer using the larger one, and pay the rest with your 7447 card. You are reactive to the agent and will not say anything that is not asked. Your birthday is in your user profile so you do not prefer to provide it.",
        "actions": [
            {
                "name": "book_reservation",
                "arguments": {
                    "user_id": "mia_li_3668",
                    "origin": "JFK",
                    "destination": "SEA",
                    "flight_type": "one_way",
                    "cabin": "economy",
                    "flights": [
                        {
                            "flight_number": "HAT136",
                            "date": "2024-05-20",
                        },
                        {
                            "flight_number": "HAT039",
                            "date": "2024-05-20",
                        },
                    ],
                    "passengers": [
                        {"first_name": "Mia", "last_name": "Li", "dob": "1990-04-05"}
                    ],
                    "payment_methods": [
                        {"payment_id": "certificate_7504069", "amount": 250},
                        {"payment_id": "credit_card_4421486", "amount": 5},
                    ],
                    "total_baggages": 3,
                    "nonfree_baggages": 0,
                    "insurance": "no",
                },
            },
        ],
    }
    data = {'data_id': "eae104c6-c043-4b2b-9da7-0e4df17721c3",
            "task_messages": [
                "Your user id is mia_li_3668. You want to fly from New York to Seattle on May 20 (one way). You do not want to fly before 11am est. You want to fly in economy. You prefer direct flights but one stopover also fine. If there are multiple options, you prefer the one with the lowest price. You have 3 baggages. You do not want insurance. You want to use your two certificates to pay. If only one certificate can be used, you prefer using the larger one, and pay the rest with your 7447 card. You are reactive to the agent and will not say anything that is not asked. Your birthday is in your user profile so you do not prefer to provide it.",
            ],
            "dialog_mode": [
                "tau_bench"
            ],
            }
    regenerate_one(data, True)
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
