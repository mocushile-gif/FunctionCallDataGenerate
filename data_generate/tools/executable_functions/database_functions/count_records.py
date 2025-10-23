import sqlite3
import os
from dotenv import load_dotenv
load_dotenv()

def count_records(database_path, table_name, where_clause=None, where_params=None, group_by=None):
    """
    Count the number of records in a table, with optional WHERE and GROUP BY clauses.

    Parameters:
    - database_path (str): The path to the database.
    - table_name (str): The name of the table.
    - where_clause (str, optional): WHERE clause to filter the records.
    - where_params (tuple or list, optional): Parameters for the WHERE clause.
    - group_by (str or list, optional): GROUP BY clause, e.g., "column_name" or a list of columns.

    Returns:
    - list: A list of counts for each group (if GROUP BY is used), or a single integer count.
    - str: Error message if an exception occurs.
    """
    # Add GROUP BY clause if provided
    if group_by:
        if isinstance(group_by, list):
            group_by_str = ", ".join(group_by)+','  # If it's a list, join the columns
        else:
            group_by_str = group_by+','
        query = f"SELECT {group_by_str}COUNT(*) FROM {table_name}"
    else:
        query = f"SELECT COUNT(*) FROM {table_name}"

    # Add WHERE clause if provided
    if where_clause:
        query += f" WHERE {where_clause}"

    # Add GROUP BY clause if provided
    if group_by:
        if isinstance(group_by, list):
            group_by = ", ".join(group_by)  # If it's a list, join the columns
        query += f" GROUP BY {group_by}"

    # Connect to the database and execute the query
    
    if not os.path.exists(database_path):
        raise FileNotFoundError(f"Database '{database_path}' does not exist.")
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(query, where_params or [])
    results = cursor.fetchall()
    conn.close()
    # If GROUP BY is used, return the count for each group
    return results if group_by else results[0][0]

if __name__ == '__main__':
    # Example Usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    database = "database/airlines.db"
    # Count the number of albums for each artist, group by artist and order by album count
    results = count_records(
        database_path=database,
        table_name="flights",
        where_clause='departure_airport = ? AND scheduled_departure BETWEEN ? AND ?',
        where_params= ['SVO', '2024-06-21 00:00:00', '2017-09-15 23:59:59'],
        group_by='arrival_airport'
    )
    print(results)
