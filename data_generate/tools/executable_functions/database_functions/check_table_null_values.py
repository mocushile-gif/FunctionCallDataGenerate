import os
import sqlite3
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

def check_table_null_values(
    database_path: str,
    table_name: str,
    save_to_file: str = None,
):
    """
    Check NULL value counts for each column in a table of an SQLite database.

    Parameters:
    - database_path (str): Path to the SQLite DB file.
    - table_name (str): Name of the table to inspect.
    - save_to_file (str): If set, saves the result to a .csv or .xlsx file.

    Returns:
    - pd.DataFrame: A DataFrame with column names, null counts, and % missing.
    """
    if not os.path.exists(database_path):
        raise FileNotFoundError(f"Database '{database_path}' does not exist.")

    # Connect to database and read full table
    conn = sqlite3.connect(database_path)
    try:
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    except Exception as e:
        conn.close()
        raise RuntimeError(f"Failed to read table '{table_name}': {e}")
    conn.close()

    total_rows = len(df)
    null_counts = df.isnull().sum()
    percent_missing = (null_counts / total_rows * 100).round(2)

    result = pd.DataFrame({
        "Column": null_counts.index,
        "Null Count": null_counts.values,
        "Missing %": percent_missing.values,
        "Total Rows": total_rows
    })

    # Save if needed
    if save_to_file:
        os.makedirs(os.path.dirname(save_to_file) or ".", exist_ok=True)
        if save_to_file.endswith(".csv"):
            result.to_csv(save_to_file, index=False)
        elif save_to_file.endswith(".xlsx"):
            result.to_excel(save_to_file, index=False)
        elif save_to_file.endswith(".json"):
            result.to_json(save_to_file, orient="records", force_ascii=False, indent=2)
        elif save_to_file.endswith(".jsonl"):
            result.to_json(save_to_file, orient="records", force_ascii=False, lines=True)
        else:
            raise ValueError("Unsupported file format. Use .csv, .xlsx, .json, or .jsonl")

    return result

# Example usage
if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    for t in ['weekly_sales', 'shopping_cart_users', 'bitcoin_members', 'interest_metrics', 'customer_regions', 'customer_transactions', 'bitcoin_transactions', 'customer_nodes', 'cleaned_weekly_sales', 'veg_txn_df', 'shopping_cart_events', 'shopping_cart_page_hierarchy', 'bitcoin_prices', 'interest_map', 'veg_loss_rate_df', 'shopping_cart_campaign_identifier', 'veg_cat', 'veg_whsle_df', 'shopping_cart_event_identifier']:
        df_result = check_table_null_values(
            database_path="database/bank_sales_trading.sqlite",
            table_name=t,
            save_to_file="./null_check_instructors.csv"
        )
        print(df_result)
