import sqlite3
import os
from dotenv import load_dotenv
load_dotenv()

def get_table_creation_sql(database_path, table_name):
    """
    Retrieve the SQL statement used to create a table.

    Parameters:
    - database_path (str): The path to the database.
    - table_name (str): The name of the table.

    Returns:
    - str: The SQL creation statement for the table.
    - str: Error message if an exception occurs.
    """
    query = f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'"

    
    if not os.path.exists(database_path):
        raise FileNotFoundError(f"Database '{database_path}' does not exist.")
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(query)
    create_sql = cursor.fetchone()[0]
    conn.close()

    return create_sql


if __name__ == '__main__':
    # Example Usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    database = "database/uw_courses.db"
    # Get the min and max album ID for each artist, grouping by artist name
    results = get_table_creation_sql(
        database_path=database,
        table_name="sections",
    )
    print(results)