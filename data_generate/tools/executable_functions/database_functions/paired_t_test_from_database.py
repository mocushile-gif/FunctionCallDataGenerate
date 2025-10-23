import os
import sqlite3
import pandas as pd
from scipy.stats import ttest_rel
from dotenv import load_dotenv
from typing import List, Any
load_dotenv()

def paired_t_test_from_database(
    database_path: str,
    from_clause: str,
    x_col: str,
    y_col: str,
    where_clause: str = None,
    where_params: List[Any] = None,
    drop_na: bool = True,
    show_summary_stats: bool = False,
):
    """
    Perform a paired t-test using two numeric columns from a database.

    Parameters:
    - database_path: Path to SQLite database.
    - from_clause: Table or JOIN clause.
    - x_col: First numeric column.
    - y_col: Second numeric column.
    - where_clause: Optional WHERE clause (without 'WHERE').
    - where_params: Optional parameter list for the WHERE clause.
    - drop_na: Whether to drop NA rows.
    - show_summary_stats: Return sample size, mean, std for each column.

    Returns:
    - dict: Paired t-test result.
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
        raise ValueError("No valid numeric data found for paired t-test.")

    t_stat, p = ttest_rel(x, y)

    result = {
        "method": "Paired t-test",
        "x_column": x_col,
        "y_column": y_col,
        "sample_size": len(x),
        "t_statistic": t_stat,
        "p_value": p,
        "significant": bool(p < 0.05)
    }

    if show_summary_stats:
        result["x_summary"] = {
            "mean": float(x.mean()),
            "std": float(x.std(ddof=1)),
            "n": int(x.count())
        }
        result["y_summary"] = {
            "mean": float(y.mean()),
            "std": float(y.std(ddof=1)),
            "n": int(y.count())
        }

    return result


# 示例调用
if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    result = paired_t_test_from_database(
        database_path="database/uw_courses.db",
        from_clause="schedules",
        x_col="start_time",
        y_col="end_time",
        where_clause="start_time IS NOT NULL AND end_time IS NOT NULL",
        drop_na=True,
        show_summary_stats=True
    )
    print(result)
