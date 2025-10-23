import sqlite3
import os
from dotenv import load_dotenv
load_dotenv()

def format_bytes(size: int) -> str:
    """将字节大小格式化为人类可读的单位字符串"""
    for unit in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024 or unit == 'TB':
            return f"{size:.2f} {unit}" if unit != 'bytes' else f"{size} {unit}"
        size /= 1024

def get_database_size(database_path):
    """
    Retrieve the size of the SQLite database in bytes.

    Parameters:
    - database_path (str): The path to the database.

    Returns:
    - int: The size of the database in bytes.
    - str: Error message if an exception occurs.
    """
    
    if not os.path.exists(database_path):
        raise FileNotFoundError(f"Database '{database_path}' does not exist.")

    size_bytes = os.path.getsize(database_path)
    size_human = format_bytes(size_bytes)

    return size_bytes, size_human

if __name__ == '__main__':
    # Example Usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    database = "database/airlines.db"
    info = get_database_size(database)
    print(info)