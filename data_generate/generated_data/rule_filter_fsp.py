import os
import shutil
import json
from tqdm import tqdm
from data_generate.utils.random_change_tool_name import generate_random_tool_name

valid_types = {
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
    "array": list,
    "object": dict,
    "null": type(None)
}

def split_rounds_by_user(messages):
    """
    将消息按用户消息分割为多个会话（session）。
    :param messages: 对话的消息列表
    :return: 分割后的会话列表
    """
    rounds = []
    current_round = []

    for message in messages:
        # 如果是用户消息，且当前round已有内容，则新开一个round
        if message['role'] == 'user' and current_round:
            rounds.append(current_round)
            current_round = [message]
        else:
            # 继续将消息添加到当前round
            current_round.append(message)

    # 添加最后一个round
    if current_round:
        rounds.append(current_round)

    return rounds

def has_duplicates(dict_list):
    seen = set()  # 用于记录已见过的字典
    for d in dict_list:
        # 将字典转换为 JSON 字符串，确保字典嵌套结构也能被正确比较
        dict_str = json.dumps(d, sort_keys=True)  # `sort_keys=True` 保证顺序一致性
        if dict_str in seen:
            return True  # 如果发现重复的字典
        seen.add(dict_str)
    return False  # 没有重复

# 幻觉检测（函数名/参数）和参数类型检测
def detect_hallucination(data):
    messages=data['messages']
    tools=data['tools']
    all_tools={}
    for tool in tools:
        tool_name=tool['name']
        arguments={key:value['type'] if 'type' in value else [item['type'] for item in value['oneOf']] for key,value in tool["parameters"]["properties"].items()}
        default={key:value['default'] for key,value in tool["parameters"]["properties"].items() if 'default' in value}
        all_tools[tool_name]={'arguments':arguments,'default':default,'required':tool["parameters"]["required"] if "required" in tool["parameters"] else []}
    for i,message in enumerate(messages):
        if message['role']=='assistant' and 'tool_calls' in message:
            tool_calls=message['tool_calls']
            if has_duplicates(tool_calls):
                raise Exception('duplicate tool calls in parallel calls')
            for tool_call in tool_calls:
                if tool_call['function']['name'] not in all_tools:
                    raise Exception(f'function hallucination')
                else:
                    if type(tool_call['function']['arguments']) is str:
                        arguments=json.loads(tool_call['function']['arguments'])
                    else:
                        arguments=tool_call['function']['arguments']
                    for argument_name,value in arguments.items():
                        if argument_name not in all_tools[tool_call['function']['name']]["arguments"]:
                            # print(tool_call)
                            raise Exception(f'argument hallucination')
                        # elif argument_name in all_tools[tool_call['function']['name']]["default"] and value==all_tools[tool_call['function']['name']]["default"][argument_name]:
                        #     raise Exception(f'unneccesary use default value')
                        else:
                            argument_type=all_tools[tool_call['function']['name']]["arguments"][argument_name]
                            if type(argument_type) is list:
                                if all([(not isinstance(value, valid_types.get(type))) and value for type in argument_type]):
                                    raise Exception(f'unmatch data type for argument')
                            else:
                                if (not isinstance(value, valid_types.get(argument_type))) and value:
                                    raise Exception(f'unmatch data type for argument')

                    for require_argument in all_tools[tool_call['function']['name']]["required"]:
                        if require_argument not in arguments:
                            raise Exception(f'function call lack of required argument')
        elif message['role']=='assistant' and any([tag in message['content'] for tag in ['<tool_response>','</tool_call>','<tool_call>']]):
            raise Exception(f'tool call decode error')
        elif message['role']=='tool':
            try:
                tool_response=json.loads(message['content'],strict=False)
            except:
                tool_response=message['content']

            if "API doesn\\'t exists" in str(tool_response) \
                or 'Failed to generate fake response' in str(tool_response) \
                or 'Failed to fetch response' in str(tool_response) \
                or 'Generating virtual response' in str(tool_response) \
                :
                raise Exception(f'tool call error')

            # if tool_response is None \
            #         or tool_response==[]  \
            #                     :
            #     call_index=i
            #     while 'tool_calls' not in messages[call_index]:
            #         call_index-=1
            #     functions=[fc['function']['name'] for fc in messages[call_index]['tool_calls']]
            #     if any(permit in functions for permit in ['find_large_files','count_records','get_column_average','search_and_highlight']):
            #         continue
            #     print(data['data_id'])
            #     print(messages[call_index]['tool_calls'])
            #     print([fc['function']['name'] for fc in messages[call_index]['tool_calls']])
            #     print(tool_response)
            #     index_response=i+1
            #     while messages[index_response]['role']!='assistant':
            #         index_response+=1
            #     print(messages[index_response])
            #     raise Exception(f'empty tool response')
            if  'get_file_info' in str(messages[i-1]) \
                and ('Unsupported file type: .xlsx' in str(tool_response) \
                or 'Unsupported file type: .csv' in str(tool_response) \
                or 'Unsupported file type: .txt' in str(tool_response) \
                or 'Unsupported file type: .json' in str(tool_response) \
                or 'Unsupported file type: .jsonl' in str(tool_response) \
                    ):
                raise Exception(f'tool "get_file_info" error')
    return False

