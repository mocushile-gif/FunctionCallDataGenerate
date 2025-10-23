import os
import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
from typing import List, Any
from dotenv import load_dotenv
load_dotenv()

def create_pie_chart_from_database(
    database_path: str,
    from_clause: str,
    label_column: str,
    value_column: str,
    where_clause: str = None,
    where_params: List[Any] = None,
    title: str = "Pie Chart",
    save_path: str = "./pie_chart.png",
    agg_method: str = "sum",
):
    """
    Generate a pie chart from grouped and aggregated values of an SQLite database table.

    Parameters:
    - database_path (str): Path to SQLite DB file.
    - from_clause (str): Table or JOIN clause.
    - label_column (str): Column to use as labels (categories).
    - value_column (str): Column to use as values (numerical).
    - where_clause (str): Optional WHERE clause (without 'WHERE').
    - where_params (List[Any]): Parameters for WHERE clause.
    - title (str): Title of the pie chart.
    - save_path (str): Path to save the pie chart image.
    - agg_method (str): Aggregation method ('sum', 'mean', 'count').

    Returns:
    - dict: Confirmation message with image path.
    """

    if not os.path.exists(database_path):
        raise FileNotFoundError(f"Database not found at: {database_path}")
    
    # Load and clean data
    if agg_method == "count":
        # Construct SQL query
        query = f"SELECT {label_column} FROM {from_clause}"
        if where_clause:
            query += f" WHERE {where_clause}"

        # Query data
        conn = sqlite3.connect(database_path)
        try:
            cursor = conn.cursor()
            cursor.execute(query, where_params or [])
            rows = cursor.fetchall()
        finally:
            conn.close()
        df = pd.DataFrame(rows, columns=[label_column])
        df = df.groupby(label_column, as_index=False).size().rename(columns={'size': 'count'})
        plt.figure(figsize=(8, 6))
        plt.pie(df['count'], labels=df[label_column], autopct='%1.1f%%', startangle=140)
    # Group and aggregate
    elif agg_method in ["sum","mean"]:
        # Construct SQL query
        query = f"SELECT {label_column}, {value_column} FROM {from_clause}"
        if where_clause:
            query += f" WHERE {where_clause}"

        # Query data
        conn = sqlite3.connect(database_path)
        try:
            cursor = conn.cursor()
            cursor.execute(query, where_params or [])
            rows = cursor.fetchall()
        finally:
            conn.close()

        label_column=label_column.split('.')[-1]
        value_column=value_column.split('.')[-1]
        
        df = pd.DataFrame(rows, columns=[label_column, value_column])
        df[value_column] = pd.to_numeric(df[value_column], errors='coerce')
        df.dropna(inplace=True)
        if df.empty:
            raise ValueError("No valid numeric data available for pie chart.")
        if agg_method == "sum":
            df = df.groupby(label_column, as_index=False)[value_column].sum()
        elif agg_method == "mean":
            df = df.groupby(label_column, as_index=False)[value_column].mean()
        plt.figure(figsize=(8, 6))
        plt.pie(df[value_column], labels=df[label_column], autopct='%1.1f%%', startangle=140)
    else:
        raise ValueError(f"Unsupported aggregation method: {agg_method}")

    # Plot
    plt.title(title)
    plt.axis('equal')

    os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
    plt.savefig(save_path)
    plt.close()

    return {"response": f"Pie chart saved to {save_path} successfully."}

if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    # result = create_pie_chart_from_database(
    #     database_path="database/bank_sales_trading.sqlite",
    #     from_clause="weekly_sales",
    #     label_column="region",
    #     value_column="sales",
    #     title="Sales Distribution by Region",
    #     save_path="./charts/sales_pie_chart.png"
    # )
    result = create_pie_chart_from_database(
        database_path="./database/uw_courses.db",
        from_clause="teachings INNER JOIN instructors ON teachings.instructor_id = instructors.id",
        label_column="name",
        value_column="section_uuid",
        agg_method="count",
        title="Sales Distribution by Region",
        save_path="./charts/sales_pie_chart.png"
    )
    print(result)

# {'function': {'arguments': '{"database_path": "./database/sakila.db", "from_clause": "rental INNER JOIN customer ON rental.customer_id = customer.customer_id", "label_column": "first_name || \' \' || last_name", "value_column": "customer_id", "agg_method": "count", "save_path": "./sakila_total_rentals_pie_chart.png", "title": "Total Rentals by Each Customer"}', 'name': 'create_pie_chart_from_database'},
#  'id': 'call_D3y81VPUEPGGkgEwJawm79fw', 'type': 'function'}