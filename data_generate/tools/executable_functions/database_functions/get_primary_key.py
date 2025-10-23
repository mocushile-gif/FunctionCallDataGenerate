import sqlite3
import os
from dotenv import load_dotenv
load_dotenv()

def get_primary_key(database_path, table_name):
    """
    Retrieve the primary key column(s) of a table.

    Parameters:
    - database_path (str): The path to the database.
    - table_name (str): The name of the table.

    Returns:
    - list: A list of primary key column names.
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

    query = f"PRAGMA table_info({table_name})"
    
    cursor.execute(query)
    columns = cursor.fetchall()
    primary_keys = [col[1] for col in columns if col[5] > 0]  # col[5] 是 pk：0 表示非主键；1 开始表示主键列顺序

    conn.close()

    if not primary_keys:
        return f'No primary key found for the table {table_name}.'
    return primary_keys


if __name__ == '__main__':
    # Example Usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    database_path = "database/chinook.db"
    table_name="Album"
    print(get_primary_key(database_path, table_name))