import os
import sqlite3
import pandas as pd
from scipy.stats import ttest_ind
from dotenv import load_dotenv
from typing import List, Any, Union
load_dotenv()

def group_t_test_from_database(
    database_path: str,
    from_clause: str,
    category_col: str,
    value_col: str,
    where_clause: str = None,
    where_params: List[Any] = None,
    group_names: Union[List[str], tuple] = None,
    equal_var: bool = True,
    dropna: bool = True,
):
    """
    Perform independent t-test on two groups from a database.

    Parameters:
    - database_path (str): Path to SQLite database.
    - from_clause (str): Table or JOIN clause.
    - category_col (str): Grouping column (categorical). Even if the original values are of type int, they will be coerced to string during grouping to ensure consistent behavior.
    - value_col (str): Numeric value column.
    - where_clause (str): Optional WHERE condition (without 'WHERE').
    - where_params (List[Any]): Parameters for WHERE clause.
    - group_names (list or tuple): Optional. If provided, must contain exactly two group values.
    - equal_var (bool): Assume equal variance (standard t-test vs Welch).
    - dropna (bool): Whether to drop rows with missing values in the two target columns.


    Returns:
    - dict: t-test result including t statistic, p-value, and interpretation.
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
    if category_col not in df.columns or value_col not in df.columns:
        raise ValueError("Missing required columns in query result.")

    df[category_col] = df[category_col].astype(str)
    df[value_col] = pd.to_numeric(df[value_col], errors='coerce')

    if dropna:
        df.dropna(subset=[category_col, value_col], inplace=True)
    elif df[[category_col, value_col]].isnull().any().any():
        raise ValueError("Missing values present. Set dropna=True to handle them.")

    if group_names:
        if not isinstance(group_names, (list, tuple)) or len(group_names) != 2:
            raise ValueError("group_names must be a list or tuple of exactly two values.")
        df = df[df[category_col].isin(group_names)]
        actual_groups = df[category_col].unique()
        if len(actual_groups) != 2:
            raise ValueError(f"One or both specified groups not found: {group_names}")
    else:
        actual_groups = df[category_col].unique()
        if len(actual_groups) != 2:
            raise ValueError("Exactly two groups are required, or specify group_names.")

    grouped = df.groupby(category_col)[value_col]
    values = [grouped.get_group(g).values for g in actual_groups]

    if any(len(v) == 0 for v in values):
        raise ValueError("One of the groups has no valid numeric values.")

    stat, p_value = ttest_ind(*values, equal_var=equal_var)

    return {
        "method": "Independent t-test" + (" (Welch)" if not equal_var else ""),
        "equal_var": equal_var,
        "dropna": dropna,
        "group_names": list(actual_groups),
        "group_1_size": len(values[0]),
        "group_2_size": len(values[1]),
        "t_statistic": stat,
        "p_value": p_value,
        "significant": bool(p_value < 0.05),
        "interpretation": (
            "Statistically significant difference (p < 0.05)"
            if p_value < 0.05 else
            "No statistically significant difference (p ≥ 0.05)"
        )
    }

if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    result = group_t_test_from_database(
        database_path="database/chinook.db",
        from_clause="Track",
        category_col="GenreId",
        value_col="UnitPrice",
        where_clause="GenreId IN ('1','2') AND UnitPrice IS NOT NULL",
        group_names=["1","2"],
        equal_var=False,
        dropna=True
    )
    import pprint
    pprint.pprint(result)
