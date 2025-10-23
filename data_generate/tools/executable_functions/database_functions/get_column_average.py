import sqlite3
import os
from dotenv import load_dotenv
load_dotenv()

def get_column_average(database_path, table_name, column_name, where_clause=None, where_params=None, group_by=None,):
    """
    Retrieve the average value of a column in a table, with optional WHERE and GROUP BY clauses.

    Parameters:
    - database_path (str): The path to the database.
    - table_name (str): The name of the table to query.
    - column_name (str): The name of the column to calculate the average.
    - where_clause (str, optional): WHERE clause to filter the rows.
    - where_params (tuple or list, optional): Parameters for the WHERE clause.
    - group_by (str or list, optional): GROUP BY clause, e.g., "column_name" or a list of columns.

    Returns:
    - float or list: The average of the column values (if GROUP BY is not used, returns a single value), or a list of averages (if GROUP BY is used).
    - str: Error message if an exception occurs.
    """
    if group_by:
        if isinstance(group_by, list):
            group_by_str = ", ".join(group_by)+','  # If it's a list, join the columns
        else:
            group_by_str = group_by+','
        query = f"SELECT {group_by_str}AVG({column_name}) FROM {table_name}"
    else:
        query = f"SELECT AVG({column_name}) FROM {table_name}"

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

    if not results[0][0]:
        return "No results returned from the query. The average is None."
    # If GROUP BY is used, return a list of averages
    return results if group_by else results[0][0]

if __name__ == '__main__':
    # Example Usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    database = "database/sakila.db"
    # Get the average number of albums per artist, grouping by artist name
    results = get_column_average(
        database_path=database,
        table_name="film",
        column_name="rental_duration",  # Count of albums
        where_clause='release_year = ?',
        where_params=["2006"],
        # group_by=['release_year']
    )
    print(results)     