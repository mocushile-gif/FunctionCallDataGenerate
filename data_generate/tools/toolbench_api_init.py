import re
import shutil
def standardize_category(category):
    save_category = category.replace(" ", "_").replace(",", "_").replace("/", "_")
    while " " in save_category or "," in save_category:
        save_category = save_category.replace(" ", "_").replace(",", "_")
    save_category = save_category.replace("__", "_")
    return save_category

def standardize(string):
    res = re.compile("[^\\u4e00-\\u9fa5^a-z^A-Z^0-9^_]")
    string = res.sub("_", string)
    string = re.sub(r"(_)\1+","_", string).lower()
    while True:
        if len(string) == 0:
            return string
        if string[0] == "_":
            string = string[1:]
        else:
            break
    while True:
        if len(string) == 0:
            return string
        if string[-1] == "_":
            string = string[:-1]
        else:
            break
    if string[0].isdigit():
        string = "get_" + string
    return string

def change_name(name):
    change_list = ["from", "class", "return", "false", "true", "id", "and"]
    if name in change_list:
        name = "is_" + name
    return name

unmapping_type={}
def api_json_to_openai_json(api_json):
        description_max_length=512
        template =     {
            "name": "",
            "description": "",
            "parameters": {
                "type": "object",
                "properties": {
                },
                "required": []
            }
        }
        
        map_type = {
            "ENUM": "string",
            "NUMBER": "number",
            "STRING": "string",
            "BOOLEAN": "boolean",
            "ARRAY": "array",
            "LIST": "array",
            "string": "string",
            "FLOAT": "number",
            'GEOPOINT (latitude, longitude)': "number"
        }

        valid_types = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict,
            "null": type(None)
        }

        pure_api_name = change_name(standardize(api_json["name"]))
        template["name"] = pure_api_name[-64:]
        template["description"] =api_json['description'][:description_max_length]
        parameters = []
        if ("required_parameters" in api_json.keys() or "optional_parameters" in api_json.keys()) and len(api_json["required_parameters"]+api_json["optional_parameters"]) > 0:
            for para in api_json["required_parameters"]:
                name = standardize(para["name"])
                name = change_name(name)
                parameters.append(name)
                # if para['default'].lower()=='false' or para['default'].lower()=='true':
                #     para['type']='boolean'
                #     para["description"]=para["description"].replace("'false'",'false').replace("'False'",'false')
                if para["type"] in map_type:
                    param_type = map_type[para["type"]]
                else:
                    unmapping_type[str(para["type"])]=para
                    param_type = "string"
                prompt = {
                    "type":param_type,
                    "description":para["description"][:description_max_length],
                }
                if para["type"]=="ENUM" and "test_endpoint" in api_json and "detail" in api_json["test_endpoint"]:
                    for detail in api_json["test_endpoint"]["detail"]:
                        if name in detail['loc']:
                            try:
                                prompt["enum"]=detail["ctx"]["enum_values"]
                            except:
                                pass

                default_value = para['default']

                if not isinstance(default_value, valid_types.get(param_type)) and len(str(default_value)) != 0:
                    try:
                        target_type=valid_types.get(param_type)
                        if target_type:
                            if param_type=="number":
                                default_value = float(default_value)
                            else:
                                default_value = target_type(default_value)
                    except:
                        # print(f"default value {default_value} cannot match param_type {param_type}, removed.")
                        default_value=''

                if isinstance(default_value, valid_types.get(param_type)) and len(str(default_value)) != 0:    
                    prompt = {
                        "type":param_type,
                        "description":para["description"][:description_max_length],
                        "default": default_value
                    }
                else:
                    prompt = {
                        "type":param_type,
                        "description":para["description"][:description_max_length]
                    }

                template["parameters"]["properties"][name] = prompt
                if name not in template["parameters"]["required"]:
                    template["parameters"]["required"].append(name)
            for para in api_json["optional_parameters"]:
                name = standardize(para["name"])
                name = change_name(name)
                parameters.append(name)
                if para["type"] in map_type:
                    param_type = map_type[para["type"]]
                else:
                    unmapping_type[str(para["type"])]=para
                    param_type = "string"

                default_value = para['default']
                if not isinstance(default_value, valid_types.get(param_type)) and len(str(default_value)) != 0:
                    try:
                        target_type=valid_types.get(param_type)
                        if target_type:
                            if param_type=="number":
                                default_value = float(default_value)
                            else:
                                default_value = target_type(default_value)
                    except:
                        # print(f"default value {default_value} cannot match param_type {param_type}, removed")
                        default_value=''

                if isinstance(default_value, valid_types.get(param_type)) and len(str(default_value)) != 0:  
                    prompt = {
                        "type":param_type,
                        "description":para["description"][:description_max_length],
                        "default": default_value
                    }
                else:
                    prompt = {
                        "type":param_type,
                        "description":para["description"][:description_max_length]
                    }
                if param_type=='array':
                    prompt["items"]={}
                    
                if para["type"]=="ENUM" and "test_endpoint" in api_json and "detail" in api_json["test_endpoint"]:
                    for detail in api_json["test_endpoint"]["detail"]:
                        if para["name"] in detail['loc']:
                            try:
                                prompt["enum"]=detail["ctx"]["enum_values"]
                            except:
                                pass
                template["parameters"]["properties"][name] = prompt
                # template["parameters"]["optional"].append(name)
        return template, pure_api_name, parameters

