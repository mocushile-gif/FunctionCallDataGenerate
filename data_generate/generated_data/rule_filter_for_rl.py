import os
import shutil
import json
from tqdm import tqdm
import traceback
from rule_filter import *

def remove_impossible_task(data):
    if (
        "is_task_completable" in data
        and "task_complete_index" in data
        and "dialog_mode" in data
        and data["dialog_mode"]
        and len(data["is_task_completable"]) == len(data["dialog_mode"])
    ):
        # 都不可完成
        
        # reasoning数据有问题,之前澄清两次如果还没解决就不加入历史，但忘了去掉对应的reasoning了
        if max([int(k) for k in list(data["assistant_reasonings"].keys())]) > len(data['messages'])-1:
            print('wrong data')
            return False        

        non_completable_range = []

        # 找出所有不可完成的段落
        if any(task == -1
               for task, dialog_mode in zip(data["is_task_completable"], data["dialog_mode"])):
            
            last_index = [index for index,message in enumerate(data['messages']) if message['role']=='assistant'][0]-1
            for task, index, dialog_mode in zip(
                data["is_task_completable"], data["task_complete_index"], data["dialog_mode"]
            ):
                if task == -1:
                    non_completable_range.append((last_index, index))
                last_index = index+1

        # 需要删除的 message index
        remove_ranges = set()
        for start, end in non_completable_range:
            remove_ranges.update(range(start, end+1))

        # 保留的 message 及其 index 映射关系
        final_messages = []
        index_map = {}  # old_index -> new_index
        for i, m in enumerate(data["messages"]):
            if i not in remove_ranges:
                final_messages.append(m)
                index_map[i] = len(final_messages)-1
        # 筛选保留的 task entries
        new_is_task_completable = []
        new_task_complete_index = []
        new_dialog_mode = []
        new_reasoning={}
        for task, index, mode in zip(
            data["is_task_completable"], data["task_complete_index"], data["dialog_mode"]
        ):
            if index not in remove_ranges:
                # 如果该段完整保留
                if index in index_map:
                    new_is_task_completable.append(task)
                    new_task_complete_index.append(index_map[index])
                    new_dialog_mode.append(mode)

        # try:
        for index in data["assistant_reasonings"].keys():
            if int(index) not in remove_ranges:
                new_reasoning[str(index_map[int(index)])]=data["assistant_reasonings"][index]
        
        # 更新数据
        data["messages"] = final_messages
        data["is_task_completable"] = new_is_task_completable
        data["task_complete_index"] = new_task_complete_index
        data["dialog_mode"] = new_dialog_mode
        data["assistant_reasonings"]=new_reasoning
        assert len(data["task_complete_index"])==len(data["is_task_completable"])==len(data["dialog_mode"])
        assert new_task_complete_index[-1]==len(data["messages"])-1
        assert sum(data["is_task_completable"])==len(data["is_task_completable"])
        assert len(data["assistant_reasonings"])==len([1 for message in data['messages'] if message['role']=='assistant'])
        assert all([data["messages"][int(index)]["role"]=="assistant" for index in data["assistant_reasonings"].keys()])
        # except Exception as e:
            # print(f'{data["data_id"]}: error in remove impossible task: {traceback.format_exc()}')
            # return False
    return data

def run_rule_filter_for_rl(folder_path,filter_data_path):
    data_path_lst = get_file_names(folder_path)
    reset_folder(filter_data_path)

    import json
    filter_data_cnt=0
    all_impossible_tasks=0
    removed_impossible_tasks=0
    tasks=0
    data_cnt=0
    from collections import defaultdict
    filter_reason = defaultdict(int)
    for data_path in data_path_lst:
        file_name=data_path.split('/')[-1].split('.')[0]
        print(file_name)
        with open(data_path,'r',encoding='utf-8') as f,\
        open(f'{filter_data_path}/{file_name}.jsonl','a+',encoding='utf-8') as out_f:
            for line in tqdm(f.readlines()):
                data=json.loads(line,strict=False)
                data_cnt+=1
                wrong_flag = detect_hallucination(data)
                mix_language_question_flag = detect_language_mix(data)
                abnormal_flag = detect_abnormal_rounds_cnt(data)
                all_impossible_tasks+=sum([1 if task==-1 else 0 for task in data["is_task_completable"]])
                tasks+=len(data["is_task_completable"])

                all_impossible_task_flag=0
                if all(task == -1 for task in data["is_task_completable"]):
                    print('all tasks are impossible')
                    all_impossible_task_flag=1

                if all_impossible_task_flag or wrong_flag or abnormal_flag or mix_language_question_flag \
                     or ('.db' in str(data['selected_files']) and 'database' not in str(data['selected_files'])) \
                        :
                    filter_data_cnt+=1
                    if all_impossible_task_flag:
                        filter_reason['all_impossible_task_flag']+=1
                    elif wrong_flag:
                        filter_reason['hallucination or wrong']+=1
                    elif abnormal_flag:
                        filter_reason['abnormal rounds cnt']+=1
                    elif mix_language_question_flag:
                        filter_reason['mix language question']+=1
                    elif ('.db' in str(data['selected_files']) and 'database' not in str(data['selected_files'])):
                        filter_reason['wrong database data']+=1
                else:
                    # data=change_tool_name(data)
                    # data=remove_default_parameters(data)
                    removed_impossible_tasks+=sum([1 if task==-1 else 0 for task in data["is_task_completable"]])
                    data=remove_impossible_task(data)
                    if data:
                        data=get_task_metadata(data)
                        out_f.write(json.dumps(data,ensure_ascii=False)+'\n')
                    else:
                        filter_reason['error in remove_impossible_task']+=1
                        filter_data_cnt+=1
            print(filter_reason)
            print(f'removed {removed_impossible_tasks} impossible tasks / all {all_impossible_tasks} impossible tasks / all {tasks} tasks')
            print(f"filtered data cnt/all data cnt:{filter_data_cnt}/{data_cnt}")
        print('Filter end for file: '+file_name)

if __name__ == "__main__":
    label_data_path = f"{os.environ['HOME_DIR']}/function_call_data/data_generate/generated_data/executable_tools/generated/task"
    category_data_path=f'{os.environ["PROJECT_DIR"]}/generated_data/executable_tools/filtered/task_for_rl'
    run_rule_filter_for_rl(label_data_path,category_data_path)