# 检测不正常轮次
def detect_abnormal_rounds_cnt(data):
    last_index=1
    for i,task_complete_index in enumerate(data["task_complete_index"]):
        task_trajectory=[]
        task_messages=data['messages'][last_index:task_complete_index+1]
        last_index=task_complete_index+1

        user_rounds=split_rounds_by_user(task_messages)
        if len(user_rounds)>5: # 筛选掉大于10轮数据（用户补充信息过多）
            print(user_rounds)
            raise Exception(f'too many rounds')
        if len(task_messages)>30 and data["is_task_completable"][i]==-1:
            print(len(task_messages))
            raise Exception(f'too many messages in a task')
    # for round in rounds:
    #     if len(round)>20: # 筛选掉每轮数据中消息长度大于20的（可能多次重复调用）
    #         # print(round)
    #         raise Exception(f'too long round')
    # if model.count_tokens(data['messages'],data['tools'])['token_count']>12800:
    #     raise Exception(f'too long tokens')
    return False


# 移除使用默认值的不必要参数
def remove_default_parameters(data):
    messages=data['messages']
    tools=data['tools']
    all_tools={}
    for tool in tools:
        tool_name=tool['name']
        arguments={key:value['type'] if 'type' in value else [item['type'] for item in value['oneOf']] for key,value in tool["parameters"]["properties"].items()}
        default={key:value['default'] for key,value in tool["parameters"]["properties"].items() if 'default' in value}
        all_tools[tool_name]={'arguments':arguments,'default':default}
    for message in messages:
        if message['role']=='assistant' and 'tool_calls' in message:
            if 'content' in message:
                del message['content']
            tool_calls=message['tool_calls']
            for tool_call in tool_calls:
                if tool_call['function']['name'] in all_tools:
                    if type(tool_call['function']['arguments']) is str:
                        arguments=json.loads(tool_call['function']['arguments'])
                    else:
                        arguments=tool_call['function']['arguments']
                    for argument_name,value in list(arguments.items()):
                        if argument_name in all_tools[tool_call['function']['name']]["arguments"]:
                            if argument_name in all_tools[tool_call['function']['name']]["default"] and value==all_tools[tool_call['function']['name']]["default"][argument_name]:
                                # print(f'unneccesary use default value')
                                del arguments[argument_name]
                    tool_call['function']['arguments'] = json.dumps(arguments, ensure_ascii=False)
    return data


def change_tool_name(data):
    tools=data['tools']
    messages=data['messages']
    tool_name_mapping={}
    for tool in tools:
        # tool_metadata=all_tools[(tool['name'],tool['description'])]
        tool_metadata=all_tools.get(tool['name'],'')
        if not tool_metadata:
            continue
        category, tool_name, api_name=tool_metadata['category'],tool_metadata['tool_name'],tool_metadata['api_define']['name']
        random_tool_name=generate_random_tool_name(category, tool_name, api_name)
        tool_name_mapping[tool['name']]=random_tool_name
        tool['name']=random_tool_name
    for message in messages:
        if message['role']=='assistant' and 'tool_calls' in message:
            for tool_call in message['tool_calls']:
                tool_call['function']['name']=tool_name_mapping[tool_call['function']['name']]
                assert tool_call['function']['name'] in list(tool_name_mapping.values())
    data['tools']=tools
    data['messages']=messages
    # tools=[tool['name'] for tool in data['tools']]
    # print(tools)
    # for message in data['messages']:
    #     if message['role']=='assistant' and 'tool_calls' in message:
    #         for tool_call in message['tool_calls']:
    #             assert tool_call['function']['name'] in tools
    return data



def detect_impossible_task(data):
    if any([task==-1 for task in data["is_task_completable"]]):
        print(data["is_task_completable"])
        raise Exception(f'exist impossible task')
    return False

