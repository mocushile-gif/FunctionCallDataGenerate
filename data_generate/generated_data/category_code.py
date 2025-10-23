import json
from collections import defaultdict
import os
import shutil

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

def process_dialogues(data):

    rounds=split_rounds_by_user(data['messages'])
    tool_lst=data['tools']
    # Initialize counters and data holders
    tool_calls = defaultdict(int)
    single_tool_call = 0
    single_tool_call_from_multiple=0
    multiple_tool_call=0
    parallel_tool_call = 0
    sequential_tool_call = 0
    round_count = len(rounds)
    round_with_tool_calls=0
    tool_sequence_per_question = defaultdict(int)
    tool_count_per_call = defaultdict(int)
    
    for current_round in rounds:

        sequence_tool_count=0
        round_with_tool_calls_flag=0
        for message in current_round:
            if 'tool_calls' in message:
                sequence_tool_count+=1
                round_with_tool_calls_flag=1
                
                for tool_call in message['tool_calls']:
                    tool_calls[tool_call['function']['name']] += 1
                tool_names=list(set([tool_call['function']['name'] for tool_call in message['tool_calls']]))

                # Check tools count to determine call type (single, parallel)
                tool_count=len(message['tool_calls'])
                if tool_count == 1 and len(tool_lst)==1:
                    single_tool_call += 1
                elif tool_count == 1 and len(tool_lst)>1:
                    single_tool_call_from_multiple += 1
                elif tool_count > 1 and len(tool_names)==1:
                    parallel_tool_call += 1
                elif tool_count > 1 and len(tool_names)>1:
                    multiple_tool_call += 1
                tool_count_per_call[tool_count]+=1
        round_with_tool_calls+=round_with_tool_calls_flag
        tool_sequence_per_question[sequence_tool_count]+=1
        if sequence_tool_count>1:
            sequential_tool_call += 1
    
    tool_sequence_per_question = dict(sorted(tool_sequence_per_question.items(), key=lambda item: int(item[0])))
    tool_count_per_call = dict(sorted(tool_count_per_call.items(), key=lambda item: int(item[0])))
    tool_call_lst = dict(sorted(dict(tool_calls).items(), key=lambda item: item[1], reverse=True))

    # Compile metadata dictionary
    metadata = {
        "id": data.get("id", None),
        "round": round_count,
        "round_with_tool_calls": round_with_tool_calls,
        "tools_lst": [tool['function']['name'] if 'function' in tool else tool['name'] for tool in data['tools']],
        "tool_call_lst": tool_call_lst,
        "single_tool_call": single_tool_call,
        "single_tool_call_from_multiple":single_tool_call_from_multiple,
        "parallel_tool_call": parallel_tool_call,
        "multiple_tool_call": multiple_tool_call,
        "sequential_tool_call": sequential_tool_call,
        "tool_count_per_call": tool_count_per_call,
        "tool_sequence_per_question": tool_sequence_per_question,
    }
    
    return metadata

# # Load JSON data from the uploaded file
# with open('/mnt/nvme0/qinxinyi/fc_score/sample_data.json', 'r') as file:
#     data = json.load(file)

# # Process the dialogues
# metadata = process_dialogues(data)

# # Save the metadata into a new JSON file
# output_file = '/mnt/nvme0/qinxinyi/fc_score/sample_data_metadata.json'
# with open(output_file, 'w') as outfile:
#     json.dump([metadata], outfile, ensure_ascii=False, indent=4)

# print(f"Metadata has been saved to {output_file}")

def get_file_names(folder_path):
    """
    获取指定文件夹下的所有文件名
    :param folder_path: 文件夹路径
    :return: 文件名列表
    """
    try:
        # 获取文件夹下的所有文件名
        file_names = [os.path.join(folder_path,file_name) for file_name in os.listdir(folder_path)]
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

def get_category(folder_path,label_data_path):
    data_path_lst = get_file_names(folder_path)
    reset_folder(label_data_path)

    import json
    for data_path in data_path_lst:
        file_name=data_path.split('/')[-1].split('.')[0]
        with open(data_path,'r',encoding='utf-8') as f,\
        open(f'{label_data_path}/{file_name}.json','a+',encoding='utf-8') as out_f:
            for line in f.readlines():
                data=json.loads(line)
                metadata = process_dialogues(data)
                out_f.write(json.dumps(metadata,ensure_ascii=False))
                out_f.write('\n')
        print(file_name)

if __name__ == "__main__":
    label_data_path = "/mnt/nvme0/qinxinyi/fc_score/data/label_data"
    category_data_path='/mnt/nvme0/qinxinyi/fc_score/data/categories'
    get_category(label_data_path,category_data_path)

