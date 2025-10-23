import json
import re
import os
import json
from collections import defaultdict
import random
import threading
import tempfile
from data_generate.agent.tool_agent import ToolAgent
from data_generate.utils import load_tool_defines
from data_generate.utils.log_setting import set_main_logger
import logging
import copy
import shutil
from colorama import Fore, Style
import subprocess
import concurrent
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
import traceback
import os
import hashlib
lock = threading.Lock()

def compute_reward(task_trajectory: list, fsp: list, full_score: float = 1.0) -> float:
    """
    计算任务轨迹的 reward 得分。
    - 完全匹配：1.0
    - 只多不少：fsp_len / task_len
    - 缺失内容：0.0
    """
    fsp_counter = Counter(fsp)
    traj_counter = Counter(task_trajectory)

    for func, count in fsp_counter.items():
        if traj_counter[func] < count:
            return 0.0  # 缺失必须函数或次数不足

    if traj_counter == fsp_counter:
        return full_score  # 完全一致

    # 多了一些函数，但 fsp 函数已覆盖 → 得分衰减
    return round(len(fsp) / len(task_trajectory), 4)

def init_tools(tools,tool_defines_path):
    if type(tools[0]) is dict:
        tools = [tool['name'] for tool in tools]
    all_tools = {}
    for tool_defines_path in tool_defines_path:
        all_tools.update(load_tool_defines(
            tool_defines_path, recursive=True))
    tools_dict = {tool_name: tool_define for tool_name,
                    tool_define in all_tools.items() if tool_define['name'] in tools}
    return tools_dict

def create_temp_file_system(file_list,file_system_path,temp_file_system_dir):
    thread_id = threading.get_ident()
    thread_id_file_system_path = f"{temp_file_system_dir}/function_call_file_system_var_{thread_id}"
    # 确保路径存在
    os.makedirs(thread_id_file_system_path, exist_ok=True)
    # Creates a temporary directory for the file_system copy
    temp_file_system_path = tempfile.mkdtemp(
        dir=thread_id_file_system_path)
    logger.info(f"temp_file_system_path:{temp_file_system_path}")

    with lock:
        if os.path.exists(temp_file_system_path):
            shutil.rmtree(temp_file_system_path)
        for file_name in file_list:
            src_path = os.path.join(file_system_path, file_name)
            dst_path = os.path.join(temp_file_system_path, file_name)
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            shutil.copy2(src_path, dst_path)
    return temp_file_system_path

def execute_modification_task(modification_task_trajectory,temp_file_system,tool_agent):
    assistant_message={'role':'assistant','tool_calls':[{'function':tool_call,'type':'function','id':i} for i,tool_call in enumerate(modification_task_trajectory)]}
    logger.info(f'{Fore.YELLOW}ASSISTANT:{Style.RESET_ALL} {Fore.WHITE}{assistant_message}{Style.RESET_ALL}')
    tool_messages = tool_agent._run(assistant_message)
    # tool出错记录，但继续生成（保留部分tool出错的数据，锻炼模型的错误处理）
    for tool_message in tool_messages:
        error_message = tool_message['content']
        if type(error_message) is dict and "status" in error_message and error_message['status'] == 'failed':
            logger.error(f'{Fore.RED}[{data["data_id"]}] TOOL ERROR:{Style.RESET_ALL} {Fore.WHITE}{error_message}{Style.RESET_ALL}')

def snapshot_directory(dir_path):
    snapshot = {}
    for root, _, files in os.walk(dir_path):
        for fname in files:
            fpath = os.path.join(root, fname)
            try:
                stat = os.stat(fpath)
                # 文件大小和修改时间作为基本指标
                snapshot[fpath] = {
                    "size": stat.st_size,
                    "mtime": stat.st_mtime
                }
            except FileNotFoundError:
                continue  # 文件可能在统计过程中被删除
    return snapshot

