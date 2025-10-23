import sqlite3
import os
from dotenv import load_dotenv
load_dotenv()

def get_column_min_max_values(database_path, table_name, column_name, where_clause=None, where_params=None, group_by=None):
    """
    Retrieve the minimum and maximum values of a column in a specified table, with optional WHERE and GROUP BY clauses.

    Parameters:
    - database_path (str): The path to the database.
    - table_name (str): The name of the table.
    - column_name (str): The name of the column to query.
    - where_clause (str, optional): WHERE clause to filter the rows.
    - where_params (tuple or list, optional): Parameters for the WHERE clause.
    - group_by (str or list, optional): GROUP BY clause, e.g., "column_name" or a list of columns.

    Returns:
    - tuple or list: A tuple (min_value, max_value) if no `GROUP BY` is used, or a list of tuples for each group.
    - str: Error message if an exception occurs.
    """

    if group_by:
        if isinstance(group_by, list):
            group_by_str = ", ".join(group_by)+','  # If it's a list, join the columns
        else:
            group_by_str = group_by+','
        query = f"SELECT {group_by_str}MIN({column_name}), MAX({column_name}) FROM {table_name}"
    else:
        query = f"SELECT MIN({column_name}), MAX({column_name}) FROM {table_name}"

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

    # If GROUP BY is used, return a list of (min_value, max_value) for each group
    return results if group_by else results[0]

if __name__ == '__main__':
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    database = "./database/EntertainmentAgency.sqlite"
    # Get the min and max album ID for each artist, grouping by artist name
    results = get_column_min_max_values(
        database_path=database,
        table_name="Entertainers",
        column_name="EntPhoneNumber",  # Using AlbumId as the column
        # where_clause="A.ArtistId = ?",
        # where_params=("1",),
        # group_by="B.Name"  # Grouping by artist name
    )
    print(results)
