import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()

def load_data(file_path, sheet_name=0):
    """
    Load data from an Excel or CSV file.

    Parameters:
    - file_path (str): Path to the file.
    - sheet_name (str or int): Sheet name or index for Excel files (default: first sheet).

    Returns:
    - pd.DataFrame: Loaded DataFrame.
    """
    if file_path.endswith(".csv"):
        encodings_to_try = ['utf-8', 'ISO-8859-1', 'GBK','gb2312']
        for encoding in encodings_to_try:
            try:
                df = pd.read_csv(file_path, encoding=encoding)
                break
            except UnicodeDecodeError:
                continue
        return df
    elif file_path.endswith((".xls", ".xlsx")):
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        return df
    else:
        raise ValueError("Unsupported file format. Please use a .csv, .xls, or .xlsx file.")

def count_column_values(file_path: str, column_name, sheet_name: str or int = 0):
    """
    统计 Excel / CSV 文件中某列值的出现次数。
    """

    df = load_data(file_path,sheet_name)
    if column_name not in df.columns:
        return {"error": f"Column '{column_name}' not found in file."}

    return {"response": df[column_name].value_counts().to_dict()}

# Example Usage
if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    file_path = "./csv_data/Chocolate Sales.csv"
    column_name = "Country"
    column_name = "author"
    file_path="./csv_data/TED Talks.csv"
    # sheet_name="OrderBreakdown"
    result = count_column_values(file_path, column_name)
    print(str(result['response'])[:4096])
    # print(f"Column value counts for '{column_name}':\n{result}")
