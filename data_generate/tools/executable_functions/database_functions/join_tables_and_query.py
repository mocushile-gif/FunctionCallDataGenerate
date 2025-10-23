import sqlite3
import os
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

def join_tables_and_query(
    database_path,
    table1,
    join_conditions=None,
    select_columns="*",
    where_clause=None,
    where_params=None,
    save_to_file=None,
    create_temp_table=None,
):
    """
    Perform a JOIN query on multiple tables and retrieve specific columns, with optional WHERE clause,
    export to file, or save result to a temporary table.

    Parameters:
    - database_path (str): Path to the SQLite database.
    - table1 (str): First table name.
    - join_conditions (list of dicts): Each dict has 'table_name' and 'on_condition' keys.
    - select_columns (str or list): Columns to select.
    - where_clause (str): WHERE clause (without 'WHERE').
    - where_params (tuple or list): Parameters for WHERE clause.
    - save_to_file (str): If set, saves result to CSV or Excel file.
    - create_temp_table (str): If set, saves result to a TEMP table in the database.

    Returns:
    - tuple: (message, results)
    """

    if isinstance(select_columns, list):
        select_columns = ", ".join(select_columns)

    # Build query
    query = f"SELECT {select_columns} FROM {table1}"
    if join_conditions:
        for join in join_conditions:
            query += f" JOIN {join['table_name']} ON {join['on_condition']}"
    if where_clause:
        query += f" WHERE {where_clause}"

    print("Executing query:", query)

    if not os.path.exists(database_path):
        raise FileNotFoundError(f"Database '{database_path}' does not exist.")

    # Execute query
    conn = sqlite3.connect(database_path)
    try:
        cursor = conn.cursor()
        cursor.execute(query, where_params or [])
        results = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        # print(column_names)

        df = pd.DataFrame(results, columns=column_names)
        message = f"Query returned {len(df)} rows."

        # Save to temporary table if specified
        if create_temp_table:
            df.to_sql(create_temp_table, conn, if_exists='replace', index=False)
            message += f"\nTemporary table '{create_temp_table}' created successfully."

        # Save to file if specified
        if save_to_file:
            if save_to_file.endswith('.csv'):
                df.to_csv(save_to_file, index=False)
                message += f"\nResult saved to CSV file: {save_to_file}"
            elif save_to_file.endswith('.xlsx'):
                df.to_excel(save_to_file, index=False)
                message += f"\nResult saved to Excel file: {save_to_file}"
            else:
                raise ValueError("Unsupported format to save file. Use .csv or .xlsx. Or you can set the `create_temp_table` to save to a temporary table in the database.")

    finally:
        conn.close()

    return message, results


if __name__ == '__main__':
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    # Example Usage with multiple joins
    database_path = "database/uw_courses.db"
    table1 = "schedules"
    join_conditions = [
        {"table_name":"sections", "on_condition":"schedules.uuid = sections.schedule_uuid"},
        {"table_name":"course_offerings", "on_condition":"course_offerings.uuid = sections.course_offering_uuid"},
        # ("courses", "courses.uuid = course_offerings.course_uuid"),
        # ("teachings", "sections.uuid = teachings.section_uuid"),
        # ("instructors", "teachings.instructor_id = instructors.id")
    ]
    # select_columns = "distinct courses.name, instructors.name"
    select_columns = "distinct sections.uuid"
    where_clause = "schedules.mon = 'true' and schedules.wed = 'true'"
    info = join_tables_and_query(database_path, table1=table1, 
                                 join_conditions=join_conditions, 
                                 select_columns=select_columns, 
                                 where_clause=where_clause,
                                #  save_to_file='./result.csv',
                                #  create_temp_table="temp_schedule_mw",
                                 )
    print(info) 