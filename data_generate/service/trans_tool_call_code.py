import os
from typing import List, Dict, Any, Optional, Union
import re
import inspect
from data_generate.tools.executable_functions.file_system_functions import *
from data_generate.tools.executable_functions.database_functions import *
from data_generate.tools.executable_functions.python_functions import *

def extract_module_without_main(func_obj) -> List[str]:
    """
    获取定义该函数的完整模块代码（去掉 if __name__ == '__main__' 块 + 去除指定冗余行）
    """
    try:
        file_path = inspect.getsourcefile(func_obj)
        if not file_path:
            return []
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception:
        return []

    result_lines = []
    skip_main = False
    skip_patterns = [
        "from dotenv import load_dotenv",
        "load_dotenv()",
        "tool_agent.file_system_path",
        "os.chdir(work_dir)"
    ]

    for line in lines:
        stripped = line.strip()
        # 跳过 main block
        if re.match(r"if\s+__name__\s*==\s*['\"]__main__['\"]\s*:", stripped):
            skip_main = True
        if skip_main:
            continue

        # 跳过包含指定模式的行
        if any(p in stripped for p in skip_patterns):
            continue

        result_lines.append(line.rstrip('\n'))

    return result_lines



def generate_tool_call_code(assistant_message: Dict[str, Any]) -> str:
    tool_calls = assistant_message.get("tool_calls", [])
    code_blocks = []

    for call in tool_calls:
        tool_data = call.get("function", {})
        tool_name = tool_data.get("name")
        arguments = tool_data.get("arguments", "{}")

        try:
            arguments_dict = json.loads(arguments) if isinstance(arguments, str) else arguments
        except json.JSONDecodeError:
            code_blocks.append(f'''raise RuntimeError("Failed to decode arguments for tool {tool_name}")''')
            continue

        func_obj = globals().get(tool_name)
        if func_obj is None:
            code_blocks.append(f'''raise RuntimeError("Function '{tool_name}' not available.")''')
            continue

        try:
            module_lines = extract_module_without_main(func_obj)
        except Exception as e:
            module_lines = [f'''raise RuntimeError("print('Failed to load module: {str(e)}')")''']

        # 构造调用代码
        args_str = ", ".join(f"{k}={repr(v)}" for k, v in arguments_dict.items())
        call_code = f"\n\n# Call the function\nresult = {tool_name}({args_str})\nprint(result)"

        full_code = "\n".join(module_lines) + call_code
        code_blocks.append(full_code)

    return "\n\n\n".join(code_blocks)


if __name__ == '__main__':
    assistant_message = {
        "role": "assistant",
        "tool_calls": [{
            "function": {
                "name": "create_line_chart",
                "arguments": {
                    "file_path": "./csv_data/Students_Grading_Dataset.csv",
                    "x_source": "Study_Hours_per_Week",
                    "y_source": "Total_Score",
                    "line_style": "--",
                    "line_color": "orange",
                    "marker": "s",
                    "title": "Daily Sales Over Time",
                    "xlabel": "Date",
                    "ylabel": "Sales",
                    "legend_label": "Sales Trend"
                }
            },
            "id": "call_fake_id",
            "type": "function"
        }]
    }
    assistant_message = {
        "role": "assistant",
        "tool_calls": [{
            "function": {
                "name": "extract_workbook_summary3b",
                "arguments": {
                    "file_path": "./excel_data/BikeBuyers_Data.xlsx",
                }
            },
            "id": "call_fake_id",
            "type": "function"
        }]
    }
    code_output = generate_tool_call_code(assistant_message)
    # print(code_output)

    # # test: 尝试运行转成的代码，ok
    from data_generate.tools.executable_functions.shangtang_functions.code_intepreter import code_intepreter
    result = code_intepreter(code_output)
    print(result)

