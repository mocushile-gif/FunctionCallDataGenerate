import sqlite3
import os
from dotenv import load_dotenv
load_dotenv()

def get_all_foreign_keys(database_path):
    """
    Retrieve foreign key constraints for all tables in the database.

    Parameters:
    - database_path (str): The path to the database.
    Returns:
    - dict: {table_name: [foreign_key_constraints]} or error message
    """

    if not os.path.exists(database_path):
        raise FileNotFoundError(f"Database '{database_path}' does not exist.")

    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # 获取所有表名
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [row[0] for row in cursor.fetchall()]

    all_foreign_keys = {}

    for table in tables:
        cursor.execute(f"PRAGMA foreign_key_list({table})")
        fks = cursor.fetchall()
        if fks:
            all_foreign_keys[table] = fks

    conn.close()

    if not all_foreign_keys:
        return "No foreign keys found in any table."
    return all_foreign_keys

if __name__ == '__main__':
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    database_path = "database/chinook.db"

    try:
        fk_results = get_all_foreign_keys(database_path)
        import json
        print(json.dumps(fk_results, indent=2))
    except Exception as e:
        print(f"Error: {e}")
