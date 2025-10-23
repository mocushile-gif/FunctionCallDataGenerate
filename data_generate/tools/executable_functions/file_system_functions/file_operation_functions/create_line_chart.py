import matplotlib.pyplot as plt
import os
import pandas as pd
from dotenv import load_dotenv
load_dotenv()
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

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

def create_line_chart(
    x_data=None,
    y_data=None,
    file_path=None,
    sheet_name: str or int = 0,
    x_source=None,
    y_source=None,
    line_style='-',
    line_color='blue',
    marker='o',
    title="Line Chart",
    xlabel="X-axis",
    ylabel="Y-axis",
    legend_label=None,
    save_path="./line_chart.png",
):
    """
    Generate a customizable line chart. Supports direct list input or file-based input from CSV/Excel.

    Parameters:
    - x_data (list): Data for the x-axis (if not using file).
    - y_data (list): Data for the y-axis (if not using file).
    - file_path (str): Optional path to a CSV or Excel file for loading data.
    - x_source (str or int): Column name or row index from file to use as x-axis.
    - y_source (str or int): Column name or row index from file to use as y-axis.
    - save_path (str): Where to save the output chart image.

    Returns:
    - dict: Response message with save location.
    """

    # Load data from file if provided
    if file_path:
        df = load_data(file_path, sheet_name)
        x_raw = df[x_source] if isinstance(x_source, str) else df.iloc[x_source]
        y_raw = pd.to_numeric(df[y_source] if isinstance(y_source, str) else df.iloc[y_source], errors='coerce')
        if y_raw.isna().all():
            raise ValueError(f"Column '{y_source}' is not numeric.")
        valid = x_raw.notna() & y_raw.notna()
        x_data, y_data = x_raw[valid].tolist(), y_raw[valid].tolist()

    sorted_pairs = sorted(zip(x_data, y_data), key=lambda pair: pair[0])
    x_data, y_data = zip(*sorted_pairs)

    # Validate x/y data
    if x_data is None or y_data is None:
        raise ValueError("Both x_data and y_data must be provided, either directly or via file + source parameters.")

    # Plotting
    plt.figure(figsize=(8, 6))
    plt.plot(x_data, y_data, linestyle=line_style, color=line_color, marker=marker, label=legend_label, alpha=0.7)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    if legend_label:
        plt.legend()

    os.makedirs(os.path.dirname(save_path) or '.', exist_ok=True)
    plt.savefig(save_path)
    return {"response": f"Line chart saved to {save_path} successfully."}

# Example Usage
if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    # x_data = list(range(1, 11))
    # y_data = [5, 12, 8, 25, 18, 30, 28, 40, 35, 50]
    # res = create_line_chart(x_data, y_data, line_style='--', line_color='green', marker='x', title="Custom Line Chart", xlabel="Days", ylabel="Values", legend_label="Trend", save_path="line_chart.png")
    # print(res)

    # result = create_line_chart(
    #     file_path="./csv_data/Students_Grading_Dataset.csv",
    #     x_source="Study_Hours_per_Week",
    #     y_source="Total_Score",
    #     line_style='--',
    #     line_color='orange',
    #     marker='s',
    #     title="Daily Sales Over Time",
    #     xlabel="Date",
    #     ylabel="Sales",
    #     legend_label="Sales Trend",
    #     # save_path="sales_chart.png"
    # )

    # result = create_line_chart(
    #     file_path="./excel_data/AmazingMartEU2.xlsx",
    #     sheet_name="OrderBreakdown",
    #     x_source="Quantity",
    #     y_source="Discount",
    #     line_style='--',
    #     line_color='orange',
    #     marker='s',
    #     title="Daily Sales Over Time",
    #     xlabel="Date",
    #     ylabel="Sales",
    #     legend_label="Sales Trend",
    #     # save_path="sales_chart.png"
    # )

    result = create_line_chart(
        file_path="./csv_data/TESLA_stock_data_2024.csv",
        x_source="Date",
        y_source="Close",
        marker='s',
        title="Daily Sales Over Time",
        xlabel="Date",
        ylabel="Close",
        save_path="line_chart.png"
    )
    print(result)