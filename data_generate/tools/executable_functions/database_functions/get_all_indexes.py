import sqlite3
import os
from dotenv import load_dotenv
load_dotenv()

def get_all_indexes(database_path):
    """
    Retrieve index information for all tables in a SQLite database.

    Parameters:
    - database_path (str): Path to the SQLite database file.
    Returns:
    - dict: {table_name: [index_list]} if found, or message string.
    """

    if not os.path.exists(database_path):
        raise FileNotFoundError(f"Database '{database_path}' does not exist.")

    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # 获取所有用户表（排除 sqlite 内部表）
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [row[0] for row in cursor.fetchall()]

    all_indexes = {}

    for table in tables:
        cursor.execute(f"PRAGMA index_list({table})")
        indexes = cursor.fetchall()
        if indexes:
            all_indexes[table] = indexes

    conn.close()

    if not all_indexes:
        return "No indexes found in any table."
    return all_indexes

if __name__ == '__main__':
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    database_path = "database/uw_courses.db"
    try:
        index_result = get_all_indexes(database_path)
        import json
        print(json.dumps(index_result, indent=2))
    except Exception as e:
        print(f"Error: {e}")
