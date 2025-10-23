import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()

def get_column_unique_values(file_path: str, column_name: str, sheet_name: str or int =0):
    """
    获取 Excel / CSV 文件中特定列的唯一值。
    """

    if file_path.endswith(('.xlsx', '.xls')):
        df = pd.read_excel(file_path,sheet_name)
    else:
        encodings_to_try = ['utf-8', 'ISO-8859-1', 'GBK','gb2312']
        for encoding in encodings_to_try:
            try:
                df = pd.read_csv(file_path, encoding=encoding)
                break
            except UnicodeDecodeError:
                continue
    if column_name not in df.columns:
        return {"error": f"Column '{column_name}' not found in file."}

    return {"response": df[column_name].dropna().unique().tolist()}

# Example Usage
if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    file_path = "./excel_data/BikeBuyers_Data.xlsx"
    column_name = "Region"

    file_path = "./csv_data/1000_ml_jobs_us.csv"
    column_name = "company_name"

    file_path = "./excel_data/AmazingMartEU2.xlsx"
    sheet_name="OrderBreakdown"
    column_name = "Quantity"

    result = get_column_unique_values(file_path, column_name, sheet_name)
    print(f"Unique values in column '{column_name}':\n{result}")
