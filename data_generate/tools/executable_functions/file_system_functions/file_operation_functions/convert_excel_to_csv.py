import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()

def convert_excel_to_csv(input_path: str, output_path: str, sheet_name: str or int = 0):
    """
    Convert between Excel (.xls/.xlsx) and CSV formats.

    Parameters:
    - input_path (str): Path to the input file (.xlsx/.xls/.csv).
    - output_path (str): Path to the output file (.csv/.xlsx/.xls).
    - sheet_name (str or int): Sheet name or index (used only for Excel to CSV).

    Returns:
    - dict: Result with success message or error.
    """

    input_ext = os.path.splitext(input_path)[1].lower()
    output_ext = os.path.splitext(output_path)[1].lower()

    try:
        # Excel → CSV
        if input_ext in [".xlsx", ".xls"] and output_ext == ".csv":
            df = pd.read_excel(input_path, sheet_name=sheet_name)
            df.to_csv(output_path, index=False, encoding='utf-8')
            return {"success": f"Converted Excel ({sheet_name}) to CSV: {output_path}"}

        # CSV → Excel
        elif input_ext == ".csv" and output_ext in [".xlsx", ".xls"]:
            df = pd.read_csv(input_path)
            df.to_excel(output_path, index=False, sheet_name="Sheet1", engine='openpyxl' if output_ext == '.xlsx' else None)
            return {"success": f"Converted CSV to Excel: {output_path}"}

        else:
            return {"error": f"Unsupported conversion: {input_ext} → {output_ext}"}

    except Exception as e:
        return {"error": str(e)}

# Example usage
if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    # Excel to CSV
    # print(convert_excel_to_csv("excel_data/AmazingMartEU2.xlsx", "sheet1_data.csv", sheet_name="OrderBreakdown"))

    # CSV to Excel
    # print(convert_excel_to_csv("sheet1_data.csv", "reconverted_excel.xlsx"))
    print(convert_excel_to_csv(**{"input_path":"./excel_data/Retail Sales Dataset.xlsx","output_path":"./Retail Sales Dataset.csv","sheet_name":"Retail Sales Dataset"}))
