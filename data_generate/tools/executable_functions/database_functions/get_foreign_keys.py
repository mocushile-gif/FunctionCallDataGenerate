import sqlite3
import os
from dotenv import load_dotenv
load_dotenv()

def get_foreign_keys(database_path, table_name):
    """
    Retrieve all foreign key constraints for a specified table.

    Parameters:
    - database_path (str): The path to the database.
    - table_name (str): The name of the table to query for foreign keys.

    Returns:
    - list: A list of foreign key constraints.
    - str: Error message if an exception occurs.
    """
    
    if not os.path.exists(database_path):
        raise FileNotFoundError(f"Database '{database_path}' does not exist.")
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # 检查表是否存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table_name,))
    if cursor.fetchone() is None:
        conn.close()
        raise ValueError(f"Table '{table_name}' does not exist in the database.")

    # 查询外键
    query = f"PRAGMA foreign_key_list({table_name})"
    cursor.execute(query)
    foreign_keys = cursor.fetchall()
    conn.close()

    if not foreign_keys:
        return f'No foreign keys found for the table {table_name}.'
    return foreign_keys

if __name__ == '__main__':
    # Example Usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    database_path = "database/sakila.db"
    # table_name="orders"
    table_name="actor"
    # Get the min and max album ID for each artist, grouping by artist name
    results = get_foreign_keys(
        database_path,
        table_name
    )
    print(results)