def compare_snapshots(before, after, file_system_path):
    added = []
    removed = []
    modified = []

    before_keys = set(before.keys())
    after_keys = set(after.keys())

    added = list(after_keys - before_keys)
    removed = list(before_keys - after_keys)

    for path in before_keys & after_keys:
        if before[path] != after[path]:
            modified.append(path)

    if added or removed or modified:
        change_details = {}
        if added:
            change_details['added'] = [os.path.relpath(p, file_system_path) for p in added]
        if removed:
            change_details['removed'] = [os.path.relpath(p, file_system_path) for p in removed]
        if modified:
            change_details['modified'] = [os.path.relpath(p, file_system_path) for p in modified]
        return True, change_details

    return False, {}

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

def check_answer_for_one_data(task_messages,lookup_task_answers):
    task_messages_for_check = [
        message['content'] if 'tool_calls' not in message else message['tool_calls']
        for message in task_messages 
        if not (message['role']=='assistant' and 'tool_calls' not in message)
    ]
    not_match_answers=[]
    for answer in lookup_task_answers:
        flag=match_answer(answer, task_messages_for_check)
        if not flag:
            not_match_answers.append(answer)
    if not_match_answers:
        return 0,not_match_answers
    return 1,[]

def get_reward_for_one_task(task_messages,task_category,gt_task_trajectory,gt_fsp,gt_lookup_task_answers,gt_file_system_change_detail,temp_file_system_path,file_system_snapshot_before,tool_agent):
        reward=1
        reasons=[]
        task_trajectory=[]
        for message in task_messages:
            if 'tool_calls' in message:
                for tool_call in message['tool_calls']:
                    if tool_call['function']['name'] in gt_fsp:
                        task_trajectory.append({"name":tool_call['function']['name'],"arguments":tool_call['function']['arguments']})
        
        if task_category =='no-function-call':
            reward=0 if task_trajectory else reward
            if reward==0:
                reasons.append(f'{"reason":"call tools in no-function-call task","GT":gt_task_trajectory,"Actual":task_trajectory}')
        if 'modification' in task_category:
            execute_modification_task(task_trajectory,temp_file_system_path,tool_agent)
            file_system_snapshot_after=snapshot_directory(temp_file_system_path)
            change_flag,change_details=compare_snapshots(file_system_snapshot_before, file_system_snapshot_after,temp_file_system_path)
            for mode in ['added','removed','modified']:
                if len(change_details.get(mode,[]))!=len(gt_file_system_change_detail.get(mode,[])):
                    reward=0
            if reward==0:
                reasons.append(f'Files changes not match:\nGT: {gt_file_system_change_detail}\nActual: {change_details}')
        if 'lookup' in task_category:
            reward,not_match_answers=check_answer_for_one_data(task_messages,gt_lookup_task_answers)
            reasons.append(f'Answers not match:{not_match_answers}')
            # trajectory_reward=compute_reward(task_trajectory, fsp)
            # if trajectory_reward==0:
            #     print(f'gpt_trajectory: {task_trajectory}')
            #     print(f'fsp_trajectory: {fsp}')
            #     print(trajectory_reward)
                # 可以设置模型与gpt和与fsp都匹配，取最高分
        logger.info(f'{Fore.BLUE}Task Category:{task_category}{Style.RESET_ALL}')
        if reward==1:
            logger.info(f'{Fore.YELLOW}Reward:{reward}{Style.RESET_ALL}')
        else:
            logger.info(f'{Fore.YELLOW}Reward:{reward}{Style.RESET_ALL}')
            logger.info(f'{Fore.YELLOW}Reason:{reasons}{Style.RESET_ALL}')
        return reward

