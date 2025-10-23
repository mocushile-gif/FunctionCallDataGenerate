import sqlite3
import os
from dotenv import load_dotenv
load_dotenv()

def get_table_info(database_path, table_name):
    """
    Get the schema (column names and types) of a specified SQLite table.

    Parameters:
    - database_path (str): The path to the database.
    - table_name (str): Name of the table to describe.

    Returns:
    - list: List of dictionaries containing column names and data types.
    - str: Error message if an exception occurs.
    """
    query = f"PRAGMA table_info({table_name})"
    
    # Construct the database file path
    if not os.path.exists(database_path):
        raise FileNotFoundError(f"Database '{database_path}' does not exist.")
    
    # Connect to the database and execute the query
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
    record_count = cursor.fetchone()[0]
    conn.close()

    # Check if the result is empty (indicating the table does not exist)
    if not result:
        raise ValueError(f"Table '{table_name}' does not exist in the database '{database_path}'.")
    
    # Format the result into a list of dictionaries
    schema = [{"column_name": row[1], "data_type": row[2]} for row in result]
    return {
            "table_name": table_name,
            "table_schema": schema,
            "record_count": record_count,
        }


if __name__ == '__main__':
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    print(get_table_info('database/uw_courses.db', 'course_offerings'))
    print(get_table_info('database/uw_courses.db', 'sections'))
    print(get_table_info('database/uw_courses.db', 'schedules'))
