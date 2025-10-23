import os
import sqlite3
import pandas as pd
from scipy.stats import shapiro, normaltest
from typing import List, Any
import numpy as np
from dotenv import load_dotenv
load_dotenv()

def run_normality_test(data):
    n = len(data)
    if n > 5000:
        stat, p = normaltest(data)
        method = "D’Agostino and Pearson"
    else:
        stat, p = shapiro(data)
        method = "Shapiro-Wilk"
    return method, stat, p

def normality_test_from_database(
    database_path: str,
    from_clause: str,
    numeric_cols: List[str],
    where_clause: str = None,
    where_params: List[Any] = None,
    use_log_transform: bool = False,
):
    """
    Run normality test for numeric columns from SQLite database.

    Parameters:
    - database_path (str): Path to SQLite DB.
    - from_clause (str): Table or JOIN clause.
    - numeric_cols (List[str]): Columns to test.
    - where_clause (str): Optional WHERE clause.
    - where_params (List[Any]): WHERE clause parameters.
    - use_log_transform (bool): Whether to apply log1p before testing.

    Returns:
    - dict: Test results.
    """

    if not os.path.exists(database_path):
        raise FileNotFoundError(f"Database not found at: {database_path}")

    cols = ", ".join(numeric_cols)
    query = f"SELECT {cols} FROM {from_clause}"
    if where_clause:
        query += f" WHERE {where_clause}"

    conn = sqlite3.connect(database_path)
    try:
        df = pd.read_sql_query(query, conn, params=where_params or [])
    finally:
        conn.close()

    results = []
    for col in numeric_cols:
        col=col.split('.')[-1]
        if col not in df.columns:
            results.append({"column": col, "error": "Column not found in result."})
            continue

        data = pd.to_numeric(df[col], errors='coerce').dropna()

        if len(data) < 3:
            results.append({
                "column": col,
                "error": "Not enough valid numeric data (n < 3)."
            })
            continue

        if use_log_transform:
            data = data[data > 0]  # log1p 只能用于正数
            data = pd.Series(np.log1p(data))

        if data.max() == data.min():
            results.append({
                "column": col,
                "sample_size": len(data),
                "error": "All values are identical. Cannot perform normality test."
            })
            continue
        method, stat, p = run_normality_test(data)
        results.append({
            "column": col,
            "sample_size": len(data),
            "method": method + (" (log-transformed)" if use_log_transform else ""),
            "statistic": stat,
            "p_value": p,
            "normal": bool(p >= 0.05)
        })

    return {
        "test_type": "Normality Test",
        "use_log_transform": use_log_transform,
        "results": results
    }

# 示例用法
if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    result = normality_test_from_database(
        database_path="./database/BowlingLeague.sqlite",
        from_clause="Bowlers b",
        numeric_cols=["b.BowlerTotalPins", "b.BowlerGamesBowled"],
        use_log_transform=True
    )
    print(result)
