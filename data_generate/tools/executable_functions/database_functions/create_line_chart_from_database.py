import os
import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
from typing import List, Any
from dotenv import load_dotenv
load_dotenv()

def create_line_chart_from_database(
    database_path: str,
    from_clause: str,
    x_column: str,
    y_column: str,
    where_clause: str = None,
    where_params: List[Any] = None,
    line_style: str = "-",
    line_color: str = "blue",
    marker: str = "o",
    title: str = "Line Chart",
    xlabel: str = "X-axis",
    ylabel: str = "Y-axis",
    legend_label: str = None,
    save_path: str = "./line_chart.png",
):
    """
    Generate a line chart from two columns of an SQLite database.

    Parameters:
    - database_path (str): Path to SQLite DB file.
    - from_clause (str): Table or JOIN clause.
    - x_column (str): Column to use as x-axis.
    - y_column (str): Column to use as y-axis.
    - where_clause (str): Optional WHERE clause (without 'WHERE').
    - where_params (List[Any]): Parameters for WHERE clause.
    - line_style (str): Line style (e.g., '-', '--', ':').
    - line_color (str): Line color.
    - marker (str): Point marker.
    - title (str): Chart title.
    - xlabel (str): Label for x-axis.
    - ylabel (str): Label for y-axis.
    - save_path (str): Where to save image.

    Returns:
    - dict: Confirmation message with image path.
    """

    if not os.path.exists(database_path):
        raise FileNotFoundError(f"Database not found at: {database_path}")

    # Construct SQL query
    query = f"SELECT {x_column}, {y_column} FROM {from_clause}"
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

    x_column=x_column.split('.')[-1]
    y_column=y_column.split('.')[-1]
    # Load and clean data
    df = pd.DataFrame(rows, columns=[x_column, y_column])
    df[y_column] = pd.to_numeric(df[y_column], errors='coerce')
    if df[x_column].isna().all():
        raise ValueError(f"Column '{y_column}' is not numeric.")
    df.dropna(inplace=True)

    if df.empty:
        raise ValueError("No valid numeric data available for line chart.")

    df.sort_values(by=x_column, inplace=True)

    # Plot
    plt.figure(figsize=(8, 6))
    plt.plot(df[x_column][:10000], df[y_column][:10000], linestyle=line_style, color=line_color, marker=marker, label=legend_label, alpha=0.8)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
    plt.savefig(save_path)
    plt.close()

    return {"response": f"Line chart saved to {save_path} successfully."}

if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    # "database_path":"database/electronic_sales.sqlite","from_clause":"order_items","x_column":"shipping_limit_date","y_column":"price","title":"Price Trend Over Time","xlabel":"Shipping Limit Date","ylabel":"Price"
    result = create_line_chart_from_database(
        database_path="database/electronic_sales.sqlite",
        from_clause="order_items",
        x_column="shipping_limit_date",
        y_column="price",
        # where_clause="region = ?",
        # where_params=["ASIA"],
        line_style="--",
        line_color="green",
        marker="x",
        title="Actual vs Scheduled Departure",
        xlabel="Scheduled Time",
        ylabel="Actual Time",
        save_path="./charts/departure_line_chart.png"
    )
    # result = create_line_chart_from_database(
    #     database_path="database/BowlingLeague.sqlite",
    #     from_clause="Bowlers",
    #     x_column="BowlerGamesBowled",
    #     y_column="BowlerTotalPins",
    #     line_style="--",
    #     line_color="green",
    #     marker="x",
    #     title="Actual vs Scheduled Departure",
    #     xlabel="Scheduled Time",
    #     ylabel="Actual Time",
    #     save_path="./charts/departure_line_chart.png"
    # )
    print(result)
