import os
import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
from typing import List, Any
from dotenv import load_dotenv
load_dotenv()

def create_histogram_from_database(
    database_path: str,
    from_clause: str,
    column_to_plot: str,
    where_clause: str = None,
    where_params: List[Any] = None,
    bins: int = 10,
    title: str = "Histogram",
    xlabel: str = "Values",
    ylabel: str = "Frequency",
    save_path: str = "./histogram_chart.png",
):
    """
    Perform a SELECT query on SQLite and generate a histogram from a target column.

    Parameters:
    - database_path (str): Path to SQLite DB.
    - from_clause (str): Table or JOIN clause.
    - column_to_plot (str): Name of the numeric column to plot.
    - where_clause (str): Optional WHERE clause without the 'WHERE' keyword.
    - where_params (list): Parameters to bind to the WHERE clause.
    - bins (int): Number of bins for the histogram.
    - title (str): Plot title.
    - xlabel (str): X-axis label.
    - ylabel (str): Y-axis label.
    - save_path (str): Path to save the histogram image.

    Returns:
    - dict: Message including saved path.
    """

    if not os.path.exists(database_path):
        raise FileNotFoundError(f"Database '{database_path}' does not exist.")

    # --- Build query ---
    query = f"SELECT {column_to_plot} FROM {from_clause}"
    if where_clause:
        query += f" WHERE {where_clause}"
        
    # --- Run query ---
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(query, where_params or [])
    results = cursor.fetchall()
    column_data = [row[0] for row in results if row[0] is not None]
    conn.close()

    if not column_data:
        raise ValueError("No valid data returned for plotting.")

    # --- Plot histogram ---
    plt.figure()
    plt.hist(column_data, bins=bins, color='skyblue', edgecolor='black', alpha=0.75)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
    plt.savefig(save_path)
    plt.close()

    return {"response": f"Histogram saved to {save_path} successfully."}

if __name__ == '__main__':
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    database = "database/BowlingLeague.sqlite"
    table = "Bowlers"
    column = "BowlerTotalPins"
    res = create_histogram_from_database(
        database_path="database/BowlingLeague.sqlite",
        from_clause="Bowlers",
        column_to_plot="BowlerTotalPins",
        # where_clause="region = ?",
        # where_params=["ASIA"],
        bins=15,
        title="Departure Time Histogram",
        xlabel="Time",
        ylabel="Flights",
        save_path="./charts/departure_hist.png"
    )
    print(res)
