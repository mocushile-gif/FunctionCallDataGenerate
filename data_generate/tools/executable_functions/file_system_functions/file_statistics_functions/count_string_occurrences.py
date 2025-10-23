import os
from dotenv import load_dotenv
load_dotenv()

def count_string_occurrences(directory, search_string, file_extension=".txt"):
    
    """
    Count the occurrences of a specific string in each file and total occurrences in a directory.

    Parameters:
    - directory (str): The directory to search in.
    - search_string (str): The string to count within files.
    - file_extension (str): The file extension to filter by (default is '.txt').

    Returns:
    - A tuple containing:
        1. Success status (True/False).
        2. A dictionary with file paths as keys and occurrence counts as values, including a total count.
    """
    try:
        occurrences = {}
        total_count = 0
        if not directory:
            directory='./'
        if not os.path.exists(directory) or not os.path.isdir(directory):
            return False, f"Error: Directory '{directory}' does not exist."
        for root, _, files in os.walk(directory):
            for file in files:
                if not file.endswith(file_extension):
                    continue
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        count = content.count(search_string)
                        occurrences[file_path] = count
                        total_count += count
                except Exception as e:
                    occurrences[file_path] = f"Error reading file: {e}"

        occurrences['TOTAL'] = total_count
        return True, occurrences

    except Exception as e:
        return False, f"Error: {str(e)}"
    
if __name__ == '__main__':
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    success, output = count_string_occurrences(
        directory="./csv_data",
        search_string="climate",
        file_extension=""
    )
    print(success, output)