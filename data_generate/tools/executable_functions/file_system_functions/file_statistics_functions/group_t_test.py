import pandas as pd
import json
from scipy.stats import ttest_ind
import os
from dotenv import load_dotenv
load_dotenv()

def load_data(file_path, sheet_name=0):
    if file_path.endswith(".csv"):
        encodings = ['utf-8', 'ISO-8859-1', 'GBK', 'gb2312']
        for enc in encodings:
            try:
                return pd.read_csv(file_path, encoding=enc)
            except UnicodeDecodeError:
                continue
    elif file_path.endswith((".xls", ".xlsx")):
        return pd.read_excel(file_path, sheet_name=sheet_name)
    elif file_path.endswith(".json"):
        return pd.read_json(file_path)
    elif file_path.endswith(".jsonl"):
        with open(file_path, 'r', encoding='utf-8') as f:
            return pd.DataFrame([json.loads(line) for line in f])
    else:
        raise ValueError("Unsupported file format.")

def group_t_test(file_path, category_col, value_col, sheet_name=0, group_names=None):
    
    df = load_data(file_path, sheet_name)

    # 检查列是否存在
    if category_col not in df.columns:
        raise ValueError(f"Column '{category_col}' not found in the data.")
    if value_col not in df.columns:
        raise ValueError(f"Column '{value_col}' not found in the data.")
        
    df[category_col] = df[category_col].astype(str)
    df[value_col] = pd.to_numeric(df[value_col].str.replace(',', ''), errors='coerce')

    # 如果指定了 group_names
    if group_names:
        if not isinstance(group_names, (list, tuple)) or len(group_names) != 2:
            raise ValueError("group_names must be a list or tuple of exactly two group values.")
        df = df[df[category_col].isin(group_names)]
        actual_groups = df[category_col].unique()
        if len(actual_groups) != 2:
            raise ValueError(f"One or both specified groups not found in data: {group_names}")
    else:
        actual_groups = df[category_col].dropna().unique()
        if len(actual_groups) != 2:
            raise ValueError("t-test requires exactly two groups, or specify group_names to select.")

    # 先做数值有效性检查
    if df[value_col].dropna().empty:
        raise ValueError(f"{value_col} contains no valid numeric data.")

    
    groups = df[[category_col, value_col]].dropna().groupby(category_col)
    values = [group[value_col].values for _, group in groups]

    stat, p = ttest_ind(*values)

    return {
        "method": "Independent t-test",
        "group_names": list(groups.groups.keys()),
        "group_1_size": len(values[0]),
        "group_2_size": len(values[1]),
        "t_statistic": stat,
        "p_value": p,
        "significant": bool(p < 0.05)
    }


if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    file_path="./json_data/Top 100 Largest Banks.json"
    # sheet_name="OrderBreakdown"
    category_col="Bank Name"
    value_col="Total Assets (2023, US$ billion)"
    group_names=["Industrial and Commercial Bank of China","Agricultural Bank of China"]

    result = group_t_test(file_path, category_col, value_col, group_names=group_names)
    print(result)