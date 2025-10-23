import os
import sqlite3
import pandas as pd
from dotenv import load_dotenv
from typing import Literal

load_dotenv()

def union_sql_queries(
    database_path: str,
    sql1: str,
    sql2: str,
    operator: Literal["UNION", "UNION ALL", "INTERSECT", "EXCEPT"] = "UNION",
    save_to_file: str = None,
    create_temp_table: str = None,
):
    """
    Combine two SQL queries using UNION, UNION ALL, INTERSECT, or EXCEPT.

    Parameters:
    - database_path (str): Path to SQLite database.
    - sql1 (str): First SQL SELECT query.
    - sql2 (str): Second SQL SELECT query.
    - operator (str): Type of set operation: 'UNION', 'UNION ALL', 'INTERSECT', or 'EXCEPT'.
    - save_to_file (str): Optional path to save result as .csv/.xlsx.
    - create_temp_table (str): Optional name of temp table to save result.

    Returns:
    - tuple: (success: bool, message: str or result preview)
    """

    if not os.path.exists(database_path):
        return False, f"Database '{database_path}' does not exist."

    if operator not in {"UNION", "UNION ALL", "INTERSECT", "EXCEPT"}:
        return False, f"Unsupported SQL operator: {operator}"

    combined_query = f"{sql1.strip()} {operator} {sql2.strip()}"

    conn = sqlite3.connect(database_path)
    try:
        df = pd.read_sql_query(combined_query, conn)

        message = f"Combined query returned {len(df)} rows using {operator}."

        if create_temp_table:
            df.to_sql(create_temp_table, conn, if_exists="replace", index=False)
            message += f" Temp table '{create_temp_table}' created."

        if save_to_file:
            if save_to_file.endswith(".csv"):
                df.to_csv(save_to_file, index=False)
                message += f" Result saved to {save_to_file}"
            elif save_to_file.endswith(".xlsx"):
                df.to_excel(save_to_file, index=False)
                message += f" Result saved to {save_to_file}"
            else:
                return False, "Unsupported save format. Use .csv or .xlsx."

        return True, message

    except Exception as e:
        return False, str(e)

    finally:
        conn.close()

if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    db = "database/bank_sales_trading.sqlite"
    sql_1 = "SELECT sales, region FROM weekly_sales WHERE region = 'ASIA'"
    sql_2 = "SELECT sales, region FROM weekly_sales WHERE region = 'EUROPE'"

    success, msg = union_sql_queries(
        database_path=db,
        sql1=sql_1,
        sql2=sql_2,
        operator="UNION",
        create_temp_table="temp_union_result",
        save_to_file="./union_result.csv"
    )
    print("Success:", success)
    print("Message:", msg)
