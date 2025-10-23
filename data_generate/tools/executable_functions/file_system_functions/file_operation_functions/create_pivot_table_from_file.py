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

def create_pivot_table_from_file(file_path, sheet_name: str or int = 0,values=[], index=[], columns=[], aggfunc="sum", save_path=None):

    """
    Create a pivot table (optionally multi-level) from a CSV or Excel file.
    Allows both 'index' and 'columns' to be empty — will return direct aggregation in that case.
    """
    df = load_data(file_path,sheet_name)

    # Built-in aggregation functions
    aggfunc_mapping = {
        "sum": "sum", "mean": "mean", "median": "median", "count": "count",
        "min": "min", "max": "max", "std": "std", "var": "var", "first": "first", "last": "last"
    }

    # Resolve aggregation function
    if aggfunc in aggfunc_mapping:
        agg_function = aggfunc_mapping[aggfunc]
    else:
        try:
            agg_function = eval(aggfunc)
            if not callable(agg_function):
                raise ValueError(f"Custom aggfunc '{aggfunc}' is not callable.")
        except Exception as e:
            raise ValueError(f"Invalid custom aggfunc: {aggfunc}. Error: {str(e)}")

    # 自动处理 values 与 columns 冲突的问题（尤其是 aggfunc=count 时）
    conflict = False
    if isinstance(values, str) and values in columns + index:
        conflict = True
    elif isinstance(values, list) and any(v in columns + index for v in values):
        conflict = True

    if conflict and agg_function == "count":
        # 找到 df 中不在 index/columns 中的列作为 values
        candidates = [col for col in df.columns if col not in (index + columns)]
        if not candidates:
            raise ValueError("No available column to use as 'values' for counting.")
        values = candidates[0]

    # Case 1: index and columns are both empty → return direct aggregation result
    if not index and not columns:
        if isinstance(values, list):
            result = df[values].agg(agg_function)
        else:
            result = df[values].agg(agg_function)
        if save_path:
            result_df = pd.DataFrame([result]) if not isinstance(result, pd.Series) else result.to_frame().T
            if save_path.endswith(".csv"):
                result_df.to_csv(save_path, index=False)
            elif save_path.endswith((".xls", ".xlsx")):
                result_df.to_excel(save_path, index=False)
            else:
                raise ValueError("Unsupported file format. Use .csv, .xls, or .xlsx")
            return f"Aggregation result saved to {save_path} successfully.", result
        return result

    # Case 2: normal pivot table
    pivot_table = pd.pivot_table(
        df, index=index or None, columns=columns or None,
        values=values, aggfunc=agg_function, fill_value=0
    )

    if save_path:
        os.makedirs(os.path.dirname(save_path) or '.', exist_ok=True)
        if save_path.endswith(".csv"):
            pivot_table.to_csv(save_path)
        elif save_path.endswith((".xls", ".xlsx")):
            pivot_table.to_excel(save_path)
        else:
            raise ValueError("Unsupported file format. Please use .csv, .xls, or .xlsx")
        return f"The created pivot table is saved to {save_path} successfully.", pivot_table

    return pivot_table


# Example Usage
if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    # pivot_multi = create_pivot_table_from_file("./excel_data/BikeBuyers_Data.xlsx", index=["Education", "Occupation"], columns=["Region"], values="Income", aggfunc='lambda x: x.max() - x.min()',save_path="./pivot_output.xlsx" )
    pivot_multi = create_pivot_table_from_file("./csv_data/1000_ml_jobs_us.csv", index=["company_address_region","seniority_level"], columns=["job_title"], values="job_title", aggfunc='count')
    pivot_multi = create_pivot_table_from_file("./excel_data/AmazingMartEU2.xlsx", sheet_name="OrderBreakdown",columns=["Category"],values="Quantity", aggfunc='mean',save_path="./pivot_output.xlsx" )
    print(pivot_multi)
