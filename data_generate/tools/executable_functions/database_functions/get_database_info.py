import sqlite3
import os
from dotenv import load_dotenv
load_dotenv()

def get_database_info(database_path):
    """
    Retrieve information about the SQLite database, including table names, 
    schema details, and record counts.

    Parameters:
    - database_path (str): The path to the database.

    Returns:
    - dict: A dictionary containing information about tables, schemas, and record counts.
    - str: Error message if an exception occurs.
    """
    
    if not os.path.exists(database_path):
        raise FileNotFoundError(f"Database '{database_path}' does not exist.")
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Fetch all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]

    database_info = {}
    for table in tables:
        # Get table schema
        cursor.execute(f"PRAGMA table_info({table});")
        schema = [{"column_name": row[1], "data_type": row[2]} for row in cursor.fetchall()]

        # Get record count
        cursor.execute(f"SELECT COUNT(*) FROM {table};")
        record_count = cursor.fetchone()[0]

        # Save table info
        database_info[table] = {
            "schema": schema,
            "record_count": record_count,
        }

    conn.close()
    return database_info


if __name__ == '__main__':
    # Example Usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    database = "database/chinook.db"
    info = get_database_info(database)
    print(info)
