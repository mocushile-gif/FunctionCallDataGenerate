import json
from typing import Any, List, Union
import shutil
import os
from dotenv import load_dotenv
load_dotenv()

def extract_data_from_json(file_path: str, keys: Union[str, List[str]], limit: int = None, output_path: str = ''):

    """
    从 JSON 文件中提取特定字段的数据。

    参数:
    - file_path (str): JSON 文件的路径。
    - keys (Union[str, List[str]]): 要提取的字段，可以是单个字段名（str）或多个字段名（list）。
    - limit (int, optional): 限制返回数据的数量。如果为 None，则提取所有数据。

    返回:
    - Dict[str, Any]: 包含提取结果或错误信息。
    """

    # ========== 新增：后缀名检测 ==========
    if not file_path.endswith(".json") and not file_path.endswith(".jsonl"):
        return {"error": "Unsupported file format. Only .json and .jsonl files are allowed."}

    # 检查 keys 类型
    if isinstance(keys, str):
        keys = [keys]

    if not keys or not isinstance(keys, list):
        return {"error": "Keys must be a non-empty string or list of strings."}

    # 打开并读取 JSON 文件
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            if file_path.endswith(".json"):
                data = json.load(f)
            else:  # 处理 jsonl
                data = [json.loads(line) for line in f if line.strip()]
    except Exception as e:
        return {"error": f"Failed to load JSON: {str(e)}"}

    # 确保数据格式正确
    if isinstance(data, dict):
        data = [data]
    elif not isinstance(data, list):
        return {"error": "The JSON file must contain an object or a list of objects."}

    # 提取字段数据
    extracted_data = []
    for key in keys:
        if not any([item.get(key,None) for item in data]):
            return {"error": f"The JSON file does not contain the key: {key}."}
    for item in data:
        if isinstance(item, dict):
            extracted_data.append({key: item.get(key,None) for key in keys})
        else:
            return {"error": "Each item in the JSON file must be a dictionary."}

    # 应用 limit
    if limit is not None and isinstance(limit, int) and limit > 0:
        result_df = extracted_data[:limit]

    if output_path:
        out_ext = os.path.splitext(output_path)[1].lower()
        try:
            if out_ext == ".csv":
                result_df.to_csv(output_path, index=False, encoding="utf-8")
            elif out_ext == ".xlsx":
                result_df.to_excel(output_path, index=False, engine='openpyxl')
            elif out_ext == ".json":
                result_df.to_json(output_path, orient="records", force_ascii=False, indent=2)
            elif out_ext == ".jsonl":
                with open(output_path, "w", encoding="utf-8") as f:
                    for record in result_df.to_dict(orient="records"):
                        f.write(json.dumps(record, ensure_ascii=False) + "\n")
            else:
                return {"error": f"Unsupported output file format: {out_ext}"}
            result_info["saved_to"] = output_path
        except Exception as e:
            return {"error": f"Failed to save output: {str(e)}"}

    result_info={}
    result_info["row_count"]=len(result_df)
    result_info["result"]=result_df

    return result_info

# Example usage
if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    file_path = './json_data/Top_1000_Github_repositories_for_popular_topics/NextJS.json'
    keys = ['stars']
    try:
        extracted = extract_data_from_json(file_path, keys, limit=10)
        print(f"Extracted data:\n{json.dumps(extracted)}")
    except Exception as e:
        print(f"Error: {e}")
