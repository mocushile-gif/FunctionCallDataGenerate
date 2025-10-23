import os
import shutil
import json
import random
import yaml
import json
import json
from tqdm import tqdm
import xml.etree.ElementTree as ET
from collections import defaultdict
import string
from data_generate.utils.random_change_tool_name import generate_random_tool_name
from data_generate.utils.format_tool_defines import format_tool_defines

random.seed(42)
# system_prompt_prefix = """You are an expert in composing functions. You are given a question and a set of possible functions. \nBased on the question, you will need to make one or more function/tool calls to achieve the purpose. \nIf none of the function can be used, point it out. If the given question lacks the parameters required by the function,\nalso point it out. You should only return the function call in tools call sections.\nHere is a list of functions in JSON format that you can invoke:\n"""
# system_prompt_suffix = """. \nShould you decide to return the function call(s). \nPut it in the format of [func1(params_name=params_value, params_name2=params_value2...), func2(params)]\n\nNO other text MUST be included. \n"""

system_prompt_prefix = """Here is a list of functions in JSON format that you can invoke:\n"""
toolace_system_prompt_suffix = """. \nShould you decide to return the function call(s). \nPut it in the format of [func1(params_name=params_value, params_name2=params_value2...), func2(params)]\n\nNO other text MUST be included. \n"""

xml_system_prompt_suffix = """
If you decide to return the function call(s), output them strictly in the following XML format:

<functions>
  <function name="func1">
    <param name="param1">value1</param>
    <param name="param2">value2</param>
  </function>
  <function name="func2">
    <param name="paramA">valueA</param>
  </function>
</functions>

NO other text MUST be included.  
The output must be a well-formed XML snippet exactly as shown, representing the function calls and their parameters.
"""

yaml_system_prompt_suffix = """
If you decide to return the function call(s), output them strictly in the following YAML format:

- function: func1
  params:
    param1: value1
    param2: value2
- function: func2
  params:
    paramA: valueA

NO other text MUST be included.  
The output must be a valid YAML snippet exactly as shown, representing the function calls and their parameters.
"""

def reset_folder(folder_path):
    """
    删除并重建指定的文件夹。
    :param folder_path: 要重建的文件夹路径
    """
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
    os.makedirs(folder_path)

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
        if random_tool_name=='hammer':
            letters = list(string.ascii_uppercase)+list(string.ascii_lowercase)+['_','.']+list(map(str,range(10)))
            # new_param_name = ''.join(random.choice(letters) for i in range(random.randint(4,10)))  # 生成随机字符串
            random_tool_name = ''.join(random.choices(letters,k=random.randint(5,15))) 
        else:
            random_tool_name=generate_random_tool_name(category, tool_name, api_name)
            
        tool_name_mapping[tool['name']]=random_tool_name
        tool['name']=random_tool_name
        # print(random_tool_name)
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

# 将转换函数和工具调用的处理封装为一个函数
def trans_toolace_format(tool_calls):
    tool_call_list = []
    for tool_call in tool_calls:
        if type(tool_call["function"]["arguments"]) is str:
            arguments = json.loads(tool_call["function"]["arguments"])
        else:
            arguments = tool_call["function"]["arguments"]
        tool_call_name = tool_call["function"]["name"]
        parameter_str_list = []
        for key, value in arguments.items():
            parameter_str = (key + "=" + json.dumps(value))
            parameter_str_list.append(parameter_str)
        tool_call_parameter_result = ", ".join(parameter_str_list)
        tool_call_result = tool_call_name + "("+tool_call_parameter_result+")"
        tool_call_list.append(tool_call_result)
    return "[" + ", ".join(tool_call_list) + "]"

