import pandas as pd
import shutil
import os
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
        return df
    elif file_path.endswith((".xls", ".xlsx")):
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        return df
    else:
        raise ValueError("Unsupported file format. Please use a .csv, .xls, or .xlsx file.")

def calculate_column_statistics(file_path: str, sheet_name: str or int = 0,column_name: str=''):
    """
    计算Excel或CSV表格中某一数值类型列的统计信息（均值、标准差、最大值、最小值）。

    参数:
    - file_path (str): Excel文件或CSV文件的路径。
    - column_name (str): 要计算统计信息的列名。

    返回:
    - dict: 包含统计信息的字典，包括均值、标准差、最大值、最小值。
    """
    # 判断文件类型
    df = load_data(file_path, sheet_name)

    if column_name not in df.columns:
        return {"error":f"Column '{column_name}' does not exist in the DataFrame."}

    # 检查列是否为数值类型
    column_data = pd.to_numeric(df[column_name], errors='coerce')  # 无法转换为数字的值将被设置为NaN
    
    if column_data.isnull().all():  # 如果整个列都是NaN，说明该列不是数值类型
        return {'error':f"The column '{column_name}' is not numeric."}

    statistics = {
        "mean": column_data.mean(),
        "std_dev": column_data.std(),
        "max": column_data.max(),
        "min": column_data.min()
    }
    return {"response":f"Statistics for column {column_name}: {statistics}"}

# Example usage:
if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    file_path = './excel_data/BikeBuyers_Data.xlsx'
    column_name = 'Region'
    file_path = './csv_data/high_popularity_spotify_data.csv'
    column_name = 'track_popularity'
    file_path = './csv_data/Chocolate Sales.csv'
    column_name = 'Amount'
    file_path = "./excel_data/AmazingMartEU2.xlsx"
    sheet_name="OrderBreakdown"
    column_name = 'Quantity'
    stats = calculate_column_statistics(file_path, sheet_name,column_name)
    print(stats)
