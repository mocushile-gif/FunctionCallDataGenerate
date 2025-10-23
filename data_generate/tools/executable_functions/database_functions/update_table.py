import sqlite3
import os
from dotenv import load_dotenv
load_dotenv()

def update_table(
    database_path, 
    table_name, 
    set_clause, 
    where_clause=None, 
    where_params=None,
    ):
    """
    Perform an UPDATE query on a specified SQLite table.

    Parameters:
    - database_path (str): The path to the database.
    - table_name (str): Name of the table to update.
    - set_clause (str): SET clause, e.g., "column1 = ?, column2 = ?".
    - where_clause (str, optional): WHERE clause to filter rows to update.
    - where_params (tuple or list, optional): Parameters for the WHERE clause.

    Returns:
    - int: The number of rows affected.
    - str: Error message if an exception occurs.
    """

    # Start building the query
    query = f"UPDATE {table_name} SET {set_clause}"

    # Add WHERE clause if provided
    if where_clause:
        query += f" WHERE {where_clause}"

    # Connect to the database and execute the query
    
    if not os.path.exists(database_path):
        raise FileNotFoundError(f"Database '{database_path}' does not exist.")
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(query, where_params or [])
    conn.commit()
    conn.close()

    return f"The number of rows affected: {cursor.rowcount}"  # Return the number of rows affected
