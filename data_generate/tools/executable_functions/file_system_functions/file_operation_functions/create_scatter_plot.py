import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv
import pandas as pd
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
load_dotenv()


def load_data(file_path, sheet_name=0):
    if file_path.endswith(".csv"):
        encodings_to_try = ['utf-8', 'ISO-8859-1', 'GBK', 'gb2312']
        for encoding in encodings_to_try:
            try:
                df = pd.read_csv(file_path, encoding=encoding)
                break
            except UnicodeDecodeError:
                continue
    elif file_path.endswith((".xls", ".xlsx")):
        df = pd.read_excel(file_path, sheet_name=sheet_name)
    elif file_path.endswith(".json"):
        df = pd.read_json(file_path)
    elif file_path.endswith(".jsonl"):
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = [json.loads(line.strip()) for line in f]
        df = pd.DataFrame(lines)
    else:
        raise ValueError("Unsupported file format. Please use a .csv, .xls, or .xlsx file.")
    return df

def create_scatter_plot(
    x_data=None,
    y_data=None,
    file_path=None,
    sheet_name: str or int = 0,
    x_source=None,
    y_source=None,
    color='blue', 
    marker='o', 
    title="Scatter Plot", 
    xlabel="X-axis", 
    ylabel="Y-axis", 
    grid=True, 
    save_path='./scatter_plot.png', 
    ):

    
    """
    Generate a scatter plot with customizable options.

    Parameters:
    - x_data (list): Data for the x-axis.
    - y_data (list): Data for the y-axis.
    - file_path (str): Optional path to a file for loading data.
    - sheet_name (str or int): Sheet name or index for Excel files.
    - x_source (str or int): Column name or row index from file to use as x-axis.
    - y_source (str or int): Column name or row index from file to use as y-axis.
    - color (str): Color of the markers.
    - marker (str): Marker style (e.g., 'o', '^', 's').
    - title (str): Title of the scatter plot.
    - xlabel (str): Label for the x-axis.
    - ylabel (str): Label for the y-axis.
    - grid (bool): Whether to show a grid.
    - save_path (str): Path to save the scatter plot image.
    """

    # Load data from file if provided
    if file_path:
        df = load_data(file_path, sheet_name)
        x_raw = pd.to_numeric(df[x_source] if isinstance(x_source, str) else df.iloc[x_source], errors='coerce')
        y_raw = pd.to_numeric(df[y_source] if isinstance(y_source, str) else df.iloc[y_source], errors='coerce')
        if x_raw.isna().all():
            raise ValueError(f"Column '{x_source}' is not numeric.")
        if y_raw.isna().all():
            raise ValueError(f"Column '{y_source}' is not numeric.")
        valid = x_raw.notna() & y_raw.notna()
        x_data, y_data = x_raw[valid].tolist(), y_raw[valid].tolist()

    plt.figure(figsize=(8, 6))
    plt.scatter(x_data, y_data, color=color, marker=marker, alpha=0.7, edgecolors='black')
    
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    if grid:
        plt.grid(True, linestyle='--', alpha=0.6)
    
    os.makedirs(os.path.dirname(save_path) or '.', exist_ok=True)
    plt.savefig(save_path)
    return {"response": f"Scatter plot saved to {save_path} successfully."}

# Example Usage
if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    # x_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    # y_data = [10, 20, 15, 30, 25, 40, 35, 50, 45, 60]
    # res = create_scatter_plot(x_data, y_data, color='red', marker='s', title="Custom Scatter", xlabel="Index", ylabel="Value", save_path="scatter_plot.png")
    # print(res)

    # res = create_scatter_plot(        file_path="./csv_data/Students_Grading_Dataset.csv",
    #     x_source="Study_Hours_per_Week",
    #     y_source="Total_Score", color='red', marker='s', title="Custom Scatter", xlabel="Index", ylabel="Value", save_path="scatter_plot.png")

    # res = create_scatter_plot(        file_path="./csv_data/Goodreads Choice Awards 2024 Top Book Dataset.csv",
    #     x_source="num_ratings",
    #     y_source="five_star_percentage", color='red', marker='s', title="Custom Scatter", xlabel="Index", ylabel="Value", save_path="scatter_plot.png")

    result = create_scatter_plot(
        file_path="./excel_data/AmazingMartEU2.xlsx",
        sheet_name="OrderBreakdown",
        x_source="Quantity",
        y_source="Discount",
        color='orange',
        marker='s',
        title="Daily Sales Over Time",
        xlabel="Date",
        ylabel="Sales",
        # save_path="sales_chart.png"
    )


    result = create_scatter_plot(
        file_path="./json_data/311_US_universities_info.json",
        x_source="overallRank",
        y_source="enrollment",
        color='orange',
        marker='s',
        title="Daily Sales Over Time",
        xlabel="Date",
        ylabel="Sales",
        # save_path="sales_chart.png"
    )

    print(result)