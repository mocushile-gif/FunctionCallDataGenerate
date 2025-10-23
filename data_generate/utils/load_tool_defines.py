import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from tools.executable_functions.api_functions import *
from tools.executable_functions.file_system_functions import *
from tools.executable_functions.database_functions import *
from tools.executable_functions.python_functions import *
from typing import List, Dict, Any, Optional, Union
import re
import inspect

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

# Example usage
if __name__ == "__main__":
    tool_defines = load_tool_defines(
        directory=f"{os.environ['HOME_DIR']}/function_call_data/data_generate/tools/defines/api_functions",
        recursive=True,
    )
    print(tool_defines)