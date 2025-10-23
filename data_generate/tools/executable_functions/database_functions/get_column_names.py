import sqlite3
import os
from dotenv import load_dotenv
load_dotenv()

def get_column_names(database_path, table_name):
    """
    Retrieve column names for a specified table in the SQLite database.

    Parameters:
    - database_path (str): The path to the database.
    - table_name (str): The name of the table to retrieve column names.

    Returns:
    - list: List of column names.
    - str: Error message if an exception occurs.
    """
    
    if not os.path.exists(database_path):
        raise FileNotFoundError(f"Database '{database_path}' does not exist.")
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = [row[1] for row in cursor.fetchall()]
    conn.close()

    return columns

if __name__ == '__main__':
    # Example Usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    database = "database/airlines.db"
    table_name='flights'
    info = get_column_names(database,table_name)
    print(info)