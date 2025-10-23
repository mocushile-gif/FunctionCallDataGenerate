import sqlite3
import os
from dotenv import load_dotenv
load_dotenv()

def get_first_n_rows(database_path, table_name, n):
    """
    Retrieve the first N rows from a specified table in the SQLite database.

    Parameters:
    - database_path (str): The path to the database.
    - table_name (str): The name of the table to retrieve data from.
    - n (int): The number of rows to retrieve.

    Returns:
    - list: A list of tuples representing the rows.
    - str: Error message if an exception occurs.
    """
    query = f"SELECT * FROM {table_name} LIMIT {n}"
    if not os.path.exists(database_path):
        raise FileNotFoundError(f"Database '{database_path}' does not exist.")
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()

    return rows

if __name__ == '__main__':
    # Example Usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    database = "database/uw_courses.db"
    # Get the min and max album ID for each artist, grouping by artist name
    results = get_first_n_rows(
        database_path=database,
        table_name="schedules",
        n="100", 
    )
    print(results)