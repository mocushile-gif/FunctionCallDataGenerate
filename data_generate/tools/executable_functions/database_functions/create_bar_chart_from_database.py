import os
import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
from typing import List, Any
from dotenv import load_dotenv
load_dotenv()

def create_bar_chart_from_database(
    database_path: str,
    from_clause: str,
    x_column: str,
    y_column: str,
    where_clause: str = None,
    where_params: List[Any] = None,
    agg_method: str = "sum",
    bar_color: str = "skyblue",
    title: str = "Bar Chart",
    xlabel: str = "X-axis",
    ylabel: str = "Y-axis",
    legend_label: str = None,
    save_path: str = "./bar_chart.png",
):
    """
    Generate a bar chart from two columns of an SQLite database.

    Parameters:
    - database_path (str): Path to SQLite DB file.
    - from_clause (str): Table or JOIN clause.
    - x_column (str): Column to use as x-axis (categories or values).
    - y_column (str): Column to use as y-axis (numerical values).
    - where_clause (str): Optional WHERE clause (without 'WHERE').
    - where_params (List[Any]): Parameters for WHERE clause.
    - bar_color (str): Bar color.
    - title (str): Chart title.
    - xlabel (str): Label for x-axis.
    - ylabel (str): Label for y-axis.
    - legend_label (str): Optional legend label.
    - save_path (str): Where to save image.

    Returns:
    - dict: Confirmation message with image path.
    """

    if not os.path.exists(database_path):
        raise FileNotFoundError(f"Database not found at: {database_path}")

    query = f"SELECT {x_column}, {y_column} FROM {from_clause}"
    if where_clause:
        query += f" WHERE {where_clause}"

    conn = sqlite3.connect(database_path)
    try:
        cursor = conn.cursor()
        cursor.execute(query, where_params or [])
        rows = cursor.fetchall()
    finally:
        conn.close()

    x_column=x_column.split('.')[-1]
    y_column=y_column.split('.')[-1]
    
    df = pd.DataFrame(rows, columns=[x_column, y_column])
    df[y_column] = pd.to_numeric(df[y_column], errors='coerce')
    df.dropna(inplace=True)

    if df.empty:
        raise ValueError(f"Column '{y_column}' is not numeric.")
    
    # Group and aggregate
    if agg_method == "sum":
        df = df.groupby(x_column, as_index=False)[y_column].sum()
    elif agg_method == "mean":
        df = df.groupby(x_column, as_index=False)[y_column].mean()
    elif agg_method == "count":
        df = df.groupby(x_column, as_index=False)[y_column].count()
    else:
        raise ValueError(f"Unsupported aggregation method: {agg_method}")

    df.sort_values(by=x_column, inplace=True)

    # Plot
    plt.figure(figsize=(10, 6))
    plt.bar(df[x_column], df[y_column], color=bar_color, label=legend_label)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    if legend_label:
        plt.legend()

    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
    plt.savefig(save_path)
    plt.close()

    return {"response": f"Bar chart saved to {save_path} successfully."}

if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    result = create_bar_chart_from_database(
        database_path="database/bank_sales_trading.sqlite",
        from_clause="weekly_sales",
        x_column="region",
        y_column="sales",
        where_clause="customer_type = ?",
        where_params=["New"],
        bar_color="orange",
        title="Weekly Sales in Asia",
        xlabel="Transaction Count",
        ylabel="Total Sales",
        legend_label="Sales Volume",
        save_path="./charts/asia_sales_barchart.png"
    )
    result = create_bar_chart_from_database(
        database_path="database/BowlingLeague.sqlite",
        from_clause="Bowlers",
        x_column="BowlerGamesBowled",
        y_column="BowlerTotalPins",
        bar_color="orange",
        title="Weekly Sales in Asia",
        xlabel="Transaction Count",
        ylabel="Total Sales",
        legend_label="Sales Volume",
        save_path="./charts/asia_sales_barchart.png"
    )
    print(result)
