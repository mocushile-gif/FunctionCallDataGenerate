import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv
import pandas as pd
load_dotenv()


def load_data(file_path, sheet_name=0):
    if file_path.endswith(".csv"):
        encodings_to_try = ['utf-8', 'ISO-8859-1', 'GBK', 'gb2312']
        for encoding in encodings_to_try:
            try:
                df = pd.read_csv(file_path, encoding=encoding)
                break
            except UnicodeDecodeError:
                continue
    elif file_path.endswith((".xls", ".xlsx")):
        df = pd.read_excel(file_path, sheet_name=sheet_name)
    elif file_path.endswith(".json"):
        df = pd.read_json(file_path)
    elif file_path.endswith(".jsonl"):
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = [json.loads(line.strip()) for line in f]
        df = pd.DataFrame(lines)
    else:
        raise ValueError("Unsupported file format. Please use a .csv, .xls, or .xlsx file.")
    return df

def check_file_null_values(
    file_path=None,
    sheet_name: str or int = 0,
    save_to_file: str = None
):
    """
    Check NULL value counts for each column in a table of an SQLite database.

    Parameters:
    - file_path (str): Optional path to a file for loading data.
    - sheet_name (str or int): Sheet name or index for Excel files.
    - save_to_file (str): If set, saves the result to a .csv or .xlsx file.

    Returns:
    - pd.DataFrame: A DataFrame with column names, null counts, and % missing.
    """

    df = load_data(file_path, sheet_name)

    total_rows = len(df)
    null_counts = df.isnull().sum()
    percent_missing = (null_counts / total_rows * 100).round(2)

    result = pd.DataFrame({
        "Column": null_counts.index,
        "Null Count": null_counts.values,
        "Missing %": percent_missing.values,
        "Total Rows": total_rows
    })

    # Save if needed
    if save_to_file:
        os.makedirs(os.path.dirname(save_to_file) or ".", exist_ok=True)
        if save_to_file.endswith(".csv"):
            result.to_csv(save_to_file, index=False)
        elif save_to_file.endswith(".xlsx"):
            result.to_excel(save_to_file, index=False)
        elif save_to_file.endswith(".json"):
            result.to_json(save_to_file, orient="records", force_ascii=False, indent=2)
        elif save_to_file.endswith(".jsonl"):
            result.to_json(save_to_file, orient="records", force_ascii=False, lines=True)
        else:
            raise ValueError("Unsupported file format. Use .csv, .xlsx, .json, or .jsonl")

    return result

# Example Usage
if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    result = check_file_null_values(
        file_path="./excel_data/达人数据.xlsx",
        sheet_name="达人筛选",
        save_to_file="null_values.json"
    )

    print(result)