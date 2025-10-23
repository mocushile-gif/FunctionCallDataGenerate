# 数据任务分类（modification/lookup/no-function-call):
# 对于每条数据:
# 1. 初始化工具、构建临时文件系统
# 2. 拆分每轮任务调用序列
# 3. 根据是否调用 modification 工具判断任务初分类
# 4. 执行 modification 工具后再次快照，若无文件变动则改为 lookup
# 5. 写入分类结果和变更详情

import json
import re
import os
import json
from collections import defaultdict
import random
import threading
import tempfile
from data_generate.utils.log_setting import set_main_logger
import logging
import copy
import shutil
from colorama import Fore, Style
import subprocess
import concurrent
import traceback
from tqdm import tqdm
import re
from concurrent.futures import ThreadPoolExecutor
from data_generate.agent.model.gpt import ChatGPTFunction
from data_generate.agent.model.qwq import QwQFunction
from fsp_generate.code.label_task.extract_lookup_task_answer_prompt import extract_lookup_task_answer_prompt
lock = threading.Lock()

def normalize_text(text: str) -> str:
    if not isinstance(text, str):
        text = json.dumps(text, ensure_ascii=False)
    else:
        try:
            text = json.dumps(json.loads(text), ensure_ascii=False)
        except:
            pass
    try:
        decoded = bytes(text, 'utf-8').decode('unicode_escape')
        # 将解码后的文本重新编码为utf-8来确保中文字符正确
        text = decoded.encode('latin-1').decode('utf-8')
    except:
        pass
    text = re.sub(r'\\n', ' ', text)
    text = re.sub(r'\\t', ' ', text)
    text = re.sub(r'\\+', '', text)
    text = re.sub(r'[^\w\s]', '', text)
    text = ' '.join(text.split()).lower()
    return text

def mask_to_regex(answer: str) -> str:
    # 1. 保留 ___MASK___ 临时占位符
    placeholder = "___MASK___".lower()
    # 2. 标准化：去掉符号，转小写
    answer = normalize_text(answer)
    # 3. 将占位符替换为正则通配符
    pattern = re.escape(answer).replace(re.escape(placeholder), r".+?")
    return pattern

def match_answer(answer, task_messages):
    normalized_task_messages = ','.join([normalize_text(message) for message in task_messages])

    if '___MASK___' in answer:
        pattern = mask_to_regex(answer)
        # 使用 re.IGNORECASE 进行忽略大小写匹配
        if not re.search(pattern, normalized_task_messages, flags=re.IGNORECASE):
            return False
    else:
        normalized_answer = normalize_text(answer)
        if normalized_answer not in normalized_task_messages:
            return False

    return True

def mask_dates(text):
    patterns = [
        # Sat Jul 19 22:56:26 2025
        r'\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}\s+\d{4}',

        # 2025-07-21 / 2025/07/21
        r'\b\d{4}[-/]\d{2}[-/]\d{2}\b',

        # Jul 22 16:41
        r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}\s+\d{2}:\d{2}\b',

        # 2025-07-18T14:17:12
        r'\b\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\b',

        # Thu, 31 Jul 2025 11:32:08 GMT
        r'\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun),\s+\d{2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\s+\d{2}:\d{2}:\d{2}\s+GMT\b'
    ]

    for pattern in patterns:
        text = re.sub(pattern, '___MASK___', str(text))
        # print(text)

    return text

def mask_mode_and_user(text):
    # 正则模式：适配文本中敏感信息
    regex_patterns = [
        r'\b100[0-7]{3}\b'
        r'\b[0-7]{3}\b',  # 匹配777、755、750等权限码
        r'-[r-][w-][x-][r-][w-][x-][r-][w-][x-]',  # -rwxr-xr-x 等
        r'\b[r-][w-][x-]\b',
        r'"permissions":\s*"[^"]*",\s*"owner":\s*"[^"]*",\s*"group":\s*"[^"]*"',
        r'\bqinxinyi\b',
        r'10-\d{3}-\d{3}-\d{2}',  # 形如 10-119-178-74 的主机名
        '5.4.0-169-generic',
        'x86_64',
        r'#\d+-Ubuntu SMP.*UTC \d{4}',  # Ubuntu 内核版本行
    ]

    for pattern in regex_patterns:
        text = re.sub(pattern, '___MASK___', str(text), flags=re.IGNORECASE | re.DOTALL)
        # print(text)

    return text

