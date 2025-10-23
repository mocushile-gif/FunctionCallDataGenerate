import pandas as pd
import sqlite3
import os
import json
from dotenv import load_dotenv
load_dotenv()
pd.set_option('display.max_rows', None)  # Display all rows
pd.set_option('display.max_columns', None)  # Display all columns
pd.set_option('display.max_colwidth', None)

def query_file_with_sql(file_path: str,
                        sql_query: str,
                        table_name: str = "data",
                        sheet_name: str or int = 0,
                        output_path: str = ''):
    """
    在文件（CSV, Excel, JSON, JSONL）上执行类SQL查询，并返回结果与行数，可选保存查询结果。

    参数:
    - file_path (str): 输入文件路径
    - sql_query (str): 要执行的 SQL 查询语句
    - table_name (str): SQLite 临时表的名称，默认 "data"
    - sheet_name (str or int): Excel 工作表名称或索引，仅适用于 Excel 文件
    - output_path (str): 可选，查询结果保存路径（支持 .csv, .xlsx, .json, .jsonl）

    返回:
    - dict: 包含行数、结果（DataFrame），若有保存则包含保存路径
    """

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    file_extension = os.path.splitext(file_path)[1].lower()

    try:
        if file_extension in [".xls", ".xlsx"]:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
        elif file_extension == ".csv":
            encodings_to_try = ['utf-8', 'ISO-8859-1', 'GBK', 'gb2312']
            for encoding in encodings_to_try:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise UnicodeDecodeError("Failed to decode CSV with common encodings")
        elif file_extension == ".json":
            df = pd.read_json(file_path)
        elif file_extension == ".jsonl":
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = [json.loads(line.strip()) for line in f]
            df = pd.DataFrame(lines)
        else:
            return {"error": f"Unsupported file type: {file_extension}"}
    except Exception as e:
        return {"error": f"Failed to load file: {str(e)}"}

    # 执行SQL查询
    try:
        with sqlite3.connect(":memory:") as conn:
            df.to_sql(table_name, conn, index=False, if_exists="replace")
            result_df = pd.read_sql_query(sql_query, conn)
    except Exception as e:
        return {"error": f"SQL execution error: {str(e)}"}

    result_info={}
    # 可选保存结果
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

    result_info["row_count"]=len(result_df)
    result_info["result"]=result_df

    return result_info


# 示例用法
if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    file_path = "./csv_data/high_popularity_spotify_data.csv"
    query = "SELECT track_name, playlist_genre, track_album_release_date FROM data WHERE track_popularity > 80"
    # output_file = "filtered_result.csv"
    # file_path = "./json_data/Books.json"
    # query = "SELECT * FROM data limit 1"

    result = query_file_with_sql(file_path, query)
    print(result)
