import sqlite3
import os
from dotenv import load_dotenv
load_dotenv()

def get_indexes(database_path, table_name):
    """
    Retrieve all indexes of a specified table in the SQLite database.

    Parameters:
    - database_path (str): The path to the database.
    - table_name (str): The name of the table to retrieve indexes from.

    Returns:
    - list: A list of indexes.
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

    query = f"PRAGMA index_list({table_name})"
    cursor.execute(query)
    indexes = cursor.fetchall()
    conn.close()
    if not indexes:
        return f'No indexes found for the table {table_name}.'
    return indexes

if __name__ == '__main__':
    # Example Usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    database_path = "database/uw_courses.db"
    table_name="courses"
    print(get_indexes(database_path, table_name))