def prune_incompletable_tasks(data: dict) -> dict:
    incompletable_indices = [
        idx for idx, status in enumerate(data.get("is_task_completable", [])) if status == -1
    ]
    if any([idx<=2 for idx in incompletable_indices]):
        return None  # 靠前的任务不可完成，直接舍弃
    
    if not incompletable_indices:
        return data  # 都可以完成，不需要修改
    # print(data.get("is_task_completable"))
    first_incompletable_index = min(incompletable_indices)
    
    # 找到 messages 截断位置
    cutoff_message_index = data["task_complete_index"][first_incompletable_index-1]
    
    # 截断 messages
    data["messages"] = data["messages"][:cutoff_message_index + 1]
    
    # 删除 index >= first_incompletable_index 的任务数据
    keys_to_trim = [
        "task_categories", "dialog_mode", "file_system_change_details",
        "task_trajectorys", "tasks", "task_complete_index", "is_task_completable"
    ]
    data['round_cnt']=first_incompletable_index
    for key in keys_to_trim:
        if key in data:
            if isinstance(data[key], list):
                data[key] = data[key][:first_incompletable_index]
            elif isinstance(data[key], dict):
                data[key] = {
                    k: v for k, v in data[key].items()
                    if int(k) < first_incompletable_index
                }
            if key!="file_system_change_details":
                assert len(data[key])==data["round_cnt"]
    # print(cutoff_message_index)
    # print(data["task_complete_index"])
    # print(len(data['messages']))
    # print(len(data["tasks"]))
    # print(round_cnt)
    assert data["task_complete_index"][-1]==len(data['messages'])-1
    return data


def get_file_names(folder_path):
    """
    获取指定文件夹下的所有文件名
    :param folder_path: 文件夹路径
    :return: 文件名列表
    """

    try:
        # 获取文件夹下的所有“文件”路径（不包括子文件夹）
        file_names = [
            os.path.join(folder_path, file_name)
            for file_name in os.listdir(folder_path)
            if os.path.isfile(os.path.join(folder_path, file_name))
        ]
        return file_names
    except Exception as e:
        print(f"Error reading folder: {e}")
        return []


def reset_folder(folder_path):
    """
    删除并重建指定的文件夹。
    :param folder_path: 要重建的文件夹路径
    """
    # 检查文件夹是否存在
    if os.path.exists(folder_path):
        # 删除整个文件夹
        shutil.rmtree(folder_path) 
    # 重新创建文件夹
    os.mkdir(folder_path)


def run_rule_filter(folder_path,filter_data_path):
    data_path_lst = get_file_names(folder_path)
    reset_folder(filter_data_path)

    import json
    from collections import defaultdict
    filter_data_cnt=defaultdict(int)
    data_cnt=defaultdict(int)
    filter_reason = defaultdict(int)
    for data_path in data_path_lst:
        file_name=data_path.split('/')[-1].split('.')[0]
        print('Start filtering for: '+file_name)
        with open(data_path,'r',encoding='utf-8') as f,\
        open(f'{filter_data_path}/{file_name}.jsonl','a+',encoding='utf-8') as out_f:
            for line in tqdm(f.readlines()):
                # try:
                data=json.loads(line,strict=False)
                data_cnt[file_name]+=1
                # data=prune_incompletable_tasks(data)
                # if not data:
                #     filter_data_cnt[file_name]+=1
                #     filter_reason['impossible task in first two tasks']+=1
                #     continue
                # except:
                #     continue

                try:
                    detect_hallucination(data)
                    detect_abnormal_rounds_cnt(data)
                    # if "is_task_completable" in data:
                    #     detect_impossible_task(data)
                    # call_tool_in_no_tool_use(data)
                except Exception as e:
                        filter_data_cnt[file_name]+=1
                        filter_reason[str(e)]+=1
                        continue

                out_f.write(json.dumps(data,ensure_ascii=False)+'\n')
    print(f"\nFiltered data cnt / All data cnt:")
    print(f'{sum(filter_data_cnt.values())} / {sum(data_cnt.values())} ({round(sum(filter_data_cnt.values())/sum(data_cnt.values())*100,2)}%)')
    for file_name, num in sorted(filter_data_cnt.items(), key=lambda x: x[1], reverse=True):
        print(f'{file_name}: {num}/{data_cnt[file_name]} ({round(num/data_cnt[file_name]*100,2)}%)')
    
    print(f"\nFilter reason:")
    for reason, num in sorted(filter_reason.items(), key=lambda x: x[1], reverse=True):
        print(f'{reason}: {num}')
    print(f"\nRetained data cnt / All data cnt:")
    print(f'{sum(data_cnt.values())-sum(filter_data_cnt.values())} / {sum(data_cnt.values())} ({round((sum(data_cnt.values())-sum(filter_data_cnt.values()))/sum(data_cnt.values())*100,2)}%)')

if __name__ == "__main__":
    import data_generate
    from data_generate.agent.model import QwQFunction
    project_dir = os.path.dirname(data_generate.__file__)

    with open(f'{project_dir}/tools/all_tools_metadata.json','r',encoding='utf-8') as f:
        all_tools_metadata=json.load(f)
        all_tools={}
        for k,v in all_tools_metadata.items():
            # all_tools[(v['api_define']['name'],v['api_define']['description'])]=v
            all_tools[(v['api_define']['name'])]=v
    model = QwQFunction()
    label_data_path = f"{project_dir}/generated_data/executable_tools/generated/fsp"
    category_data_path=f'{project_dir}/generated_data/executable_tools/filtered/fsp'
    run_rule_filter(label_data_path,category_data_path)