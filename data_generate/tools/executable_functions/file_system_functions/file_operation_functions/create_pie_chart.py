import matplotlib.pyplot as plt
import os
import pandas as pd
from dotenv import load_dotenv
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

def create_pie_chart(labels=None, sizes=None, file_path=None, sheet_name=0, 
    category_col=None, value_col=None, agg_method='sum',
    title="Pie Chart", save_path=None):

    """
    Generate a customizable pie chart.

    Parameters:
    - labels (list): Labels for each slice.
    - sizes (list): Size of each slice.
    - file_path (str): Optional file to load categories/values from.
    - sheet_name (str or int): Sheet name or index for Excel files.
    - category_col (str): Column name to use as x-axis categories (when loading from file).
    - value_col (str): Column name to use as y-axis values (when loading from file).
    - agg_method: Aggregation method if grouping ('sum', 'mean', 'count').
    - title (str): Title of the pie chart.
    - save_path (str): Path to save the pie chart image.
    """
    # Load data from file if specified
    if file_path and category_col and (value_col or agg_method == 'count'):
        
        df = load_data(file_path, sheet_name)
        df[category_col] = df[category_col] if isinstance(category_col, str) else df.iloc[category_col].tolist()

        if agg_method == 'count':
            df = df[[category_col]]
            df = df.groupby(category_col, as_index=False).size().rename(columns={'size': 'count'})
            labels = df[category_col]
            sizes = df['count']
        else:
            df[value_col] = pd.to_numeric(df[value_col].str.replace(',', '') if isinstance(value_col, str) else df.iloc[value_col], errors='coerce')
            if df[value_col].dropna().empty:
                raise ValueError(f"Column '{value_col}' is not numeric.")
            df = df[[category_col, value_col]]

            if agg_method == 'sum':
                df = df.groupby(category_col, as_index=False)[value_col].sum()
            elif agg_method == 'mean':
                df = df.groupby(category_col, as_index=False)[value_col].mean()

            labels = df[category_col]
            sizes = df[value_col]

    plt.figure(figsize=(8, 6))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True, startangle=140)
    plt.title(title)

    if not save_path:
        save_path = './pie_chart.png'

    os.makedirs(os.path.dirname(save_path) or '.', exist_ok=True)
    plt.savefig(save_path)
    return {"response": f"Pie chart saved to {save_path} successfully."}

# Example Usage
if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    labels = ['Category A', 'Category B', 'Category C', 'Category D']
    sizes = [0.0919, 0.0869, 0.0806, 0.0742]
    # colors = ['blue', 'green', 'red', 'purple']
    # explode = (0, 0.1, 0, 0)  # Highlight second slice
    arguments={"file_path":"./json_data/Top 100 Largest Banks.json", "category_col": "Bank Name", "value_col": "Total Assets (2023, US$ billion)", "save_path": "./csv_data/top_10_banks_pie_chart.png", "title": "Top 10 Banks by Total Assets", "agg_method": "sum"}
    # res = create_pie_chart(labels=labels, sizes=sizes, title="Custom Pie Chart", save_path="pie_chart.png")
    # res = create_pie_chart(
    #     file_path="./csv_data/Students_Grading_Dataset.csv",
    #     category_col="Grade",
    #     agg_method='count',
    #     title="Custom Pie Chart",
    #     save_path="sales_chart.png"
    # )
    res = create_pie_chart(
        **arguments
    )
    print(res)