def get_reward(data,task_index,label_task_messages):
    if "reward_details" in data and len(data["reward_details"])==data['round_cnt']:
        return data
    tools_dict=init_tools(data['tools'],tool_defines_path)
    # 初始化文件系统需要在所有任务前！
    temp_file_system_path=create_temp_file_system(data['selected_files'],file_system_path,temp_file_system_dir)
    file_system_snapshot_before=snapshot_directory(temp_file_system_path)
    tool_agent = ToolAgent(
            llm_name='gpt',
            file_system_path=temp_file_system_path,
            tools=tools_dict,
            output_limit=4096,
        )
    # 检查任务类型
    check_flag=True
    reward_details={}
    last_index=1
    try:
        for i,task_end_index in enumerate(data["task_complete_index"]):
                
            task_category=data["task_categories"][f'{i}']
            gt_file_system_change_detail=data["file_system_change_details"].get(f'{i}',[])
            gt_lookup_task_answers=data["lookup_task_answer_details"].get(f'{i}',[])
            gt_task_messages=data['messages'][last_index:task_end_index] #不包含总结部分
            last_index=task_end_index+1

            gt_task_trajectory=[[fc for fc in step] for step in data["task_trajectorys"][f'{i}']]
            gt_fsp=[fc for fc in data["fsp"][i] if fc not in ['__miss func__','__miss params__']]
            gt_task_trajectory = [step for steps in gt_task_trajectory for step in steps if step['name'] in gt_fsp]
            print(gt_task_trajectory)

            if i!=task_index:
                # 在对应的任务index之前，先把前面的任务都执行了，把文件系统变成对应的任务index之前的状态
                if 'modification' in task_category:
                    execute_modification_task(gt_task_trajectory,temp_file_system_path,tool_agent)
                    file_system_snapshot_before=snapshot_directory(temp_file_system_path)
            else:
                if data["is_task_completable"][i]==-1:
                    return 0
                else:
                    reward=get_reward_for_one_task(label_task_messages,task_category,gt_task_trajectory,gt_fsp,gt_lookup_task_answers,gt_file_system_change_detail,temp_file_system_path,file_system_snapshot_before,tool_agent)
                    return reward
    finally:
        # 安全释放资源
        if tool_agent.code_session:
            tool_agent.code_session._close()
        if temp_file_system_path.startswith(temp_file_system_dir):
            subprocess.run(["sudo", "rm", "-rf", temp_file_system_path])
            logger.info(f"file_system_path:{temp_file_system_path} deleted")
            
                
if __name__ == "__main__":
    import data_generate, fsp_generate
    project_dir = os.path.dirname(data_generate.__file__)
    fsp_dir = os.path.dirname(fsp_generate.__file__)
    temp_file_system_dir="/mnt/afs2/qinxinyi/function_call_data_temp"
    file_system_path=f"{project_dir}/working_dir/file_system_new"
    tool_defines_path=[f'{project_dir}/tools/defines/python_functions',f'{project_dir}/tools/defines/file_system_functions',f'{project_dir}/tools/defines/database_functions',f'{project_dir}/tools/defines/api_functions']
    logger = set_main_logger(log_path=f'{os.path.dirname(os.path.abspath(__file__))}/error_log.log',console_level=logging.INFO, file_level=logging.WARNING)

    gt_data_path='/mnt/afs2/qinxinyi/function_call_data/mongodb/fsp_500_0718.jsonl'
    rl_data_path='/mnt/afs2/qinxinyi/function_call_data/mongodb/test.jsonl'

    gt_data={}
    with open(gt_data_path,'r',encoding='utf-8') as f:
        for line in f.readlines():
            data=json.loads(line)
            gt_data[data['data_id']]=data

    data_to_reward=[]
    with open(rl_data_path,'r',encoding='utf-8') as f:
        for line in f.readlines():
            data=json.loads(line)
            data_to_reward.append(data)

    data=data_to_reward[0]
    task_index=3
    gt=gt_data[data['data_id']]
    last_task_index=data["task_complete_index"][task_index-1] if task_index>0 else 0
    task_end_index=data["task_complete_index"][task_index]
    task_messages=data['messages'][last_task_index+1:task_end_index]

    reward=get_reward(gt,task_index,task_messages)

