import sqlite3
import os
def create_and_populate_database(sql_file_path, database_path):
    """
    Create a SQLite database from an SQL script.

    Parameters:
    - sql_file_path (str): The path to the SQL script file.
    - database_path (str): The path where the SQLite database will be created.

    Returns:
    - A success message or an error message.
    """
    try:
        # Ensure the database directory exists
        os.makedirs(os.path.dirname(database_path), exist_ok=True)

        # Connect to the SQLite database
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        # Read and execute the SQL script
        with open(sql_file_path, "r") as f:
            sql_script = f.read()
        cursor.executescript(sql_script)

        # Check imported tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()


        # Close the connection
        conn.close()

        return f"Database created successfully at {database_path}. Tables imported: {tables}"
    except Exception as e:
        return f"Error creating database {database_path}: {str(e)}"

import sqlite3
import csv
import os

def insert_data(data_path,database_path):
    # 数据库路径和CSV文件路径
    def get_csv_files(data_path):
        """
        获取指定路径下所有 CSV 文件，并以文件名为 key，文件路径为 value。

        Args:
            data_path (str): 数据目录路径。

        Returns:
            dict: 以文件名（无扩展名）为键，文件完整路径为值的字典。
        """
        csv_files = {}
        for root, _, files in os.walk(data_path):  # 遍历路径
            for file in files:
                if file.endswith(".csv"):  # 仅处理 CSV 文件
                    file_name = os.path.splitext(file)[0]  # 去除扩展名
                    file_path = os.path.join(root, file)  # 获取完整路径
                    csv_files[file_name] = file_path  # 添加到字典
        return csv_files
    csv_files = get_csv_files(data_path)

    # 连接到SQLite数据库
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    def import_csv_to_table(table_name, csv_file_path):
        """将CSV文件的数据导入指定表中"""
        if not os.path.exists(csv_file_path):
            print(f"File {csv_file_path} does not exist!")
            return

        # 自动生成插入语句
        with open(csv_file_path, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            headers = next(reader)  # 获取CSV文件的列名
            processed_data =[]
            for row in reader:
                processed_row = []
                for item in row:
                    try:
                        # 尝试转换为整数
                        processed_row.append(int(item))
                    except ValueError:
                        # 如果不能转换，保留原始值
                        processed_row.append(item)
                processed_data.append(processed_row)
            
            placeholders = ", ".join(["?"] * len(headers))
            insert_query = f"INSERT INTO {table_name} ({', '.join(headers)}) VALUES ({placeholders})"

            # 插入数据
            for row in processed_data:
                # print(row)
                try:
                    cursor.execute(insert_query, row)
                except Exception as e:
                    print(row)
                    print(str(e))
                    break
            conn.commit()
            print(f"Data imported into table '{table_name}' from {csv_file_path}")

    # 批量导入所有表的数据
    for table, csv_path in csv_files.items():
        import_csv_to_table(table, csv_path)

    # 关闭数据库连接
    cursor.close()
    conn.close()

# sql_file_path='./agent/working_dir/database/Chinook_Sqlite.sql'
# database_path='./agent/working_dir/database/chinook.db'
# print(create_and_populate_database(sql_file_path, database_path))

# sql_file_path='./agent/working_dir/database/sakila_sqlite.sql'
# database_path='./agent/working_dir/database/sakila.db'
# print(create_and_populate_database(sql_file_path, database_path))

sql_file_path='./agent/working_dir/database/uw_courses.sql'
database_path='./agent/working_dir/database/uw_courses.db'
data_path='./agent/working_dir/database/uw_courses'
print(create_and_populate_database(sql_file_path, database_path))
insert_data(data_path,database_path)
