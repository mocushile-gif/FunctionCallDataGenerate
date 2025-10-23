import os
import sqlite3
import pandas as pd
from scipy.stats import f_oneway
from typing import List, Any
from dotenv import load_dotenv
load_dotenv()

def anova_test_from_database(
    database_path: str,
    from_clause: str,
    category_col: str,
    value_col: str,
    where_clause: str = None,
    where_params: List[Any] = None,
    show_summary_stats: bool = False,
    show_interpretation: bool = False,
    drop_empty_groups: bool = True,
):
    """
    Perform a one-way ANOVA test using data from an SQLite database.

    Parameters:
    - database_path (str): Path to the SQLite DB file.
    - from_clause (str): Table or JOIN clause for SELECT.
    - category_col (str): Categorical column.
    - value_col (str): Numeric value column.
    - where_clause (str): Optional WHERE clause.
    - where_params (List[Any]): Parameters for the WHERE clause.
    - show_summary_stats (bool): Whether to return group summary stats.
    - show_interpretation (bool): Whether to return human-readable conclusion.
    - drop_empty_groups (bool): If True, drop empty groups instead of raising error.


    Returns:
    - dict: ANOVA test results.
    """
    db_path = database_path
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found at: {db_path}")

    query = f"SELECT {category_col}, {value_col} FROM {from_clause}"
    if where_clause:
        query += f" WHERE {where_clause}"

    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql_query(query, conn, params=where_params or [])
    finally:
        conn.close()

    if category_col not in df.columns:
        raise ValueError(f"Column '{category_col}' not found.")
    if value_col not in df.columns:
        raise ValueError(f"Column '{value_col}' not found.")

    df[category_col] = df[category_col].astype(str)
    df[value_col] = pd.to_numeric(df[value_col], errors="coerce")
    df.dropna(inplace=True)
    

    grouped = df.groupby(category_col)[value_col].apply(list)
    group_names = grouped.index.tolist()
    groups = grouped.values

    if len(groups) < 2:
        raise ValueError("ANOVA requires at least two groups.")

    if not drop_empty_groups and any(len(g) == 0 for g in groups):
        raise ValueError("One or more groups have no data.")
    groups = [g for g in groups if len(g) > 0]

    f_stat, p_value = f_oneway(*groups)

    result = {
        "method": "One-way ANOVA",
        "group_names": group_names,
        "num_groups": len(groups),
        "f_statistic": f_stat,
        "p_value": p_value,
        "significant": p_value < 0.05
    }

    if show_interpretation:
        result["interpretation"] = (
            "✅ Statistically significant (p < 0.05)"
            if p_value < 0.05 else
            "❌ Not statistically significant (p ≥ 0.05)"
        )

    if show_summary_stats:
        stats = df.groupby(category_col)[value_col].agg(["count", "mean", "std"]).reset_index()
        result["summary_stats"] = stats.to_dict(orient="records")

    return result

# 示例调用
if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    res = anova_test_from_database(
        database_path="./database/uw_courses.db",
        from_clause="schedules",
        category_col="mon",
        value_col="start_time",
        where_clause="start_time IS NOT NULL",
        show_summary_stats=True,
        show_interpretation=True,
        drop_empty_groups=True
    )
    # arguments={"category_col": "strftime('%m', book_date)", "database_path": "./database/airlines.db", "from_clause": "bookings", "value_col": "total_amount", "show_interpretation": True}
    # res = anova_test_from_database(**arguments)
    print(res)
