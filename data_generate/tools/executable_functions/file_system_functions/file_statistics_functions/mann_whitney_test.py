import pandas as pd
import json
from scipy.stats import mannwhitneyu
import os
from dotenv import load_dotenv
load_dotenv()

def load_data(file_path, sheet_name=0):
    if file_path.endswith(".csv"):
        for enc in ['utf-8', 'ISO-8859-1', 'GBK', 'gb2312']:
            try:
                return pd.read_csv(file_path, encoding=enc)
            except UnicodeDecodeError:
                continue
    elif file_path.endswith((".xls", ".xlsx")):
        return pd.read_excel(file_path, sheet_name=sheet_name)
    elif file_path.endswith(".json"):
        return pd.read_json(file_path)
    elif file_path.endswith(".jsonl"):
        with open(file_path, "r", encoding="utf-8") as f:
            return pd.DataFrame([json.loads(line) for line in f])
    else:
        raise ValueError("Unsupported file format.")

def mann_whitney_test(file_path, category_col, value_col, group_names=None, sheet_name=0):

    df = load_data(file_path, sheet_name)

    if category_col not in df.columns or value_col not in df.columns:
        raise ValueError("Specified columns not found in dataset.")

    df[category_col] = df[category_col].astype(str)
    df[value_col] = pd.to_numeric(df[value_col], errors='coerce')
    df = df[[category_col, value_col]].dropna()

    if group_names:
        df = df[df[category_col].isin(group_names)]
        if df[category_col].nunique() != 2:
            raise ValueError("Mann–Whitney test requires exactly two groups.")
    else:
        if df[category_col].nunique() != 2:
            raise ValueError("Please specify two groups explicitly when there are more than two.")

    groups = [group[value_col].values for _, group in df.groupby(category_col)]
    stat, p = mannwhitneyu(*groups, alternative='two-sided')

    return {
        "method": "Mann–Whitney U Test",
        "group_names": list(df[category_col].unique()),
        "u_statistic": stat,
        "p_value": p,
        "significant": bool(p < 0.05)
    }

if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    file_path = "./excel_data/AmazingMartEU2.xlsx"
    sheet_name = "OrderBreakdown"
    category_col = "Category"
    value_col = "Sales"
    group_names = ["Office Supplies", "Technology"]  # 指定两个组

    result = mann_whitney_test(file_path, category_col, value_col, group_names, sheet_name)
    print(result)
