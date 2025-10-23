import filecmp
import os
from dotenv import load_dotenv
load_dotenv()

def compare_files(file1, file2):
    """
    Compare two files to check if they are identical.

    Parameters:
    - file1 (str): Path to the first file.
    - file2 (str): Path to the second file.

    Returns:
    - A tuple containing:
        1. Success status (True/False).
        2. A formatted message indicating whether the files are identical or an error message.
    """
    
    try:
        are_equal = filecmp.cmp(file1, file2, shallow=False)
        status = "identical" if are_equal else "different"
        return True, f"Files compared: {file1}, {file2}\tStatus: {status}"
    except Exception as e:
        return False, f"Error: {str(e)}"

if __name__ == '__main__':
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    success, output = compare_files("./excel_data/AmazingMartEU2.xlsx", "./excel_data/AmazingMartEU2.xlsx")
    print(output)