def trans_yaml_format(tool_calls):
    """
    把工具调用列表格式化为 YAML 格式字符串

    tool_calls: list of dict，每个包含 "function":{"name":str, "arguments":str|dict}

    返回：YAML格式字符串
    """
    out_list = []

    for call in tool_calls:
        func_name = call["function"]["name"]
        args_raw = call["function"]["arguments"]
        # arguments可能是json字符串，转换成dict
        if isinstance(args_raw, str):
            try:
                args = json.loads(args_raw)
            except json.JSONDecodeError:
                args = {}
        else:
            args = args_raw

        out_list.append({
            "function": func_name,
            "params": args
        })

    # yaml.safe_dump 默认会将bool、数字等自动转成对应yaml类型
    # 设置 default_flow_style=False 保证是块格式
    yaml_str = yaml.safe_dump(out_list, allow_unicode=True, default_flow_style=False)
    return yaml_str

def trans_xml_format(tool_calls):
    """
    把工具调用列表格式化为指定的 XML 字符串

    参数:
        tool_calls: list of dict, 每个dict包含 "function": {"name": str, "arguments": str|dict}

    返回:
        str, XML 格式字符串
    """
    root = ET.Element("functions")

    for call in tool_calls:
        func_name = call["function"]["name"]
        args_raw = call["function"]["arguments"]

        # 解析 arguments
        if isinstance(args_raw, str):
            try:
                args = json.loads(args_raw)
            except json.JSONDecodeError:
                args = {}
        else:
            args = args_raw

        func_elem = ET.SubElement(root, "function", name=func_name)

        for k, v in args.items():
            param_elem = ET.SubElement(func_elem, "param", name=k)
            param_elem.text = str(v)

    # 生成字符串，含xml声明
    xml_str = ET.tostring(root, encoding="unicode")
    return xml_str

def call_id_save(tool_calls, temp_call_id_dict):
    for tool_call in tool_calls:
        tool_call_id = tool_call["id"]
        tool_call_name = tool_call["function"]["name"]
        temp_call_id_dict[tool_call_id] = tool_call_name
    return temp_call_id_dict

def trans_format_for_file(input_file_path, output_file_path,trans_format):
    with open(output_file_path, "w+") as output_file:
        data=[]
        with open(input_file_path, "r") as input_file:
            for in_line in input_file:
                json_line = json.loads(in_line)
                if random_func_name:
                    try:
                        json_line=change_tool_name(json_line)
                    except:
                        pass
                temp_call_id_dict = {}
                json_line_message = json_line["messages"]

                chosen_format = random.choices(list(tool_defines_format_choices.keys()), weights=tool_defines_format_choices.values(), k=1)[0]
                json_line_tool = format_tool_defines(json_line["tools"], chosen_format)

                if trans_format=='mix':
                    select_format = random.choices(list(mix_types.keys()), weights=mix_types.values(), k=1)[0]
                else:
                    select_format = trans_format
                select_formats[select_format]+=1
                if select_format=='original':
                    data.append({'messages':json_line["messages"],
                    'tools':json_line["tools"]})
                    continue
                elif select_format=='toolace':
                    system_prompt_suffix=toolace_system_prompt_suffix
                elif select_format=='xml':
                    system_prompt_suffix=xml_system_prompt_suffix
                elif select_format=='yaml':
                    system_prompt_suffix=yaml_system_prompt_suffix
                else:
                    raise Exception("unsupport format")
                system_prompt = system_prompt_prefix + json_line_tool + system_prompt_suffix

                utterance_list = []
                if json_line_message[0]["role"] == "system":
                    new_utterance = {"role": "system", "content": json_line_message[0]['content']+system_prompt}
                    utterance_list.append(new_utterance)
                    json_line_message = json_line_message[1:]
                for utterance in json_line_message:
                    if (utterance["role"] == "assistant") and ("tool_calls" in utterance):
                        # 对openAI工具调用进行数据格式转换
                        if select_format=='toolace':
                            tool_format = trans_toolace_format(utterance["tool_calls"])
                        elif select_format=='yaml':
                            tool_format = trans_yaml_format(utterance["tool_calls"])
                        elif select_format=='xml':
                            tool_format = trans_xml_format(utterance["tool_calls"])
                        temp_call_id_dict = call_id_save(utterance["tool_calls"], temp_call_id_dict)
                        new_utterance = {"role": "assistant", "content": tool_format}
                        utterance_list.append(new_utterance)
                    elif utterance["role"] == "tool":
                        tool_call_id = utterance["tool_call_id"]
                        tool_call_name = temp_call_id_dict[tool_call_id]
                        tool_response = json.dumps({"name": tool_call_name, "result": utterance["content"]})
                        new_utterance = {"role": "tool", "content": tool_response}
                        utterance_list.append(new_utterance)
                    else:
                        new_utterance = utterance
                        utterance_list.append(new_utterance)
                data.append(utterance_list)
            for item in data:
                output_file.write(json.dumps(item, ensure_ascii=False) + "\n")

