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

def load_graph(dependency_data_path):
    """
    构建依赖图，边方向为：target_func → func（即调用顺序）
    """
    import json
    with open(dependency_data_path, "r", encoding="utf-8") as f:
        raw_cache = json.load(f)
        relation_cache = {
            tuple(k.split(" → ", 1)): v for k, v in raw_cache.items()
        }
    # 构建图
    graph = defaultdict(list)
    for (source, target), is_related in relation_cache.items():
        if is_related:
            graph[source].append(target) 
    return graph

from collections import Counter

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

    return False, None

def label_one_data(data):
    if "task_categories" in data:
        return data
    task_categories={}
    file_system_change_details={}
    tools_dict=init_tools(data['tools'],tool_defines_path)
    temp_file_system_path=create_temp_file_system(data['selected_files'],file_system_path,temp_file_system_dir)
    file_system_snapshot_before=snapshot_directory(temp_file_system_path)
    tool_agent = ToolAgent(
            llm_name='gpt',
            file_system_path=temp_file_system_path,
            tools=tools_dict,
            output_limit=4096,
        )
    try:
        for i,task_end_index in enumerate(data["task_complete_index"]):
            # task_messages=data['messages'][last_index:task_end_index]
            # last_index=task_end_index
            # task_trajectory=[[fc['name'] for fc in step] for step in data["task_trajectorys"][f'{i}']]
            # task_trajectory = [name for step in task_trajectory for name in step if name not in fixed_tools]
            # fsp=[fc for fc in data["fsp"][i] if fc not in ['__miss func__','__miss params__']+fixed_tools]
            # trajectory_reward=compute_reward(task_trajectory, fsp)
            # if trajectory_reward==0:
            #     print(f'gpt_trajectory: {task_trajectory}')
            #     print(f'fsp_trajectory: {fsp}')
            #     print(trajectory_reward)
            # 可以设置模型与gpt和与fsp都匹配，取最高分
            
            modification_task_trajectory=[]
            lookup_task_trajectory=[]
            task_trajectory=[[fc for fc in step] for step in data["task_trajectorys"][f'{i}']]
            # task_trajectory = [name for step in task_trajectory for name in step if name not in fixed_tools]
            task_trajectory = [name for step in task_trajectory for name in step]
            for tool in task_trajectory:
                if 'modification' in tool_category[tool['name']]:
                    modification_task_trajectory.append(tool)
                else:
                    lookup_task_trajectory.append(tool)

            # 若task的action中包含modification工具，且这些工具的actions会对文件系统造成改动，则task属于modification类型
            # 若task的action中不包含modification工具，或包含，但不会对文件系统造成改动，则task属于lookup类型
            if modification_task_trajectory and lookup_task_trajectory:
                # print([fc['name'] for fc in modification_task_trajectory])
                task_category='modification & lookup'
            elif modification_task_trajectory:
                task_category='modification'
            elif lookup_task_trajectory:
                # print([fc['name'] for fc in lookup_task_trajectory])
                task_category='lookup'
            else:
                task_category='no-function-call'
            # print(modification_task_trajectory)
            # 相关文件复制到临时文件夹中，执行modification_task_trajectory，如果文件夹有变化，则保留原分类，若没有变化则为lookup
            if modification_task_trajectory:
                execute_modification_task(modification_task_trajectory,temp_file_system_path,tool_agent)
                file_system_snapshot_after=snapshot_directory(temp_file_system_path)
                change_flag,change_details=compare_snapshots(file_system_snapshot_before, file_system_snapshot_after,temp_file_system_path)
                if change_flag:
                    file_system_change_details[i]=change_details
                    logger.info(f"Modification task: {change_details}")
                else:
                    task_category='lookup'
                file_system_snapshot_before=file_system_snapshot_after
            task_categories[i]=task_category
            
        data['task_categories']=task_categories
        data['file_system_change_details']=file_system_change_details
        # print(data["task_trajectorys"])
        return data
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

    tool_category=load_graph(f'{fsp_dir}/data/graph/tool_category_graph.json')
    data_path=f'{project_dir}/generated_data/executable_tools/generated/fsp/generate_fsp_all_self_gpt_500_0718.jsonl'
    data_path=f'{project_dir}/generated_data/executable_tools/generated/fsp/test.jsonl'
    label_data_path=f'{fsp_dir}/data/generate_fsp_all_self_gpt_labeled_500_0718.jsonl'
    label_data_path=f'{fsp_dir}/data/test.jsonl'
    tool_defines_path=[f'{project_dir}/tools/defines/python_functions',f'{project_dir}/tools/defines/file_system_functions',f'{project_dir}/tools/defines/database_functions',f'{project_dir}/tools/defines/api_functions']
    fixed_tools=['display_directory_tree','get_file_info','read_file_contents','get_all_table_names','get_table_info','get_column_info','get_database_info']
    logger = set_main_logger(log_path=f'{os.path.dirname(os.path.abspath(__file__))}/error_log.log',console_level=logging.INFO, file_level=logging.WARNING)

    # with open(label_data_path,'w',encoding='utf-8') as out_f:
    #     pass

    # with open(data_path,'r',encoding='utf-8') as f,\
    #     open(label_data_path,'a',encoding='utf-8') as out_f:
    #     for line in f.readlines():
    #         data=json.loads(line)
    #         labeled_data=label_one_data(data)
    #         out_f.write(json.dumps(labeled_data, ensure_ascii=False)+"\n")

    existing_data_id=[]
    if os.path.exists(label_data_path):
        with open(label_data_path,'r',encoding='utf-8') as f:
            for line in f.readlines():
                data=json.loads(line)
                existing_data_id.append(data['data_id'])

    remaining_data=[]
    remaining_data_id=[]
    with open(data_path,'r',encoding='utf-8') as f:
        for line in f.readlines():
            data=json.loads(line)
            if data['data_id'] not in existing_data_id:
                remaining_data.append(data)
            remaining_data_id.append(data['data_id'])

    failed_cnt = 0
    progress_bar = tqdm(total=len(remaining_data)+len(existing_data_id))
    progress_bar.update(len(existing_data_id))
    with ThreadPoolExecutor(max_workers=1) as executor:
        futures = [executor.submit(label_one_data,data) for data in remaining_data]
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
                    with open(label_data_path,'a',encoding='utf-8') as out_f:
                        out_f.write(json.dumps(result, ensure_ascii=False)+"\n")
            except Exception as e:
                logger.critical(f"Error: {e}")  # 打印线程内部的异常
                logger.critical(traceback.print_exc())