import pandas as pd
import json
from scipy.stats import spearmanr
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

def spearman_correlation_test(file_path, x_col, y_col, sheet_name=0):
    df = load_data(file_path, sheet_name)
    x = pd.to_numeric(df[x_col], errors='coerce')
    y = pd.to_numeric(df[y_col], errors='coerce')
    valid = x.notna() & y.notna()
    x, y = x[valid], y[valid]

    if len(x) == 0 or len(y) == 0:
        raise ValueError("No valid numeric data found for Spearman correlation.")

    r, p = spearmanr(x, y)
    return {
        "method": "Spearman Correlation",
        "r": r,
        "p_value": p,
        "significant": bool(p < 0.05)
    }

if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    file_path = "./excel_data/AmazingMartEU2.xlsx"
    sheet_name = "OrderBreakdown"
    x_col = "Quantity"
    y_col = "Sales"

    result = spearman_correlation_test(file_path, x_col, y_col, sheet_name)
    print(result)
