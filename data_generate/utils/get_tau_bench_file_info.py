# -*- coding: utf-8 -*-
import pandas as pd
import os
import json
import sqlite3
from dotenv import load_dotenv
load_dotenv()

pd.set_option('display.max_rows', None)  # Display all rows
pd.set_option('display.max_columns', None)  # Display all columns
pd.set_option('display.max_colwidth', None)
def get_tau_bench_file_info(file_path: str, preview_rows: int = 5, work_dir=None):
    work_dir = work_dir if work_dir else os.environ.get('FILE_SYSTEM_PATH', './')
    os.chdir(work_dir)

    file_infos=[]
    with open(file_path,'r',encoding='utf-8') as f:
        data=json.load(f)
    
    for database_name, table_data in data.items():
        new_data=[]
        for id,v in table_data.items():
            new_item={}
            new_item['id']=id
            new_item.update(v)
            new_data.append(new_item)
        try:
            df = pd.DataFrame(new_data)
        except Exception as e:
            print(f"❌ Error converting '{database_name}' to DataFrame: {e}")
            continue

        file_infos.append({
            "database": database_name,
            "num_rows": len(df),
            "num_columns": len(df.columns),
            "column_names": df.columns.tolist(),
            "random_preview_rows": df.sample(n=min(preview_rows, len(df))).to_dict(orient="records")
        })
    return {"response": file_infos}



# Example Usage
if __name__ == "__main__":
    test_files = [
        ("/mnt/afs2/qinxinyi/function_call_data/data_generate/working_dir/tau_bench/airline.json",1),
        ("/mnt/afs2/qinxinyi/function_call_data/data_generate/working_dir/tau_bench/retail.json",1),
    ]

    for file_path, preview_rows in test_files:
        print(f"\n📄 File: {file_path} (Preview {preview_rows} rows)")
        result = get_file_info(file_path, preview_rows, f'{os.environ["PROJECT_DIR"]}/working_dir/file_system_new/')
        print("File Information:", json.dumps(result, indent=2, ensure_ascii=False))