def detect_mask_data(data):
    # 数据掩码处理函数：替换答案中的文件名（模型生成的）和日期为掩码
    # 获取原始查询任务答案详情
    lookup_details = data.get('lookup_task_answer_details', {})
    selected_set = set(data.get("selected_files", []))
    mask_files = []

    # 遍历文件系统变更记录，收集需要掩码处理的文件路径
    for task_idx, changes in data.get("file_system_change_details", {}).items():
        for change_type, file_list in changes.items():
            # 筛选出模型生成的文件名
            mask_files.extend(
                file for file in file_list if file not in selected_set
            )

    masked_lookup_details = {}

    # 对每个任务的答案进行掩码处理
    for task_id, values in lookup_details.items():
        new_values = []
        for val in values:
            masked_val = val
            for file in mask_files:
                if file in masked_val:
                    # print(f"Original: {masked_val}")
                    suffix = os.path.splitext(file)[1]  # 获取文件后缀，如 .png
                    # 构造可替换模式：可能带 ./、.\\、路径等
                    escaped_file = re.escape(file)
                    file_pattern = rf"(?:\.\/|\.\\|[\w\/\\]*?)?{escaped_file}"
                    # 替换文件路径为掩码+后缀格式
                    masked_val = re.sub(file_pattern, f"___MASK___{suffix}", masked_val)
            
            # 日期时间掩码处理
            masked_val = mask_dates(masked_val)
            masked_val = mask_mode_and_user(masked_val)
            new_values.append(masked_val)
            if masked_val!=val:
                print(f"{val} -- > {masked_val}")  # 调试输出掩码后的结果
            
        masked_lookup_details[task_id] = new_values
    data['lookup_task_answer_details']=masked_lookup_details
    return data


def check_one_data(data):
    data=detect_mask_data(data)
    check_flag=True
    lookup_task_answer_details={}
    last_index=1
    for i,task_end_index in enumerate(data["task_complete_index"]):
        # print(data['data_id'],i)
        task_category=data["task_categories"][f'{i}']
        task_messages=data['messages'][last_index:task_end_index] #不包含总结部分
        task=task_messages[0]['content']
        last_index=task_end_index+1
        if 'lookup' not in task_category or data["is_task_completable"][i]==-1:
            continue

        answers=data["lookup_task_answer_details"][f'{i}']
        task_messages_for_check = [
            message['content'] if 'tool_calls' not in message else message['tool_calls']
            for message in task_messages 
            if not (message['role']=='assistant' and 'tool_calls' not in message)
        ]
        try:
            if answers:
                not_match_answers=[]
                for answer in answers:
                    flag=match_answer(answer, task_messages_for_check)
                    if not flag:
                        not_match_answers.append(answer)
                if not_match_answers:
                    check_flag=False
                    raise ValueError(f"not matched: {not_match_answers}")
            else:
                check_flag=False
                raise ValueError("No answers extracted.")
        except Exception as e:
            check_data={
                "data_id":data["data_id"],
                "task_id":i,
                "task":task,
                "conversation":task_messages_for_check,
                "Answer":answers,
                "check": str(e)}
            print(f'please recheck this data: {data["data_id"]}')
            logger.info(f"Task: {task}\nAnswer: {answers}")
            with open(extract_answer_need_check,'a',encoding='utf-8') as f:
                f.write(json.dumps(check_data,indent=4,ensure_ascii=False)+'\n')
            data["lookup_task_answer_details"][f'{i}']=False
    
    return check_flag,data

