import os
import sqlite3
import pandas as pd
import numpy as np
from scipy.stats import mannwhitneyu
from typing import List, Any
from dotenv import load_dotenv
load_dotenv()

def mann_whitney_test_from_database(
    database_path: str,
    from_clause: str,
    category_col: str,
    value_col: str,
    group_names: List[str] = None,
    where_clause: str = None,
    where_params: List[Any] = None,
    sort_group_order: bool = False,
    show_summary_stats: bool = False,
):
    """
    Perform Mann–Whitney U test using SQLite database.

    Parameters:
    - database_path: Path to SQLite database.
    - from_clause: Table or join clause for SELECT.
    - category_col: Grouping column (even if int, will be treated as str).
    - value_col: Numeric value column.
    - group_names: Optional list of exactly two group values.
    - where_clause: Optional WHERE clause (without 'WHERE').
    - where_params: Parameters for WHERE clause.
    - sort_group_order: Sort group names before analysis.
    - show_summary_stats: Whether to include group summary stats.

    Returns:
    - dict: Mann–Whitney test results.
    """

    if not os.path.exists(database_path):
        raise FileNotFoundError(f"Database not found: {database_path}")

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
    # 列检查与处理
    if category_col not in df.columns or value_col not in df.columns:
        raise ValueError(f"Missing columns: {category_col}, {value_col}")

    df[category_col] = df[category_col].astype(str)  # 即使是整数列，也转换为字符串以确保稳定性
    df[value_col] = pd.to_numeric(df[value_col], errors="coerce")
    df.dropna(inplace=True)

    if group_names:
        df = df[df[category_col].isin(group_names)]
        actual_groups = sorted(group_names) if sort_group_order else group_names
    else:
        actual_groups = df[category_col].unique().tolist()
        if len(actual_groups) != 2:
            raise ValueError("Mann–Whitney test requires exactly two groups.")
        if sort_group_order:
            actual_groups = sorted(actual_groups)

    grouped_data = [df[df[category_col] == g][value_col].values for g in actual_groups]

    if any(len(g) == 0 for g in grouped_data):
        raise ValueError("One or more groups contain no valid numeric values.")

    stat, p = mannwhitneyu(grouped_data[0], grouped_data[1], alternative="two-sided")

    result = {
        "method": "Mann–Whitney U Test",
        "group_names": actual_groups,
        "u_statistic": stat,
        "p_value": p,
        "significant": bool(p < 0.05)
    }

    if show_summary_stats:
        summary = {}
        for g, values in zip(actual_groups, grouped_data):
            summary[g] = {
                "n": len(values),
                "mean": float(np.mean(values)),
                "std": float(np.std(values, ddof=1)) if len(values) > 1 else 0.0
            }
        result["group_summary_stats"] = summary

    return result


# 示例调用
if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    result = mann_whitney_test_from_database(
        database_path="./database/uw_courses.db",
        from_clause="schedules",
        category_col="mon",
        value_col="start_time",
        show_summary_stats=True,
        sort_group_order=True
    )
    print(result)
