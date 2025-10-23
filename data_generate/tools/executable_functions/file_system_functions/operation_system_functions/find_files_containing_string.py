import os
from dotenv import load_dotenv
load_dotenv()

def find_files_containing_string(directory, search_string, file_extension=".txt"):
    
    """
    Find all files in a directory containing a specific string.

    Parameters:
    - directory (str): The directory to search in.
    - search_string (str): The string to search for within files.
    - file_extension (str): The file extension to filter by (default is '.txt').

    Returns:
    - A tuple containing:
        1. Success status (True/False).
        2. A list of file paths containing the string or an error message.
    """
    if not directory:
        directory='./'

    if not os.path.exists(directory) or not os.path.isdir(directory):
        raise Exception(f"Error: Directory '{directory}' does not exist.")
        
    try:
        matching_files = []

        for root, _, files in os.walk(directory):
            for file in files:
                if not file.endswith(file_extension):
                    continue
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        if search_string in f.read():
                            matching_files.append(file_path)
                except Exception as e:
                    continue

        if not matching_files:
            return True, f"No files containing '{search_string}' were found."
        return True, matching_files

    except Exception as e:
        return False, f"Error: {str(e)}"

if __name__ == '__main__':
    # Example usage of find_files_containing_string
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    success, output = find_files_containing_string(
        directory="./",
        search_string="machine",
        file_extension=".json"
    )
    print(success, output)