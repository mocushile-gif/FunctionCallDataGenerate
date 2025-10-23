import sqlite3
import os
from dotenv import load_dotenv
load_dotenv()

def get_column_info(database_path, table_name, column_name):
    """
    Retrieve detailed information about a column in a specified table, 
    including min, max, and avg values for INTEGER columns or distinct 
    values (up to 20) for other data types.

    Parameters:
    - database_path (str): The path to the database.
    - table_name (str): The name of the table.
    - column_name (str): The name of the column to retrieve information about.

    Returns:
    - dict: A dictionary with column details and statistics.
    - str: Error message if an exception occurs.
    """
    # Connect to the database
    
    if not os.path.exists(database_path):
        raise FileNotFoundError(f"Database '{database_path}' does not exist.")
    
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    
    # Check column type
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns_info = cursor.fetchall()
    
    column_info = next((col for col in columns_info if col[1] == column_name), None)
    if not column_info:
        raise ValueError(f"Column '{column_name}' does not exist in table '{table_name}'.")
    
    data_type = column_info[2].upper()  # Column type
    
    # Prepare result structure
    result = {
        "column_name": column_name,
        "data_type": data_type,
    }
    
    if "INT" in data_type or "NUM" in data_type:  # Handle INTEGER columns
        query = f"SELECT MIN({column_name}), MAX({column_name}), AVG({column_name}) FROM {table_name}"
        cursor.execute(query)
        min_val, max_val, avg_val = cursor.fetchone()
        result.update({
            "min_value": min_val,
            "max_value": max_val,
            "avg_value": avg_val
        })
    else:  # Handle other column types
        query = f"SELECT DISTINCT {column_name} FROM {table_name}"
        cursor.execute(query)
        distinct_values = [row[0] for row in cursor.fetchall()]
        result.update({
            "distinct_values": distinct_values
        })
    
    conn.close()
    return result

if __name__ == '__main__':
    # Example Usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    database = "./database/olist_ecommerce.db"
    table = "customers"
    column = "customer_zip_code_prefix"
    info = get_column_info(database_path=database, table_name=table, column_name=column)
    print(info)
