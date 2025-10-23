import os
import sqlite3
import pandas as pd
from scipy.stats import spearmanr
from dotenv import load_dotenv
from typing import List, Any
load_dotenv()

def spearman_correlation_from_database(
    database_path: str,
    from_clause: str,
    x_col: str,
    y_col: str,
    where_clause: str = None,
    where_params: List[Any] = None,
    drop_na: bool = True,
):
    """
    Perform Spearman correlation test using data from a database.

    Parameters:
    - database_path (str): Path to the SQLite database.
    - from_clause (str): Table or JOIN clause.
    - x_col (str): Name of the first numeric column.
    - y_col (str): Name of the second numeric column.
    - where_clause (str): Optional WHERE clause (without 'WHERE').
    - where_params (List[Any]): Optional parameters for the WHERE clause.
    - drop_na (bool): Whether to drop rows with missing values.

    Returns:
    - dict: Spearman correlation result.
    """

    if not os.path.exists(database_path):
        raise FileNotFoundError(f"Database not found at: {database_path}")

    query = f"SELECT {x_col}, {y_col} FROM {from_clause}"
    if where_clause:
        query += f" WHERE {where_clause}"

    conn = sqlite3.connect(database_path)
    try:
        df = pd.read_sql_query(query, conn, params=where_params or [])
    finally:
        conn.close()

    x_col=x_col.split('.')[-1]
    y_col=y_col.split('.')[-1]
    if x_col not in df.columns or y_col not in df.columns:
        raise ValueError(f"Missing column(s): {x_col}, {y_col}")

    x = pd.to_numeric(df[x_col], errors='coerce')
    y = pd.to_numeric(df[y_col], errors='coerce')

    if drop_na:
        valid = x.notna() & y.notna()
        x, y = x[valid], y[valid]

    if len(x) == 0 or len(y) == 0:
        raise ValueError("No valid numeric data found for Spearman correlation.")

    r, p = spearmanr(x, y)

    return {
        "method": "Spearman Correlation",
        "x_column": x_col,
        "y_column": y_col,
        "sample_size": len(x),
        "r": r,
        "p_value": p,
        "significant": p < 0.05
    }

# 示例调用
if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    result = spearman_correlation_from_database(
        database_path="./database/uw_courses.db",
        from_clause="schedules",
        x_col="start_time",
        y_col="end_time",
        where_clause="start_time IS NOT NULL AND end_time IS NOT NULL",
        drop_na=True
    )
    print(result)
