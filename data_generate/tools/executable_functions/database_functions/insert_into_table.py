import sqlite3
import os
from dotenv import load_dotenv
load_dotenv()

def infer_sqlite_type(value):
    if isinstance(value, int):
        return "INTEGER"
    elif isinstance(value, float):
        return "REAL"
    elif value is None:
        return "TEXT"  # 默认给 null 值 TEXT 类型
    else:
        return "TEXT"

def insert_into_table(database_path, table_name, columns, values):

    if len(columns) != len(values):
        raise ValueError("Number of columns and values must match.")

    if not os.path.exists(database_path):
        raise FileNotFoundError(f"Database '{database_path}' does not exist.")

    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # 检查表是否存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table_name,))
    table_exists = cursor.fetchone()

    if not table_exists:
        # 自动构造建表语句
        col_defs = []
        for col, val in zip(columns, values):
            col_type = infer_sqlite_type(val)
            col_defs.append(f"{col} {col_type}")
        create_stmt = f"CREATE TABLE {table_name} ({', '.join(col_defs)});"
        cursor.execute(create_stmt)

    # 构造插入语句
    column_str = ", ".join(columns)
    placeholders = ", ".join("?" for _ in values)
    query = f"INSERT INTO {table_name} ({column_str}) VALUES ({placeholders})"
    cursor.execute(query, values)

    conn.commit()
    affected_rows = cursor.rowcount
    conn.close()

    return f"The number of rows affected: {affected_rows}"
