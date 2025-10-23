import os
import re
import json
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append('/mnt/nvme0/qinxinyi/function_call_data/data_generate')
sys.path.append('/mnt/nvme0/qinxinyi/function_call_data/data_generate/agent')
from agent.model import *

function_folder_path = '/mnt/nvme0/qinxinyi/function_call_data/data_generate/tools/executable_functions/file_system_functions'
define_folder_path = '/mnt/nvme0/qinxinyi/function_call_data/data_generate/tools/defines/file_system_functions'
new_define_folder_path = '/mnt/nvme0/qinxinyi/function_call_data/data_generate/tools/defines/temp'

PROMPT="""
python函数：
{function}

请你基于以上的python写出其openai格式的json函数定义，请确保description的完整和合理性，参数类型正确。
注意：tool_agent不要添加到参数中。默认为英文描述。
你的输出只包含该定义，无需额外解释。

openai格式的json函数定义例子：
{example}
"""

def get_function_define(function_name):
    with open(f'{function_folder_path}/{function_name}.py', 'r', encoding='utf-8') as f:
        function_str = f.read()
    with open('/mnt/nvme0/qinxinyi/function_call_data/data_generate/tools/defines/python_functions/calculate_average.json','r',encoding='utf-8') as f:
        example=json.loads(f.read())
    template={"function": function_str,"example":example}
    prompt = PROMPT.format(**template)
    message = [{"role": "user", "content": prompt}]
    llm = QWen25Function(args={'temperature': 0.7})
    res,error_code = llm.chat(message)

    if '```json' in res['content']:
        match = re.findall(r'```json\s*(.*?)\s*```', res['content'], re.DOTALL)[0]
    else:
        match = res['content']
    try:
        parsed_match = json.loads(match.replace("'", '\\"'), strict=False)
        with open(f'{new_define_folder_path}/{function_name}.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(parsed_match, ensure_ascii=False, indent=4))
    except Exception as e:
        raise Exception('Tool call arguments decode error:\n' + str(e))

def generate_function_definitions():
    for filename in os.listdir(function_folder_path):
        if filename.endswith('.py'):
            function_name = filename[:-3]
            if not os.path.exists(f'{define_folder_path}/{function_name}.json') and not os.path.exists(f'{new_define_folder_path}/{function_name}.json'):
                print(function_name)
                get_function_define(function_name)

generate_function_definitions()