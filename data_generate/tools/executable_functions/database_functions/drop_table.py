import sqlite3
import os
from dotenv import load_dotenv
load_dotenv()

def drop_table(database_path, table_name):
    """
    Drop a table from the SQLite database.

    Parameters:
    - database_path (str): Path to the SQLite database.
    - table_name (str): Name of the table to drop.

    Returns:
    - str: Success message or error message if an exception occurs.
    """

    if not os.path.exists(database_path):
        raise FileNotFoundError(f"Database '{database_path}' does not exist.")

    query = f"DROP TABLE IF EXISTS {table_name}"

    conn = sqlite3.connect(database_path)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?;
        """, (table_name,))
        exists = cursor.fetchone() is not None

        if not exists:
            return f"Table '{table_name}' does not exist. Nothing to drop."

        cursor.execute(query)
        conn.commit()
    finally:
        conn.close()

    return f"Table '{table_name}' dropped successfully."

if __name__ == '__main__':
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    database_path = "database/bank_sales_trading.sqlite"
    table_name= "temp_union_result"
    print(drop_table(database_path, table_name))
