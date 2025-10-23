import sqlite3
import os
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

def export_table_to_file(
    database_path, 
    from_clause, 
    save_to_file,
    columns="*",
):
    """
    export a table to a csv/excel file.

    Parameters:
    - database_path (str): The path to the database.
    - from_clause (str): Name of the table to query (or complex FROM clause like JOIN).
    - columns (str or list): Columns to select, default is "*".
    - save_to_file (str, optional): If provided, saves the result to the given file path (supports .csv or .xlsx).
    
    Returns:
    - list: Query results as a list of tuples.
    """
    
    # Determine the database path
    if not os.path.exists(database_path):
        raise FileNotFoundError(f"Database '{database_path}' does not exist.")

    # Convert list of columns to a comma-separated string if necessary
    if isinstance(columns, list):
        columns = ", ".join(columns)

    # Start building the query
    query = f"SELECT {columns} FROM {from_clause}"

    # Execute query
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]
    conn.close()

    # Optionally save results to a file
    message = f"Query returned {len(results)} rows."
    df = pd.DataFrame(results, columns=column_names)
    if save_to_file.endswith('.csv'):
        df.to_csv(save_to_file, index=False)
        message+=f"\nThe return rows are save to file {save_to_file} successfully."
    elif save_to_file.endswith('.xlsx'):
        df.to_excel(save_to_file, index=False)
        message+=f"\nThe return rows are save to file {save_to_file} successfully."
    elif save_to_file.endswith(".json"):
        df.to_json(save_to_file, orient="records", force_ascii=False, indent=2)
        message+=f"\nThe return rows are save to file {save_to_file} successfully."
    elif save_to_file.endswith(".jsonl"):
        df.to_json(save_to_file, orient="records", force_ascii=False, lines=True)
        message+=f"\nThe return rows are save to file {save_to_file} successfully."
    else:
        raise ValueError("Unsupported file format. Use .csv or .xlsx")

    return message,results



if __name__ == '__main__':
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    # Example Usage
    database = "database/airlines.db"
    results = export_table_to_file(
        database_path=database,
        from_clause="aircrafts_data ORDER BY range",
        save_to_file="top_5_longest_ranges.csv"
    )
    print(results)
