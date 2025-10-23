import sqlite3
import os
from dotenv import load_dotenv
load_dotenv()

def create_table(database_path, table_name, columns):
    """
    Create a new table in the SQLite database.

    Parameters:
    - database_path (str): The path to the database.
    - table_name (str): Name of the table to create.
    - columns (list of tuples): List of tuples where each tuple contains
      (column_name, data_type), e.g., [('id', 'INTEGER'), ('name', 'TEXT')].

    Returns:
    - str: Success message or error message if an exception occurs.
    """
    # Build the columns part of the query
    columns_str = ", ".join([f"{col['column_name']} {col['data_type']}" for col in columns])
    query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_str})"

    # Connect to the database and execute the query
    
    if not os.path.exists(database_path):
        raise FileNotFoundError(f"Database '{database_path}' does not exist.")
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    conn.close()

    return f"Table '{table_name}' created successfully."

if __name__ == '__main__':
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    # Example Usage
    database_path = "database/sakila.db"
    table_name= "top_rated_movies2"
    columns=[{"column_name": "track_id", "data_type": "INTEGER"}, {"column_name": "track_name", "data_type": "TEXT"}, {"column_name": "purchase_count", "data_type": "INTEGER"}, {"column_name": "album_name", "data_type": "TEXT"}]
    print(create_table(database_path,table_name,columns))