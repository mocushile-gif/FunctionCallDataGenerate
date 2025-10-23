import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from typing import List, Dict, Any, Optional, Union
import re
import inspect
from collections import defaultdict

def load_tool_defines(directory, recursive=False):
    import data_generate
    project_dir = os.path.dirname(data_generate.__file__)
    project_dir=project_dir+'/tools/defines'
    """
    Read all JSON files in a given directory and return their contents as a list.

    Parameters:
    - directory (str): The path to the directory containing JSON files.
    - recursive (bool): Whether to search subdirectories recursively. Defaults to False.

    Returns:
    - A list of dictionaries representing the contents of each JSON file.
    - str: Error message if an exception occurs.
    """
    json_list = {}
    if not os.path.exists(directory):
        raise FileNotFoundError(f"The directory '{directory}' does not exist.")
    try:
        for root, _, files in os.walk(directory):
            for filename in files:
                if filename.endswith('.json'):
                    file_path = os.path.join(root, filename)
                    with open(file_path, 'r', encoding='utf-8') as file:
                        try:
                            json_content = json.load(file)
                            assert json_content['name'] == filename[:-5]
                            if project_dir:
                                json_list[f"{os.path.relpath(os.path.dirname(file_path),project_dir).replace(os.sep, '.')}.{json_content['name']}"]=json_content
                            else:
                                json_list[f"{os.path.basename(os.path.dirname(file_path))}.{json_content['name']}"]=json_content
                        except Exception as e:
                            return f"Error when reading JSON file '{filename}': {str(e)}"
            if not recursive:
                break
        return json_list
    except Exception as e:
        return f"Error processing directory '{directory}': {str(e)}"

import json
from collections import defaultdict
from typing import Dict, List

def collect_tool_response(response_files: list) -> Dict[str, Dict[str, List[str]]]:
    """
    Collect tool responses from a JSONL file, organized by tool name and argument string.
    For each (tool_name, arguments), up to 3 responses will be stored.

    Parameters:
        response_file (str): Path to the JSONL file.

    Returns:
        tool_res_dict (dict): Nested dict with tool_name -> arguments -> list of tool responses.
    """
    tool_res_dict = defaultdict(lambda: defaultdict(str))
    for response_file in response_files:
        with open(response_file, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                try:
                    item = json.loads(line)
                    messages = item.get('messages', [])
                    item_tools=[]
                    for i, message in enumerate(messages):
                        if message.get('role') == 'assistant' and 'tool_calls' in message:
                            for tool_call in message['tool_calls']:
                                tool_name = tool_call['function']['name']
                                if tool_name in item_tools:
                                    continue
                                arguments = tool_call['function'].get('arguments', '{}')
                                tool_call_id = tool_call['id'] if 'id' in tool_call else tool_call['function'].get('id')

                                if len(tool_res_dict[tool_name].keys()) >= 5:
                                    continue
                                elif str(arguments) in tool_res_dict[tool_name]:
                                    continue

                                # 找到对应 tool 响应
                                for j in range(i+1, len(messages)):
                                    reply = messages[j]
                                    if reply.get('role') == 'tool' and reply.get('tool_call_id') == tool_call_id:
                                        tool_res = reply.get('content', '')
                                        tool_res_dict[tool_name][str(arguments)]=tool_res
                                        item_tools.append(tool_name)
                                        break

                except json.JSONDecodeError as e:
                    print(f"[Line {line_num}] JSON decode error: {e}")
                except Exception as e:
                    print(f"[Line {line_num}] Unexpected error: {e}")

    return tool_res_dict

                        

    

# Example usage
if __name__ == "__main__":
    response_file=['/afs_b/qinxinyi/function_call_data/data_generate/generated_data/executable_tools/filtered/v3/generate_executable_all_self+xlam_multimode_gpt.jsonl',
    '/afs_b/qinxinyi/function_call_data/data_generate/generated_data/executable_tools/filtered/v3/generate_executable_all_self+xlam_multimode_qwq.jsonl',
    '/afs_b/qinxinyi/function_call_data/data_generate/generated_data/executable_tools/filtered/v2/generate_executable_all_self+xlam_multimode_qwq.jsonl',
    '/afs_b/qinxinyi/function_call_data/data_generate/generated_data/executable_tools/filtered/v2/generate_executable_all_self+xlam_multimode_gpt.jsonl',
    '/afs_b/qinxinyi/function_call_data/data_generate/generated_data/executable_tools/filtered/v1/generate_executable_mix_all_tools2.jsonl',
    '/afs_b/qinxinyi/function_call_data/data_generate/generated_data/executable_tools/filtered/v1/generate_executable_mix_all_tools.jsonl',
    ]
    tools_define_paths=['/afs_b/qinxinyi/function_call_data/data_generate/tools/defines/xlam_rapidapi_tools',]

    tool_defines={}
    for tools_define_path in tools_define_paths:
        tool_defines.update(load_tool_defines(
            directory=tools_define_path,
            recursive=True,
        ))
    tool_response_dict=collect_tool_response(response_file)
    # print(len(tool_response_dict.keys()))
    # print(len(tool_defines.keys()))

    cache_folder='/afs_b/qinxinyi/function_call_data/data_generate/tools/tool_response_cache'
    collect_tool_responses={}
    for origin_tool_name in tool_defines.keys():
        tool_name=origin_tool_name.split('.')[-1]
        if os.path.exists(os.path.join(cache_folder, tool_name+".json")):
            tools_cache_record = json.load(open(os.path.join(cache_folder, tool_name+".json"), "r"))
        tool_responses=tool_response_dict.get(tool_name,defaultdict(str))
        if not tool_responses or len(tool_responses.keys())<5:
            num=min((5-len(tool_responses.keys())),len(tools_cache_record.keys()))
            for key, val in list(tools_cache_record.items())[:num]:
                tool_responses[key] = val   

        if not tool_responses:
            print('no response found for:'+origin_tool_name)
        collect_tool_responses[tool_name]=tool_responses
    print(len(collect_tool_responses.keys()))
    print(len(tool_defines.keys()))
    with open('/afs_b/qinxinyi/function_call_mt/tools_pool/tools/tool_response_collections_rapidapi.json','w',encoding='utf-8') as f:
        f.write(json.dumps(collect_tool_responses,ensure_ascii=False,indent=4))
        