def extract_one_data(data):
    try:
        data['answer_need_check']=[]
        lookup_task_answer_details=data.get("lookup_task_answer_details",{})
        last_index=1
        for i,task_end_index in enumerate(data["task_complete_index"]):
            task_category=data["task_categories"][f'{i}']
            task_messages=data['messages'][last_index:task_end_index+1] #不包含总结部分
            task=task_messages[0]['content']
            last_index=task_end_index+1
            if 'lookup' not in task_category or data["is_task_completable"][i]==-1:
                continue
            if lookup_task_answer_details.get(f'{i}',None):
                continue
            # 去掉单纯回复的assistant信息
            task_messages=[message for message in task_messages if not (message['role']=='assistant' and 'tool_calls' not in message)]
            answers = []

            task_messages_for_check = [
                message['content'] if 'tool_calls' not in message else message['tool_calls']
                for message in task_messages 
                if not (message['role']=='assistant' and 'tool_calls' not in message)
            ]
            try:
                retry_history = []
                response_content = None
                
                for retry_count in range(3):
                    try:
                        # 提取答案
                        prompt_parameter = {
                            "task": task,
                            "task_messages": task_messages,
                        }
                        prompt = extract_lookup_task_answer_prompt.format(**prompt_parameter)
                        retry_history_str="\n".join(retry_history)
                        if retry_history:
                            prompt+= f'''**The extracted answers are not correct:**
                                        {retry_history_str}

                                        Please retry.
                                        '''
                        messages = [{"role": "user", "content": prompt}]
                        response, status_code = llm.chat(messages)
                        
                        if status_code != 200:
                            raise Exception(f'API错误代码 {status_code}: {response}')
                            
                        response_content = response['content']
                        
                        # 解析JSON响应
                        json_str = None
                        if '```json' in response_content:
                            matches = re.findall(r'```json(.*?)```', response_content, re.DOTALL)
                            json_str = matches[0].strip() if matches else None
                        else:
                            json_str = response_content.strip()
                            
                        if not json_str:
                            raise ValueError(f"Invalid JSON content: {response_content}")
                        try:
                            response_data = json.loads(json_str)
                        except:
                            raise ValueError(f"Invalid JSON content: {response_content}")
                        answers = response_data.get("shortest_necessary_answer_string", [])
                        
                        if not answers:
                            raise ValueError(f"Missing 'shortest_necessary_answer_string' field: {response_content}")
                            
                        # 验证答案匹配

                        not_match_answers=[]
                        for answer in answers:
                            flag=match_answer(answer, task_messages_for_check)
                            if not flag:
                                not_match_answers.append(answer)
                        if not_match_answers:
                            raise ValueError(f"The extracted answer not in the conversation history: {not_match_answers}")
                            
                        break  # 全部验证通过则退出循环
                        
                    except Exception as e:
                        error_msg = f"第{retry_count+1}次尝试失败: {str(e)}"
                        logger.critical(f"{error_msg}")
                        retry_history.append(error_msg)
                        if retry_count < 2:
                            continue
                        raise  # 最后一次失败直接抛出
                        
            except Exception as e:
                logger.critical(f"最终验证失败: {str(e)}")
                # 记录详细错误信息到检查文件...
                logger.info(f"Task: {task}\nAnswer: {answers}")
                check_data={
                    "data_id":data["data_id"],
                    "task_id":i,
                    "task":task,
                    "conversation":task_messages_for_check,
                    "Answer":answers,
                    "check": str(e)}
                print(f'please recheck this data: {data["data_id"]}')
                with open(extract_answer_need_check,'a',encoding='utf-8') as f:
                    f.write(json.dumps(check_data,indent=4,ensure_ascii=False)+'\n')
                data['answer_need_check'].append(i)
            lookup_task_answer_details[i]=answers
        data['lookup_task_answer_details']=lookup_task_answer_details
        data=detect_mask_data(data)
        if not data['answer_need_check']:
            del data['answer_need_check']
        return data
    except Exception as e:
        print(str(e))
        traceback.print_exc()
        return data

