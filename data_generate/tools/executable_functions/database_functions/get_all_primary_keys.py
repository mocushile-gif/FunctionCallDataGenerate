import sqlite3
import os
from dotenv import load_dotenv
load_dotenv()

def get_all_primary_keys(database_path):
    """
    Retrieve primary key columns for all tables in a SQLite database.

    Parameters:
    - database_path (str): The path to the database.
    Returns:
    - dict: {table_name: [primary_key_columns]} or str if no PKs found.
    """


    if not os.path.exists(database_path):
        raise FileNotFoundError(f"Database '{database_path}' does not exist.")

    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # 获取所有表名（排除系统表）
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [row[0] for row in cursor.fetchall()]

    all_primary_keys = {}

    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        pk_columns = [col[1] for col in columns if col[5] > 0]  # col[5] 为 pk 顺序
        if pk_columns:
            all_primary_keys[table] = pk_columns

    conn.close()

    if not all_primary_keys:
        return "No primary keys found in any table."
    return all_primary_keys

if __name__ == '__main__':
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    database_path = "database/chinook.db"
    pk_result = get_all_primary_keys(database_path)
    print(pk_result)
