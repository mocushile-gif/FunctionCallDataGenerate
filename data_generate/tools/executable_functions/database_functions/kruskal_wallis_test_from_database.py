import os
import sqlite3
import pandas as pd
from scipy.stats import kruskal
from dotenv import load_dotenv
from typing import List, Any
load_dotenv()

def kruskal_wallis_test_from_database(
    database_path: str,
    from_clause: str,
    category_col: str,
    value_col: str,
    where_clause: str = None,
    where_params: List[Any] = None,
    dropna: bool = True,
):
    """
    Perform Kruskal–Wallis H-test from an SQLite database.

    Parameters:
    - database_path (str): Path to the SQLite DB file.
    - from_clause (str): Table or JOIN clause.
    - category_col (str): Categorical column (will be converted to str even if numeric).
    - value_col (str): Numeric value column.
    - where_clause (str): Optional WHERE clause (without 'WHERE').
    - where_params (List[Any]): Parameters for WHERE clause.
    - dropna (bool): Whether to drop rows with nulls in category or value columns.

    Returns:
    - dict: Kruskal–Wallis test results.
    """

    if not os.path.exists(database_path):
        raise FileNotFoundError(f"Database not found at: {database_path}")

    query = f"SELECT {category_col}, {value_col} FROM {from_clause}"
    if where_clause:
        query += f" WHERE {where_clause}"

    conn = sqlite3.connect(database_path)
    try:
        df = pd.read_sql_query(query, conn, params=where_params or [])
    finally:
        conn.close()

    category_col=category_col.split('.')[-1]
    value_col=value_col.split('.')[-1]

    df[category_col] = df[category_col].astype(str)
    df[value_col] = pd.to_numeric(df[value_col], errors='coerce')

    if dropna:
        df.dropna(subset=[category_col, value_col], inplace=True)

    groups = [group[value_col].values for _, group in df.groupby(category_col)]
    group_names = list(df[category_col].unique())

    if len(groups) < 2:
        raise ValueError("Kruskal–Wallis test requires at least two groups.")
    if any(len(g) == 0 for g in groups):
        raise ValueError("One or more groups have no valid numeric data.")

    stat, p = kruskal(*groups)

    return {
        "method": "Kruskal–Wallis Test",
        "group_names": group_names,
        "num_groups": len(groups),
        "h_statistic": stat,
        "p_value": p,
        "significant": bool(p < 0.05)
    }

# 示例调用
if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    result = kruskal_wallis_test_from_database(
        database_path="./database/uw_courses.db",
        from_clause="schedules",
        category_col="mon",
        value_col="start_time",
        where_clause="start_time IS NOT NULL",
        dropna=True
    )
    print(result)
