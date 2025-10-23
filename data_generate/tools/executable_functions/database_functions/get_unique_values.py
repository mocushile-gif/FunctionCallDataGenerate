import sqlite3
import os
from dotenv import load_dotenv
load_dotenv()

def get_unique_values(database_path, table_name, column_name):
    """
    Retrieve unique values of a column in a specified table.

    Parameters:
    - database_path (str): The path to the database.
    - table_name (str): The name of the table.
    - column_name (str): The name of the column to query.

    Returns:
    - list: A list of unique values.
    - str: Error message if an exception occurs.
    """

    query = f"SELECT DISTINCT {column_name} FROM {table_name}"
    
    if not os.path.exists(database_path):
        raise FileNotFoundError(f"Database '{database_path}' does not exist.")
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(query)
    unique_values = cursor.fetchall()
    conn.close()

    return f'Get {len(unique_values)} unique values of column {column_name} in table {table_name} from database {database_path}',unique_values

if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    database_path = "database/sakila.db"   # 你的数据库路径
    table_name = "film1"
    column_name = "release_year"
    database_path = "./database/olist_ecommerce.db"
    table_name = "customers"
    column_name = "customer_zip_code_prefix"
    unique_years = get_unique_values(database_path, table_name, column_name)
    print(str(unique_years)[:100])