def trans_format_for_folder(input_folder_path, output_folder_path, trans_format):
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)
    else:
        reset_folder(output_folder_path)
    # 获取文件夹中所有的文件
    file_list = os.listdir(input_folder_path)
    for file_name in tqdm(file_list):
        input_file_path = os.path.join(input_folder_path, file_name)
        if os.path.isfile(input_file_path):
            # 拆分文件名和扩展名
            base_name, ext = os.path.splitext(file_name)
            if trans_format=='mix':
                file_suffix=''.join([k+str(v) for k,v in mix_types.items()])
            else:
                file_suffix=trans_format
            # 在文件名尾部添加 _format
            if random_func_name=='hammer':
                new_file_name = f"{base_name}_{file_suffix}{ext}_hammer"
            else:
                new_file_name = f"{base_name}_{file_suffix}{ext}"
            output_file_path = os.path.join(output_folder_path, new_file_name)
            if os.path.exists(output_file_path):
                continue
            trans_format_for_file(input_file_path, output_file_path, trans_format)
    total = sum(select_formats.values())
    proportions = {k: round(v / total,2) for k, v in select_formats.items()}
    print(proportions)

# 主执行函数
if __name__ == "__main__":
    import data_generate
    project_dir = os.path.dirname(data_generate.__file__)

    with open(f'{project_dir}/tools/all_tools_metadata.json','r',encoding='utf-8') as f:
        all_tools_metadata=json.load(f)
        all_tools={}
        for k,v in all_tools_metadata.items():
            # all_tools[(v['api_define']['name'],v['api_define']['description'])]=v
            all_tools[(v['api_define']['name'])]=v

    trans_format='mix'
    mix_types={'yaml':1,'original':0,'toolace':1,'xml':0}
    # 试了hammer把工具名改成随机字符串，实验貌似用处不大
    random_func_name='random_change_tool_name' #如果是hammer则转为随机字符串，否则只是转变格式
    # 试了不同格式的工具定义，但实验貌似没啥用
    tool_defines_format_choices = {'json':1, 'yaml':0, 'toml':0, 'xml':0}

    select_formats = defaultdict(int)
    input_folder = f"{project_dir}/generated_data/executable_tools/sampled"  # 输入文件夹路径
    output_folder = f"{project_dir}/generated_data/executable_tools/{trans_format}_format"  # 输出文件夹路径

    input_folder = f"{project_dir}/generated_data/executable_tools/filtered/fsp"  # 输入文件夹路径
    output_folder = f"{project_dir}/generated_data/executable_tools/{trans_format}_format/fsp"  # 输出文件夹路径

    input_folder = f"{project_dir}/generated_data/executable_tools/filtered/v4"  # 输入文件夹路径
    output_folder = f"{project_dir}/generated_data/executable_tools/{trans_format}_format/v4"  # 输出文件夹路径
    # 确保输出文件夹存在
    trans_format_for_folder(input_folder, output_folder, trans_format)
