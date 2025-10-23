import sqlite3
import os
from dotenv import load_dotenv
import pandas as pd
load_dotenv()

def select_from_tables(
    database_path, 
    from_clause, 
    columns="*", 
    where_clause=None, 
    where_params=None, 
    order_by=None, 
    limit=None,
    group_by=None,
    distinct=False,
    save_to_file=None,
    create_temp_table=None,
):
    """
    Perform a SELECT query on a specified SQLite table with dynamic parameters and optional export or temp table creation.

    Parameters:
    - database_path (str): Path to the SQLite database.
    - from_clause (str): Table name or JOIN clause.
    - columns (str or list): Columns to select.
    - where_clause (str): WHERE condition (no 'WHERE').
    - where_params (tuple or list): Parameters for WHERE clause.
    - order_by (str): ORDER BY clause.
    - limit (int): Max number of rows.
    - group_by (str or list): GROUP BY clause.
    - distinct (bool): If true, adds DISTINCT to SELECT.
    - save_to_file (str): If set, exports results to CSV or Excel.
    - create_temp_table (str): If set, creates a TEMP table in the same database with this name.

    Returns:
    - tuple: (message, results)
    """

    if not os.path.exists(database_path):
        raise FileNotFoundError(f"Database '{database_path}' does not exist.")

    if isinstance(columns, list):
        columns = ", ".join(columns)

    distinct_clause = "DISTINCT " if distinct else ""
    query = f"SELECT {distinct_clause}{columns} FROM {from_clause}"
    if where_clause:
        query += f" WHERE {where_clause}"
    if group_by:
        group_by_clause = ", ".join(group_by) if isinstance(group_by, list) else group_by
        query += f" GROUP BY {group_by_clause}"
    if order_by:
        query += f" ORDER BY {order_by}"
    if limit:
        query += f" LIMIT {limit}"

    # Connect to database and fetch results
    conn = sqlite3.connect(database_path)
    try:
        cursor = conn.cursor()
        cursor.execute(query, where_params or [])
        results = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]

        df = pd.DataFrame(results, columns=column_names)

        message = f"Query returned {len(df)} rows."

        # Save to temp table if requested
        if create_temp_table:
            df.to_sql(create_temp_table, conn, if_exists="replace", index=False)
            message += f"\nTemporary table '{create_temp_table}' created in database."

        # Save to file if requested
        if save_to_file:
            if save_to_file.endswith('.csv'):
                df.to_csv(save_to_file, index=False)
                message += f"\nSaved result to {save_to_file}."
            elif save_to_file.endswith('.xlsx'):
                df.to_excel(save_to_file, index=False)
                message += f"\nSaved result to {save_to_file}."
            else:
                raise ValueError("Unsupported file format. Use .csv or .xlsx.")

    finally:
        conn.close()

    return message, results

if __name__ == '__main__':
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    # role': 'assistant', 'tool_calls': [{'function': {'arguments': '{"columns":["coordinates"],"database_path":"./database/airlines.db","from_clause":"airports_data","where_clause":"airport_name->>\'name\' LIKE \'%Nefteyugansk%\'"}', 'name': 'select_from_tables'}
    msg, _ = select_from_tables(
        database_path="./database/airlines.db",
        from_clause="airports_data",
        columns=["airport_name"],
        where_clause="airport_name Like '%Nefteyugansk%'",
        # where_params=["SVO"],
        limit=100,
        # save_to_file='./result.csv',
        # create_temp_table="temp_flights_svo"
    )
    print(msg,_[:10])
