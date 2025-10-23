import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()

def filter_string_data(file_path: str, column_name: str, thresholds, sheet_name: str or int =0, conditions=None, save_as: str = None, logical_operator: str = "or"):
    """
    根据指定条件筛选 Excel 或 CSV 数据，并返回符合条件的行，支持多个条件组合筛选。

    参数:
    - file_path (str): Excel 或 CSV 文件的路径。
    - column_name (str): 用于筛选的列名，仅支持字符串类型的列。
    - thresholds (list[str]): 筛选的值列表，保留该列值符合条件的行。
    - conditions (list[str], 可选): 筛选条件列表，默认是 `equal_to`，支持 'equal_to', 'not_equal_to', 'contains', 'starts_with', 'ends_with'。
    - save_as (str, 可选): 保存筛选结果的文件路径（支持 .xlsx 或 .csv）。

    返回:
    - dict: 筛选后的数据或错误信息。
    """


    if logical_operator not in ("or", "and"):
        return {"error": "logical_operator must be either 'or' or 'and'"}

    # 读取文件
    if file_path.endswith((".xlsx", ".xls")):
        df = pd.read_excel(file_path,sheet_name)
    elif file_path.endswith(".csv"):
        encodings_to_try = ['utf-8', 'ISO-8859-1', 'GBK','gb2312']
        for encoding in encodings_to_try:
            try:
                df = pd.read_csv(file_path, encoding=encoding)
                break
            except UnicodeDecodeError:
                continue
    else:
        return {"error": "Unsupported file type. Please provide an Excel (.xlsx, .xls) or CSV (.csv) file."}

    if column_name not in df.columns:
        return {"error": f"Column '{column_name}' does not exist in the DataFrame."}

    column_dtype = df[column_name].dtype
    if not pd.api.types.is_string_dtype(column_dtype):
        return {"error": f"Unsupported data type for column '{column_name}'. Supported type is only string."}

    if not isinstance(thresholds, list):
        thresholds = [thresholds]  # 如果用户传递的是单个值，则转换为列表

    if conditions is None:
        conditions = ["equal_to"] * len(thresholds)  # 默认使用 equal_to 条件
    elif not isinstance(conditions, list):
        conditions = [conditions]  # 如果用户传递的是单个条件，则转换为列表

    if len(thresholds) != len(conditions):
        return {"error": "Mismatch between the number of thresholds and conditions. Ensure they have the same length."}

    # 初始化筛选条件
    filter_masks = []
    for threshold, condition in zip(thresholds, conditions):
        if condition == "equal_to":
            mask = df[column_name] == threshold
        elif condition == "not_equal_to":
            mask = df[column_name] != threshold
        elif condition == "contains":
            mask = df[column_name].str.contains(str(threshold), na=False)
        elif condition == "starts_with":
            mask = df[column_name].str.startswith(str(threshold), na=False)
        elif condition == "ends_with":
            mask = df[column_name].str.endswith(str(threshold), na=False)
        else:
            return {"error": f"Unsupported condition '{condition}'. Supported conditions are 'equal_to', 'not_equal_to', 'contains', 'starts_with', 'ends_with'."}
        filter_masks.append(mask)

    combined_mask = filter_masks[0]
    for mask in filter_masks[1:]:
        if logical_operator == "or":
            combined_mask |= mask  # 逻辑 OR
        else:
            combined_mask &= mask  # 逻辑 AND

    filtered_df = df[combined_mask]

    # 保存结果（如果指定了文件路径）
    if save_as:
        os.makedirs(os.path.dirname(save_as) or '.', exist_ok=True)
        if save_as.endswith(".xlsx"):
            filtered_df.to_excel(save_as, index=False)
        elif save_as.endswith(".csv"):
            filtered_df.to_csv(save_as, index=False)
        else:
            return {"error": "Unsupported file type for saving. Use '.xlsx' or '.csv'."}
        return {
    "response": f"Filtered data successfully saved to {save_as}.",
    "row_count": filtered_df.shape[0],
    "preview_5_rows": filtered_df.head(5).to_dict(orient='records')
}

    return {"response": 
                {"row_count": filtered_df.shape[0],
                "filtered_data": filtered_df.to_dict(orient="records")}}

# Example Usage:
if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    file_path = './excel_data/BikeBuyers_Data.xlsx'
    column_name = 'Region'
    thresholds = ['Europe', 'Pacific']
    conditions = ["equal_to", "equal_to"]
    sheet_name="BikeBuyers_Data"
    logical_operator="or"
    save_as = "european_pacific_customers.csv"

    result = filter_string_data(file_path, column_name, thresholds, sheet_name,conditions,logical_operator=logical_operator,save_as=save_as)
    print(f"Filtered data ({column_name} matches {thresholds} with conditions {conditions}):\n", result)
