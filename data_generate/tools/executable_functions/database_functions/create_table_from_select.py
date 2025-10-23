import sqlite3
import os
from dotenv import load_dotenv
load_dotenv()

def create_table_from_select(database_path: str, table_name: str, sql_query: str):
    """
    Create a new table from an existing SQL SELECT query.

    Parameters:
    - database_path: Path to the SQLite database file
    - table_name: Name of the new table to create
    - sql_query: SELECT SQL query used to populate the new table

    Returns:
    - Success message string
    """
    if not os.path.exists(database_path):
        raise FileNotFoundError(f"Database '{database_path}' does not exist.")
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    cursor.execute(f"CREATE TABLE {table_name} AS {sql_query}")
    conn.commit()
    conn.close()
    return f"Table '{table_name}' created successfully from query."

if __name__ == '__main__':
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    from select_from_tables import select_from_tables
    print(select_from_tables(
        database_path="./database/uw_courses.db",
        from_clause="schedules",
        ))