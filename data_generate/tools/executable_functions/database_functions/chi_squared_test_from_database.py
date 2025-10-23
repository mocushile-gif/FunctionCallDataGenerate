import os
import sqlite3
import pandas as pd
from scipy.stats import chi2_contingency
from dotenv import load_dotenv
from typing import List, Any
load_dotenv()

def chi_squared_test_from_database(
    database_path: str,
    from_clause: str,
    col1: str,
    col2: str,
    where_clause: str = None,
    where_params: List[Any] = None,
    show_contingency: bool = False,
    show_interpretation: bool = False,
):
    """
    Perform a chi-squared test on two categorical columns from a database.

    Parameters:
    - database_path (str): Path to SQLite database.
    - from_clause (str): Table or JOIN clause.
    - col1 (str): First categorical column.
    - col2 (str): Second categorical column.
    - where_clause (str): Optional WHERE clause (without 'WHERE').
    - where_params (List[Any]): Parameters for WHERE clause.
    - show_contingency (bool): Whether to return the contingency table.
    - show_interpretation (bool): Whether to return interpretation string.

    Returns:
    - dict: Chi-squared test result and optionally more details.
    """

    if not os.path.exists(database_path):
        raise FileNotFoundError(f"Database not found: {database_path}")

    query = f"SELECT {col1}, {col2} FROM {from_clause}"
    if where_clause:
        query += f" WHERE {where_clause}"

    conn = sqlite3.connect(database_path)
    try:
        df = pd.read_sql_query(query, conn, params=where_params or [])
    finally:
        conn.close()
    print(df.head())
    col1=col1.split('.')[-1]
    col2=col2.split('.')[-1]
    
    if col1 not in df.columns or col2 not in df.columns:
        raise ValueError(f"Missing column(s): {col1}, {col2}")

    df[col1] = df[col1].astype(str)
    df[col2] = df[col2].astype(str)

    contingency = pd.crosstab(df[col1], df[col2])
    print(contingency)
    if contingency.empty or contingency.shape[0] < 2 or contingency.shape[1] < 2:
        raise ValueError("Chi-squared test requires at least a 2x2 contingency table.")

    chi2, p_value, dof, expected = chi2_contingency(contingency)

    result = {
        "method": "Chi-squared Test",
        "chi2_statistic": chi2,
        "p_value": p_value,
        "degrees_of_freedom": dof,
        "significant": bool(p_value < 0.05)
    }

    if show_interpretation:
        if p_value < 0.05:
            interpretation = "The result is statistically significant (p < 0.05)."
        else:
            interpretation = "The result is not statistically significant (p ≥ 0.05)."
        result["interpretation"] = interpretation

    if show_contingency:
        result["contingency_table"] = contingency.to_dict()
    return result

# 示例调用
if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    # result = chi_squared_test_from_database(
    #     database_path="database/uw_courses.db",
    #     from_clause="sections JOIN course_offerings ON sections.course_offering_uuid = course_offerings.uuid",
    #     col1="term_code",
    #     col2="section_type",
    #     where_clause="term_code IS NOT NULL AND section_type IS NOT NULL",
    #     show_contingency=True,
    #     show_interpretation=True
    # )
    # result = chi_squared_test_from_database(
    #     database_path="./database/EntertainmentAgency.sqlite",
    #     from_clause="Agents",
    #     col1="AgtCity",
    #     col2="AgtState",
    #     show_contingency=True,
    #     show_interpretation=True
    # )
    arguments={"col1":"category.name","col2":"rental_duration","database_path":"./database/sakila.db","from_clause":"film f JOIN film_category fc ON f.film_id = fc.film_id JOIN category ON fc.category_id = category.category_id","show_interpretation":True}
    result = chi_squared_test_from_database(**arguments)

    import pprint
    pprint.pprint(result)
