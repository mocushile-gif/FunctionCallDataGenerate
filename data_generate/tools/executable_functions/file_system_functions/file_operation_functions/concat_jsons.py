import json
import os
from glob import glob
from dotenv import load_dotenv
load_dotenv()

def concat_jsons(pattern, save_dir='./', file_name='concat_data.json'):
    """
    Merge multiple JSON files that match a pattern into one.

    Parameters:
    - pattern: File search pattern (e.g., 'data/*.json').
    - save_dir: Directory to save the merged file (default: same as first matched file).
    - file_name: Name of the merged file (default: concat_data.json).

    Returns:
    - A message indicating success or error details.
    """

    file_paths = glob(pattern)
    
    if not file_paths:
        return "No files matched the pattern."
    
    merged_data = []
    for file_path in file_paths:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                merged_data.extend(data)
            elif isinstance(data, dict):
                merged_data.append(data)
    
    if not save_dir:
        save_dir = os.path.dirname(file_paths[0])
    else:
        if not os.path.exists(save_dir):
            os.mkdir(save_dir)
    
    save_path = os.path.join(save_dir, file_name)
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, indent=4, ensure_ascii=False)
    
    file_list = "\n".join([os.path.basename(path) for path in file_paths])
    message = (
        f"Concat JSON files successful!\n"
        f"Merged files:\n{file_list}\n"
        f"Saved to: {save_path}"
    )
    return message

# 示例调用
if __name__ == '__main__':
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    result = concat_jsons('./json_data/*.json')
    print(result)
