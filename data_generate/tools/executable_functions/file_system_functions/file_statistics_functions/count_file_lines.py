import os
from dotenv import load_dotenv
import pandas as pd
load_dotenv()

def count_file_lines(file_path):
    
    """
    Count the number of lines in a file.

    Parameters:
    - file_path (str): The path to the file.

    Returns:
    - A tuple containing:
        1. Success status (True/False).
        2. A formatted string with the file path and line count or an error message.
    """
    try:
        ext = os.path.splitext(file_path)[1].lower()

        if ext in ('.xlsx', '.xls'):
            xls = pd.ExcelFile(file_path)
            output_lines = []
            for sheet in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet)
                output_lines.append(f"{len(df)} rows (sheet: {sheet})")
            output_text = f"{file_path}\n" + "\n".join(output_lines)
            return True, output_text

        elif ext == '.csv':
            df = pd.read_csv(file_path)
            return True, f"{len(df)} rows (CSV)\t{file_path}"
        else:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                line_count = sum(1 for _ in f)
            return True, f"{line_count} lines (text)\t{file_path}"
        # else:
        #     with open(file_path, 'rb') as f:
        #         line_count = sum(chunk.count(b'\n') for chunk in iter(lambda: f.read(1024 * 1024), b''))
        #     return True, f"{line_count} lines (text)\t{file_path}"
    except Exception as e:
        return False, f"Error reading file {file_path}: {e}"

if __name__ == '__main__':
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    file_path="./json_data/Top_1000_Github_repositories_for_popular_topics/R.json"
    success, output = count_file_lines(file_path)
    print(output)
