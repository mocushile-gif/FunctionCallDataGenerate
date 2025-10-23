import pandas as pd
import json
from scipy.stats import f_oneway
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

def anova_test(file_path, category_col, value_col, sheet_name=0):

    df = load_data(file_path, sheet_name)

    # 检查列是否存在
    if category_col not in df.columns:
        raise ValueError(f"Column '{category_col}' not found in the data.")
    if value_col not in df.columns:
        raise ValueError(f"Column '{value_col}' not found in the data.")

    df[category_col] = df[category_col].astype(str)
    df[value_col] = pd.to_numeric(df[value_col], errors='coerce')

    # 先做数值有效性检查
    if df[value_col].dropna().empty:
        raise ValueError(f"{value_col} contains no valid numeric data.")

    grouped = df[[category_col, value_col]].dropna().groupby(category_col)
    group_names = list(grouped.groups.keys())
    groups = [group[value_col].values for _, group in grouped]

    if len(groups) < 2:
        raise ValueError("ANOVA requires at least two groups.")
    if any(len(g) == 0 for g in groups):
        raise ValueError("Each group must contain at least one valid numeric value.")

    f_stat, p = f_oneway(*groups)

    return {
        "method": "One-way ANOVA",
        "group_names": group_names,
        "num_groups": len(groups),
        "f_statistic": f_stat,
        "p_value": p,
        "significant": bool(p < 0.05)
    }


if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    file_path = "./excel_data/AmazingMartEU2.xlsx"
    sheet_name = "OrderBreakdown"
    category_col = "Category"   # 类别列
    value_col = "Sales"       # 数值列

    result = anova_test(file_path, category_col, value_col, sheet_name)
    print(result)
