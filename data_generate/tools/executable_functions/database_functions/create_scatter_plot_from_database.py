import os
import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
from typing import List, Any
from dotenv import load_dotenv
load_dotenv()

def create_scatter_plot_from_database(
    database_path: str,
    from_clause: str,
    x_column: str,
    y_column: str,
    where_clause: str = None,
    where_params: List[Any] = None,
    color: str = "blue",
    marker: str = "o",
    title: str = "Line Chart",
    xlabel: str = "X-axis",
    ylabel: str = "Y-axis",
    legend_label: str = None,
    save_path: str = "./scatter_plot.png",
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
    - color (str): Color of the markers.
    - marker (str): Marker style (e.g., 'o', '^', 's').
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
    df[x_column] = pd.to_numeric(df[x_column], errors='coerce')
    df[y_column] = pd.to_numeric(df[y_column], errors='coerce')
    if df[x_column].isna().all():
        raise ValueError(f"Column '{x_column}' is not numeric.")
    if df[x_column].isna().all():
        raise ValueError(f"Column '{y_column}' is not numeric.")
    df.dropna(inplace=True)

    if df.empty:
        raise ValueError("No valid numeric data available for line chart.")

    df.sort_values(by=x_column, inplace=True)

    # Plot
    plt.figure(figsize=(8, 6))
    plt.scatter(df[x_column], df[y_column], color=color, marker=marker, alpha=0.7, label=legend_label)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
    plt.savefig(save_path)
    plt.close()

    return {"response": f"Scatter plot saved to {save_path} successfully."}

if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    # result = create_scatter_plot_from_database(
    #     database_path="database/bank_sales_trading.sqlite",
    #     from_clause="weekly_sales",
    #     x_column="transactions",
    #     y_column="sales",
    #     where_clause="region = ?",
    #     where_params=["ASIA"],
    #     color="green",
    #     marker="x",
    #     title="Actual vs Scheduled Departure",
    #     xlabel="Scheduled Time",
    #     ylabel="Actual Time",
    #     save_path="./charts/departure_scatter_plot.png"
    # )
    result = create_scatter_plot_from_database(
        database_path="database/BowlingLeague.sqlite",
        from_clause="Bowler_Scores",
        x_column="RawScore",
        y_column="HandiCapScore",
        where_clause="WonGame = ?",
        where_params=["1"],
        color="green",
        marker="x",
        title="Actual vs Scheduled Departure",
        xlabel="Scheduled Time",
        ylabel="Actual Time",
        save_path="./departure_scatter_plot.png"
    )
    # "{\"database_path\":\"./database/BowlingLeague.sqlite\",\"from_clause\":\"Bowler_Scores\",\"x_column\":\"RawScore\",\"y_column\":\"HandiCapScore\",\"where_clause\":\"WonGame = ?\",\"where_params\":[\"1\"],\"title\":\"Scatter Plot of RawScore vs HandiCapScore for Winners\",\"xlabel\":\"RawScore\",\"ylabel\":\"HandiCapScore\",\"save_path\":\"./scatter_plot.png\"}", "name": "create_scatter_plot_from_database"}, "id": "call_v2STcfRwB73cVvvPrKwVtAiL",
    print(result)
