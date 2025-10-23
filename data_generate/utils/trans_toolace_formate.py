import os
import json

system_prompt_prefix = """You are an expert in composing functions. You are given a question and a set of possible functions. \nBased on the question, you will need to make one or more function/tool calls to achieve the purpose. \nIf none of the function can be used, point it out. If the given question lacks the parameters required by the function,\nalso point it out. You should only return the function call in tools call sections.\nHere is a list of functions in JSON format that you can invoke:\n"""
system_prompt_suffix = """. \nShould you decide to return the function call(s). \nPut it in the format of [func1(params_name=params_value, params_name2=params_value2...), func2(params)]\n\nNO other text MUST be included. \n"""

SQL_TOOL_PROMPT = """
Database-related Tools Notes:
1.You have access to five databases:
 ###airlines: A dataset of operations from a Russian airline, covering various aspects such as planes, airports, flights, boarding passes, bookings, seats, and ticketing.
 ###chinook: A music and media dataset, covering aspects like artists, albums, tracks, customers, employees, invoices, and playlists.
 ###sakila: A movie rental store operations dataset, covering areas including movies, actors, categories, inventory, rental records, customers, employees, and payment records.
 ###olist_ecommerce: An e-commerce dataset, covering various aspects such as customers, orders, products, payments, and reviews.
 ###uw_courses: A dataset from the University of Wisconsin-Madison, covering courses, course offerings, instructors, classrooms, and grade distributions.
These databases are independent of each other and not related.

2.Neither you nor the user are aware of the specific contents of the databases. Therefore, the table and column names in the user’s query might not be the actual column names in the databases. Always start by calling <get_column_info>, <get_table_info>, <get_all_table_names>, or <get_database_info> to retrieve the database structure information before querying specific data.
 For example, if you want to query the flights in the airlines database where the status is "Cancelled", first call <get_database_info> to retrieve the database structure, then call <get_column_info> to check the different values in the "status" column of the flights table to confirm that status='Cancelled' indicates a cancelled flight, and only then perform the specific query.

3.You can interact with the database using all available tools without needing to ask the user for permission.
"""

FILE_TOOL_PROMPT = """
File System-related Tools Notes:

1.Default Working Root Path: The default working root path is set to './'.
2.Unknown File Path: If the file path is not known in advance, always begin by using the <display_directory_tree> tool to retrieve a comprehensive list of directory contents and file paths.
3.Unknown File Information: If specific file information (e.g., column names) is unclear before performing queries or operations, start by utilizing the <read_file_contents> tool to examine the relevant file details.
"""

system_prompt_prefix = """Here is a list of functions in JSON format that you can invoke:\n"""
system_prompt_suffix = """. \nShould you decide to return the function call(s). \nPut it in the format of [func1(params_name=params_value, params_name2=params_value2...), func2(params)]\n\nNO other text MUST be included. \n"""

# 将转换函数和工具调用的处理封装为一个函数
def trans_openai_formate(tool_calls):
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

def call_id_save(tool_calls, temp_call_id_dict):
    for tool_call in tool_calls:
        tool_call_id = tool_call["id"]
        tool_call_name = tool_call["function"]["name"]
        temp_call_id_dict[tool_call_id] = tool_call_name
    return temp_call_id_dict

# def get_system_prompt(tools):
#     json_line_tool = json.dumps(tools, ensure_ascii=False)
#     system_prompt = system_prompt_prefix + json_line_tool + system_prompt_suffix

#     project_dir=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#     file_tools=load_tool_defines(f'{project_dir}/tools/defines/file_system_functions',recursive=True)
#     sql_tools=load_tool_defines(f'{project_dir}/tools/defines/database_functions',recursive=True)

    
#     if any([tool['name'] in file_tools for tool in tools]):
#         tool_response_prompt+=SQL_TOOL_PROMPT
#     if any([file_dirname in tool for tool in assistant_tools.keys()]):
#         # file工具中总是有这个工具，便于assistant获取相关信息
#         assistant_tools.update({f'{file_dirname}.{tool}':all_tools[f'{file_dirname}.{tool}'] for tool in fixed_file_tools})
#         tool_response_prompt+=FILE_TOOL_PROMPT
    

def process_file(input_file_path, output_file_path):
    with open(output_file_path, "w+") as output_file:
        with open(input_file_path, "r") as input_file:
            for in_line in input_file:
                json_line = json.loads(in_line)
                temp_call_id_dict = {}
                json_line_message = json_line["messages"]
                json_line_tool = json.dumps(json_line["tools"], ensure_ascii=False)
                # system_prompt中current_time被删除了
                toolace_system_prompt = system_prompt_prefix + json_line_tool + system_prompt_suffix

                toolace_utterance_list = []
                if json_line_message[0]["role"] == "system":
                    new_utterance = {"role": "system", "content": json_line_message[0]['content']+toolace_system_prompt}
                    toolace_utterance_list.append(new_utterance)
                    json_line_message = json_line_message[1:]
                for utterance in json_line_message:
                    if (utterance["role"] == "assistant") and ("tool_calls" in utterance):
                        # 对openAI工具调用进行数据格式转换
                        toolace_tool_format = trans_openai_formate(utterance["tool_calls"])
                        temp_call_id_dict = call_id_save(utterance["tool_calls"], temp_call_id_dict)
                        new_utterance = {"role": "assistant", "content": toolace_tool_format}
                        toolace_utterance_list.append(new_utterance)
                        continue
                    if utterance["role"] == "tool":
                        tool_call_id = utterance["tool_call_id"]
                        tool_call_name = temp_call_id_dict[tool_call_id]
                        tool_response = json.dumps({"name": tool_call_name, "result": utterance["content"]})
                        new_utterance = {"role": "tool", "content": tool_response}
                        toolace_utterance_list.append(new_utterance)
                        continue
                    else:
                        new_utterance = utterance
                        toolace_utterance_list.append(new_utterance)
                        continue
                output_file.write(json.dumps(toolace_utterance_list, ensure_ascii=False) + "\n")

def process_folder(input_folder_path, output_folder_path):
    # 获取文件夹中所有的文件
    file_list = os.listdir(input_folder_path)
    for file_name in file_list:
        # 构建完整的文件路径
        input_file_path = os.path.join(input_folder_path, file_name)
        if os.path.isfile(input_file_path):
            # 为输出文件创建相应路径
            output_file_path = os.path.join(output_folder_path, file_name)
            process_file(input_file_path, output_file_path)

# 主执行函数
if __name__ == "__main__":
    input_folder = "./generated_data/executable_tools/sampled2"  # 输入文件夹路径
    output_folder = "./generated_data/executable_tools/transfer_toolace_format"  # 输出文件夹路径
    
    # 确保输出文件夹存在
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    process_folder(input_folder, output_folder)
