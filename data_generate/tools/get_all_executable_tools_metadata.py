import os
import json

def load_tool_defines(directory, recursive=False):
    """
    Read all JSON files in a given directory and return their contents as a list.

    Parameters:
    - directory (str): The path to the directory containing JSON files.
    - recursive (bool): Whether to search subdirectories recursively. Defaults to False.

    Returns:
    - A list of dictionaries representing the contents of each JSON file.
    - str: Error message if an exception occurs.
    """
    import data_generate
    project_dir = os.path.dirname(data_generate.__file__)
    project_dir=project_dir+'/tools/defines'
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
                            tool_key=f"{os.path.relpath(os.path.dirname(file_path),project_dir).replace(os.sep, '.')}.{json_content['name']}"
                            json_list[tool_key]={
                                "category": tool_key.split('.')[0],
                                "tool_name": tool_key.split('.')[1],
                                "tool_description": json_content['description'],
                                "api_define": json_content}
                        except Exception as e:
                            return f"Error when reading JSON file '{filename}': {str(e)}"
            if not recursive:
                break
        return json_list
    except Exception as e:
        return f"Error processing directory '{directory}': {str(e)}"

# Example usage
if __name__ == "__main__":
    tool_dict={}
    project_dir=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for folder in ['file_system_functions','python_functions','database_functions','api_functions']:
        defines=load_tool_defines(
            directory=f"{project_dir}/tools/defines/{folder}",
            recursive=True
        )
        print(defines)
        tool_dict.update(defines)
        print(f'{folder}:{len(defines)}')
    print(f'total self tools:{len(tool_dict)}\n')

    with open(f'{project_dir}/tools/xlam_rapidapi_tools_metadata.json','r',encoding='utf-8') as f:
        xlam_tools=json.load(f)
        print(f'xlam:{len(xlam_tools)}')
    for tool_name in xlam_tools.keys():
        tool_dict[xlam_tools[tool_name]['category']+'.'+tool_name]=xlam_tools[tool_name]
    
    with open(f'{project_dir}/tools/all_tools_metadata.json','w',encoding='utf-8') as out_f:
        json.dump(tool_dict,out_f,ensure_ascii=False,indent=4)
    print(f'total tools:{len(tool_dict)}')