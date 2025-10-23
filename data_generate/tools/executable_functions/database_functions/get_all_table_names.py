import sqlite3
import os
from dotenv import load_dotenv
load_dotenv()

def get_all_table_names(database_path):
    """
    Retrieve all table names in the SQLite database.

    Parameters:
    - database_path (str): The path to the database.

    Returns:
    - list: List of table names.
    - str: Error message if an exception occurs.
    """
    
    if not os.path.exists(database_path):
        raise FileNotFoundError(f"Database '{database_path}' does not exist.")
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()

    return tables

if __name__ == '__main__':
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    database = "database/airlines.db"
    info = get_all_table_names(database)
    print(info)