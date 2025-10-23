import matplotlib.pyplot as plt
import os
import pandas as pd
from dotenv import load_dotenv
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

def create_bar_chart(
    categories=None, values=None, file_path=None, sheet_name=0,
    category_col=None, value_col=None, agg_method='sum',
    color='blue', title="Bar Chart", xlabel="Categories", ylabel="Values",
    save_path='./bar_chart.png'
):

    """
    Generate a customizable bar chart, optionally loading data from file.

    Parameters:
    - categories (list): Categories for the x-axis.
    - values (list): Values corresponding to categories.
    - file_path (str): Optional file to load categories/values from.
    - sheet_name (str or int): Sheet name or index for Excel files.
    - category_col (str): Column name to use as x-axis categories (when loading from file).
    - value_col (str): Column name to use as y-axis values (when loading from file).
    - agg_method: Aggregation method if grouping ('sum', 'mean', 'count').
    - color (str): Bar color.
    - title (str): Chart title.
    - xlabel (str): Label for x-axis.
    - ylabel (str): Label for y-axis.
    - save_path (str): Path to save the bar chart image.
    """

    # Load data from file if specified
    if file_path and category_col and value_col:
        
        df = load_data(file_path, sheet_name)
        df[category_col] = df[category_col] if isinstance(category_col, str) else df.iloc[category_col].tolist()
        df[value_col] = pd.to_numeric(df[value_col] if isinstance(value_col, str) else df.iloc[value_col], errors='coerce')
        if df[value_col].isna().all():
            raise ValueError(f"Column '{value_col}' is not numeric.")
        df = df[[category_col, value_col]]

        if agg_method == 'sum':
            df = df.groupby(category_col, as_index=False)[value_col].sum()
        elif agg_method == 'mean':
            df = df.groupby(category_col, as_index=False)[value_col].mean()
        elif agg_method == 'count':
            df = df.groupby(category_col, as_index=False)[value_col].count()

        plt.figure(figsize=(8, 6))
        plt.bar(df[category_col], df[value_col], color=color, edgecolor='black', alpha=0.7)
    else:
        plt.figure(figsize=(8, 6))
        plt.bar(categories, values, color=color, edgecolor='black', alpha=0.7)

    
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    plt.xticks(rotation=45)  # 防止标签重叠

    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path) or '.', exist_ok=True)
    plt.savefig(save_path)
    return {"response": f"Bar chart saved to {save_path} successfully."}

if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    res = create_bar_chart(
        categories=["A", "B", "C"], 
        values=[10, 20, 15], 
        color='skyblue', 
        title="Demo Bar", 
        xlabel="Label", 
        ylabel="Score", 
        # save_path="./bar_chart1.png"
    )
    print(res)

    res = create_bar_chart(
        file_path="./excel_data/家电销售.xlsx",
        category_col="商品名称",
        value_col="销售数量",
        title="家电销售图",
        xlabel="产品",
        ylabel="销量",
        color="orange",
        # save_path="./bar_chart2.png"
    )

    result = create_bar_chart(
        file_path="./excel_data/IMDB Movie Top 1000.xlsx",
        category_col="Genre",
        value_col="Rating",
        title="Daily Sales Over Time",
        xlabel="Date",
        ylabel="Sales",
        # save_path="sales_chart.png"
    )
    result = create_bar_chart(
        file_path="./json_data/311_US_universities_info.json",
        category_col="state",
        value_col="enrollment",
        title="Daily Sales Over Time",
        xlabel="Date",
        ylabel="Sales",
        save_path="sales_chart.png"
    )
    print(result)