if __name__ == "__main__":
    import data_generate, fsp_generate
    project_dir = os.path.dirname(data_generate.__file__)
    fsp_dir = os.path.dirname(fsp_generate.__file__)

    label_data_path=f'{fsp_dir}/data/generate_fsp_all_self_gpt_labeled_extracted_o.jsonl'
    extract_answer_data_path=f'{fsp_dir}/data/generate_fsp_all_self_gpt_labeled_extracted.jsonl'
    extract_answer_need_check=f'{fsp_dir}/data/extracted_answers_o.json'

    label_data_path=f'{fsp_dir}/data/generate_fsp_all_self_gpt_labeled_500_0718.jsonl'
    label_data_path=f'{fsp_dir}/data/generate_fsp_all_self_gpt_labeled_600.jsonl'
    # label_data_path=f'{fsp_dir}/data/test.jsonl'
    label_data_path='/mnt/afs2/qinxinyi/function_call_data/mongodb/fsp_600.jsonl'

    extract_answer_data_path=f'{fsp_dir}/data/generate_fsp_all_self_gpt_labeled_extracted_500_0718.jsonl'
    extract_answer_data_path=f'{fsp_dir}/data/generate_fsp_all_self_gpt_labeled_extracted_600.jsonl'
    # extract_answer_data_path=f'{fsp_dir}/data/test_extracted.jsonl'
    extract_answer_data_path='/mnt/afs2/qinxinyi/function_call_data/mongodb/fsp_600.jsonl'

    extract_answer_need_check=f'{fsp_dir}/data/extracted_answers_need_check_500_0718.json'
    extract_answer_need_check=f'{fsp_dir}/data/extracted_answers_need_check_600.json'
    # extract_answer_need_check=f'{fsp_dir}/data/test_check.json'
    logger = set_main_logger(log_path=f'{os.path.dirname(os.path.abspath(__file__))}/error_log.log',console_level=logging.INFO, file_level=logging.WARNING)
    with open(extract_answer_need_check,'w',encoding='utf-8') as f:
        pass

    llm = ChatGPTFunction(name='gpt4o-ptu-client')
    # llm = QwQFunction()

    existing_data=[]
    existing_data_id=[]
    if os.path.exists(extract_answer_data_path):
        with open(extract_answer_data_path,'r',encoding='utf-8') as f:
            for i,line in enumerate(f.readlines()):
                if line:
                    data=json.loads(line)
                    existing_data.append(data)
                    existing_data_id.append(data['data_id'])

    remaining_data=[]
    complete_data=[]
    for data in existing_data:
        check_result,data=check_one_data(data)
        if not check_result:
            remaining_data.append(data)
        else:
            complete_data.append(data)
    print(f'Existing Data: {len(existing_data)}')
    print(f'Complete Extracting Data: {len(complete_data)}')
    print(f'Extracted Data with error: {len(remaining_data)}')

    with open(label_data_path,'r',encoding='utf-8') as f:
        for line in f.readlines():
            data=json.loads(line)
            if data['data_id'] not in existing_data_id:
                remaining_data.append(data)

    print(f'Remaining data to extract: {len(remaining_data)}')

    with open(extract_answer_data_path,'w',encoding='utf-8') as out_f:
        for data in complete_data:
            out_f.write(json.dumps(data, ensure_ascii=False)+"\n")
    
    remaining_data=remaining_data
    failed_cnt = 0
    progress_bar = tqdm(total=len(remaining_data)+len(complete_data))
    progress_bar.update(len(complete_data))
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(extract_one_data,data) for data in remaining_data]
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
                    logger.info(f"FAILED_CNT:{failed_cnt}/{total}")
                else:
                    with open(extract_answer_data_path,'a',encoding='utf-8') as out_f:
                        out_f.write(json.dumps(result, ensure_ascii=False)+"\n")
            except Exception as e:
                logger.critical(f"Error: {e}")  # 打印线程内部的异常
                logger.critical(traceback.print_exc())