import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()

def write_table_to_file(columns, rows, file_path, encoding="utf-8", index=False):
    """
    Write tabular data (columns + rows) to a CSV or Excel file.

    Parameters:
    - columns (list): List of column names.
    - rows (list of lists): Table data, each sub-list is a row.
    - file_path (str): Path to save the output file (.csv or .xlsx).
    - encoding (str): File encoding (for CSV only).
    - index (bool): Whether to write row indices.

    Returns:
    - str: Confirmation message.
    """
    
    # Validate inputs
    if not isinstance(columns, list) or not all(isinstance(col, str) for col in columns):
        raise ValueError("columns must be a list of strings.")
    if not all(isinstance(row, list) and len(row) == len(columns) for row in rows):
        raise ValueError("Each row must be a list with the same length as columns.")

    # Convert to DataFrame
    df = pd.DataFrame(rows, columns=columns)

    # Save to file
    if file_path.endswith(".csv"):
        df.to_csv(file_path, index=index, encoding=encoding)
    elif file_path.endswith((".xls", ".xlsx")):
        df.to_excel(file_path, index=index)
    else:
        raise ValueError("Unsupported file format. Please use .csv or .xlsx")

    return f"Data written to {file_path} successfully."

if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    columns = ["Name", "Age", "City"]
    rows = [
        ["Alice", 30, "New York"],
        ["Bob", 25, "London"],
        ["Charlie", 28, "Beijing"]
    ]
    
    result = write_table_to_file(columns, rows, "people.csv")
    print(result)