import os
import json
from tqdm import tqdm
# For pipeline environment preparation
def get_white_list(tool_root_dir):
    # print(tool_root_dir)
    white_list_dir = os.path.join(tool_root_dir)
    white_list = {}
    api_metadata={}
    for cate in tqdm(os.listdir(white_list_dir)):
        if not os.path.isdir(os.path.join(white_list_dir,cate)):
            continue
        for file in os.listdir(os.path.join(white_list_dir,cate)):
            if not file.endswith(".json"):
                continue
            standard_tool_name = file.split(".")[0]
            # print(standard_tool_name)
            with open(os.path.join(white_list_dir,cate,file)) as reader:
                js_data = json.load(reader)
            tool_name = js_data["tool_name"]
            api_list = js_data["api_list"]
            tool_description=js_data["tool_description"]
            for api in api_list:
                openai_api_define,pure_api_name,parameters=api_json_to_openai_json(api)
                if pure_api_name not in api_metadata:
                    api_metadata[pure_api_name]=[{"category":cate,"tool_name":standard_tool_name,"tool_description":tool_description,"api_name":pure_api_name,"parameters":parameters,"api_define":openai_api_define}]
                else:
                    api_metadata[pure_api_name].append({"category":cate,"tool_name":standard_tool_name,"tool_description":tool_description,"api_name":pure_api_name,"parameters":parameters,"api_define":openai_api_define})
            # white_list[standardize(origin_tool_name)] = {"category":cate, "standard_tool_name": standard_tool_name,"api_list":api_list}
    return api_metadata

# 把xlam的工具筛选出来
api_metadata=get_white_list('/mnt/nvme0/qinxinyi/StableToolBench/server/tools')
# print(white_list['time_zone_api'])

new_api_metadata={}
# 定义路径
path_rapidapi = "./tools/defines/xlam_rapidapi_tools/"
path_python = "./tools/defines/xlam_python_tools/"
# 重置文件夹
for path in [path_rapidapi]:
    if os.path.exists(path):
        shutil.rmtree(path)  # 删除文件夹及其内容
    os.mkdir(path)  # 重新创建文件夹

other_executable_tools={}
for file in os.listdir('./tools/defines/file_system_functions'):
    if file.endswith(".json"):
        other_executable_tools[file[:-5]]=1
for file in os.listdir('./tools/defines/python_functions'):
    if file.endswith(".json"):
        other_executable_tools[file[:-5]]=1
for file in os.listdir('./tools/defines/database_functions'):
    if file.endswith(".json"):
        other_executable_tools[file[:-5]]=1
        
with open('./tools/xlam_tools.json','r',encoding='utf-8') as f:
    for item in f:
        tool=json.loads(item)
        flag=False

        if tool['name'] in api_metadata:
            metadatas=api_metadata[tool["name"]]
            for metadata in metadatas:
                if all([parameter in metadata['parameters'] for parameter in list(tool["parameters"].keys())]):
                    if tool['name'] in other_executable_tools:
                        print(f'与其他可执行工具重名:{tool["name"]},请修改这些工具名')
                        
                    with open(f'{path_rapidapi}/{tool["name"]}.json','w',encoding='utf-8') as new_f:
                        # json.dump(tool,new_f,ensure_ascii=False,indent=4)
                        new_api_description=tool['description'] if len(tool['description'])>len(metadata['api_define']['description']) else metadata['api_define']['description']
                        new_description=f"This is a sub-function API for tool {metadata['tool_name']}.\nTool description: {metadata['tool_description']}\nAPI description: {new_api_description}"
                        metadata['api_define']['description']=new_description
                        
                        for parameter in list(metadata['api_define']['parameters']['properties'].keys()):
                            original_parameter_description=metadata['api_define']['parameters']['properties'][parameter]['description'] 
                            if parameter in tool['parameters']:
                                apigen_parameter_description=tool['parameters'][parameter]['description']
                                new_parameter_description= original_parameter_description if len(original_parameter_description)>len(apigen_parameter_description) else apigen_parameter_description
                                metadata['api_define']['parameters']['properties'][parameter]['description']=new_parameter_description
                            elif parameter not in metadata['api_define']['parameters']['required']:
                                print(f"remove no required and non-xlam paramter {parameter}")
                                del metadata['api_define']['parameters']['properties'][parameter]
                            # print('original_parameter_description'+metadata['api_define']['parameters']['properties'][parameter]['description'])
                            # print('apigen_parameter_description'+tool['parameters'][parameter]['description'])
                            # print('\n\n')
                        json.dump(metadata['api_define'],new_f,ensure_ascii=False,indent=4)
                    new_api_metadata[tool['name']]={"category":metadata["category"],
                                                    "tool_name":metadata["tool_name"],
                                                    "tool_description":metadata["tool_description"],
                                                    "api_define":metadata["api_define"]}
                    flag=True
                    break
    print(f"无法匹配的数据类型：{unmapping_type}。统一设置为string。")
        # if tool['name'] not in api_metadata or flag==False:
        #     with open(f'{path_python}/{tool["name"]}.json','w',encoding='utf-8') as new_f:
        #         json.dump(tool,new_f,ensure_ascii=False,indent=4)
            
with open('./tools/xlam_rapidapi_tools_metadata.json','w',encoding='utf-8') as new_f:
    json.dump(new_api_metadata,new_f,ensure_ascii=False,indent=4)