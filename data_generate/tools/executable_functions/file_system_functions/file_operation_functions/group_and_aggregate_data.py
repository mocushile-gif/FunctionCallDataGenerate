import pandas as pd
import shutil
import os
from dotenv import load_dotenv
load_dotenv()

def group_and_aggregate_data(file_path: str, group_by_column: str, agg_column: str, agg_func: str,sheet_name: str or int=0,save_as: str = None, sort_type: int = 0,):

    """
    按指定列分组并对另一列进行聚合，支持Excel文件和CSV文件。

    参数:
    - file_path (str): 文件的路径（可以是Excel文件或CSV文件）。
    - group_by_column (str): 用于分组的列名。
    - agg_column (str): 要聚合的列名。
    - agg_func (str): 聚合函数，如 'sum', 'mean', 'max', 'min'。
    - save_as (str): 可选参数，保存分组聚合结果的文件路径（支持 .xlsx 或 .csv 文件）。
    - sort_type (int): 聚合结果排序顺序，0（不排序），1（降序），2（升序）。默认不排序。

    返回:
    - pd.DataFrame: 分组聚合后的数据。
    """
    # 判断文件类型
    if file_path.endswith(".xlsx") or file_path.endswith(".xls"):
        # 如果是Excel文件，加载指定工作表
        df = pd.read_excel(file_path,sheet_name)
    elif file_path.endswith(".csv"):
        # 如果是CSV文件，加载数据
        encodings_to_try = ['utf-8', 'ISO-8859-1', 'GBK','gb2312']
        for encoding in encodings_to_try:
            try:
                df = pd.read_csv(file_path, encoding=encoding)
                break
            except UnicodeDecodeError:
                continue
    else:
        return {"error":"Unsupported file type. Please provide an Excel (.xlsx, .xls) or CSV (.csv) file."}

    # 检查列是否存在
    if group_by_column not in df.columns or agg_column not in df.columns:
        return {"error":f"Columns '{group_by_column}' or '{agg_column}' not found in the file."}

    # 分组聚合
    grouped_df = df.groupby(group_by_column)[agg_column].agg(agg_func)

    # 如果聚合列和分组列相同，则改名避免冲突
    if agg_column == group_by_column:
        grouped_df.name = f"{agg_func}_{agg_column}"

    # 构建 DataFrame 并设置列名
    grouped_df = grouped_df.reset_index()

    # 排序（如果启用）
    if sort_type!=0:
        ascending=False if sort_type==1 else True
        grouped_df = grouped_df.sort_values(by=agg_column, ascending=ascending)

    # 保存结果（如果指定文件路径）
    if save_as:
        if save_as.endswith(".xlsx"):
            grouped_df.to_excel(save_as, index=False)
            return {"response":f"Aggregated data successfully saved to {save_as}. here is the first 5 rows:\n{grouped_df.head(5)}"}
        elif save_as.endswith(".csv"):
            grouped_df.to_csv(save_as, index=False)
            return {"response":f"Aggregated data successfully saved to {save_as}. ",
                "row_count": grouped_df.shape[0],
                "preview_5_rows": grouped_df.head(5).to_dict(orient='records')
                }
        else:
            return {"error":"Unsupported file type for saving. Use '.xlsx' or '.csv'."}
    else:
        
        return {"response": 
                    {"row_count": grouped_df.shape[0],
                    "aggregated_data": grouped_df}
        }
# Example usage:
if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    # 文件路径（可选CSV或Excel）
    file_path = "./csv_data/TESLA_stock_data_2024.csv"
    # 配置参数
    group_by_column = 'Date'
    agg_column = 'Date'
    agg_func = 'count'

    file_path = "./excel_data/AmazingMartEU2.xlsx"
    sheet_name="OrderBreakdown"
    agg_column = "Quantity"
    group_by_column = "Quantity"
    agg_func = 'count'
    # # CSV文件示例
    try:
        aggregated_data_csv = group_and_aggregate_data(file_path, group_by_column, agg_column, agg_func,sheet_name,sort_type=1
        # ,save_as='result.csv'
        )
        print(f"Aggregated data from CSV by {group_by_column}:\n{aggregated_data_csv}")
    except Exception as e:
        print(f"CSV error: {e}")
