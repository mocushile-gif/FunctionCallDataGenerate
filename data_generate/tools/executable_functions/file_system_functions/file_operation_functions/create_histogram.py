import matplotlib.pyplot as plt
import shutil
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

def create_histogram(data: list=None, file_path: str=None,sheet_name: str or int = 0,data_source=None, bins: int = 10, bin_range: tuple = None, color: str = 'blue', title: str = "Histogram", xlabel: str = "Values", ylabel: str = "Frequency", save_path: str = "./histogram_chart.png"):
    """
    Create a histogram based on provided data with customizations. Optionally save the histogram to a file.

    Parameters:
    - data (list): The data for which histogram needs to be plotted.
    - file_path (str): Optional path to a CSV or Excel file for loading data.
    - data_source (str or int): Column name or row index from file to use as data.
    - bins (int): The number of equal-width bins in the range. Default is 10.
    - bin_range (tuple): A tuple specifying the (min, max) range for the bins. If None, the range is automatically determined from the data.
    - color (str): The color of the bars in the histogram.
    - title (str): The title of the histogram.
    - xlabel (str): The label for the x-axis.
    - ylabel (str): The label for the y-axis.
    - save_path (str): The file path where the histogram should be saved. Default to "./histogram_chart.png"
    """

    # Load data from file if provided
    if file_path:
        df = load_data(file_path,sheet_name)
        data_raw = pd.to_numeric(df[data_source] if isinstance(data_source, str) else df.iloc[data_source], errors='coerce')
        if data_raw.isna().all():
            raise ValueError(f"Column '{data_source}' is not numeric.")
        data = data_raw.tolist()

    if bin_range is None:
        # Automatically determine the range from the data
        bin_range = (min(data), max(data))

    # Create the histogram
    plt.hist(data, bins=bins, range=bin_range, color=color, edgecolor='black', alpha=0.7)

    # Add title and labels
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    # Save the plot
    os.makedirs(os.path.dirname(save_path) or '.', exist_ok=True)
    plt.savefig(save_path)
    return {"response":f"Histogram saved to {save_path} successfully."}

# Example usage
if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    # data = [12, 15, 14, 10, 13, 14, 15, 16, 18, 18, 15, 12, 13, 11, 14]
    # save_path = "histogram.png"  # Specify the file path where you want to save the histogram
    # res=create_histogram(data, bins=5, color='green', title="Custom Histogram", xlabel="Age Group", ylabel="Number of People", save_path=save_path)
    # res=create_histogram(file_path="./excel_data/AmazingMartEU2.xlsx",sheet_name="OrderBreakdown",data_source="Quantity",bins=5, color='green', title="Custom Histogram", xlabel="Age Group", ylabel="Number of People")
    res=create_histogram(file_path="./excel_data/家电销售.xlsx",data_source="销售数量",bins=5, color='green', title="Custom Histogram", xlabel="销售数量", ylabel="Number of People")
    res=create_histogram(file_path="./json_data/311_US_universities_info.json",data_source="enrollment",bins=5, color='green', title="Custom Histogram", xlabel="销售数量", ylabel="Number of People")
    print(res)
