import sqlite3
import os
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

def execute_sql_command(database_path, query, save_to_file=None, create_temp_table=None):
    """
    Executes an SQL query on the specified SQLite database.

    Parameters:
    - database_path (str): Path to the SQLite database.
    - query (str): The SQL query to execute.
    - save_to_file (str, optional): Path to save result (.csv or .xlsx). Only used for SELECT.
    - create_temp_table (str, optional): Name of TEMP table to store SELECT results.

    Returns:
    - tuple: (True/False, results or error message)
    """
    
    if not os.path.exists(database_path):
        return False, f"Database '{database_path}' does not exist."

    conn = sqlite3.connect(database_path)
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()

        if query.strip().lower().startswith("select"):
            column_names = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(results, columns=column_names)

            msg = f"Query returned {len(df)} rows."

            if create_temp_table:
                df.to_sql(create_temp_table, conn, if_exists='replace', index=False)
                msg += f" Temporary table '{create_temp_table}' created."

            if save_to_file:
                if save_to_file.endswith(".csv"):
                    df.to_csv(save_to_file, index=False)
                    msg += f" Result saved to file: {save_to_file}"
                elif save_to_file.endswith(".xlsx"):
                    df.to_excel(save_to_file, index=False)
                    msg += f" Result saved to file: {save_to_file}"
                else:
                    return False, "Unsupported file format for save_to_file. Use .csv or .xlsx."
            msg+="\n"
            return True, msg, results
        else:
            conn.commit()
            return True, "Query executed successfully.", results

    except Exception as e:
        return False, str(e), None

    finally:
        conn.close()


if __name__ == '__main__':
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    db = "./database/uw_courses.db"
    sql = """
    PRAGMA table_info(schedules)
    """
    output = execute_sql_command(
        database_path=db,
        query=sql,
        # save_to_file="./query_result.csv",
        # create_temp_table="temp_clients_single"
    )
    print("Output:", output)
