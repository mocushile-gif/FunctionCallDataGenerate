import pandas as pd
import json
from scipy.stats import shapiro, normaltest
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

def run_normality_test(data):
    n = len(data)
    if n > 5000:
        stat, p = normaltest(data)
        method = "D’Agostino and Pearson"
    else:
        stat, p = shapiro(data)
        method = "Shapiro-Wilk"
    return method, stat, p

def normality_test(file_path, numeric_cols=None, sheet_name=0):

    df = load_data(file_path, sheet_name)
    if numeric_cols is None:
        numeric_cols = df.select_dtypes(include='number').columns.tolist()

    results = []
    for col in numeric_cols:
        data = pd.to_numeric(df[col], errors='coerce').dropna()
        if len(data) < 3:
            results.append({
                "column": col,
                "error": "Not enough valid numeric data (n < 3)."
            })
            continue
        method, stat, p = run_normality_test(data)
        if data.max() == data.min():
            results.append({
                "column": col,
                "sample_size": len(data),
                "error": "All values are identical. Cannot perform normality test."
            })
            continue
        results.append({
            "column": col,
            "sample_size": len(data),
            "method": method,
            "statistic": stat,
            "p_value": p,
            "normal": bool(p >= 0.05)
        })

    return {
        "test_type": "Normality Test",
        "results": results
    }

if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    file_path = "./excel_data/AmazingMartEU2.xlsx"
    sheet_name = "OrderBreakdown"
    numeric_cols = ["Sales", "Quantity"]

    result = normality_test(file_path, numeric_cols, sheet_name)
    print(result)
