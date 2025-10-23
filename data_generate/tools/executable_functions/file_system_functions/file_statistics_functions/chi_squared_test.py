import pandas as pd
import json
from scipy.stats import chi2_contingency
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

def chi_squared_test(file_path, col1, col2, sheet_name=0):

    df = load_data(file_path, sheet_name)
    contingency_table = pd.crosstab(df[col1], df[col2])
    if contingency_table.empty or contingency_table.shape[0] < 2 or contingency_table.shape[1] < 2:
        raise ValueError("❌ Chi-squared test requires at least a 2x2 contingency table.")

    chi2, p, dof, expected = chi2_contingency(contingency_table)

    return {
        "method": "Chi-squared Test",
        "chi2_statistic": chi2,
        "p_value": p,
        "degrees_of_freedom": dof,
        "significant": bool(p < 0.05)
    }

if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    file_path = "./excel_data/AmazingMartEU2.xlsx"
    sheet_name = "OrderBreakdown"
    col1 = "Category"
    col2 = "Sub-Category"

    result = chi_squared_test(file_path, col1, col2, sheet_name)
    print(result)
