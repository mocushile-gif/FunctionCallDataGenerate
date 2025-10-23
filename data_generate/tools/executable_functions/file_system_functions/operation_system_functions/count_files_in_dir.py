import os
from dotenv import load_dotenv
load_dotenv()

def count_files_in_dir(directory='./', file_extension=None, recursive=True):
    
    """
    Count the number of files in a directory, with optional filtering by file extension.

    Parameters:
    - directory (str): The directory to search for files.
    - file_extension (str): The file extension to filter by (e.g., '.txt'). Defaults to None (all files).
    - recursive (bool): Whether to include files in subdirectories. Defaults to True.

    Returns:
    - A tuple containing:
        1. Success status (True/False).
        2. A formatted message with the total file count or an error message.
    """
            # Check if directory exists
    if not directory:
        directory='./'
    if not os.path.exists(directory) or not os.path.isdir(directory):
        return False, f"Error: Directory '{directory}' does not exist."
    file_count = 0
    for root, _, files in os.walk(directory):
        if file_extension:
            file_count += sum(1 for file in files if file.endswith(file_extension))
        else:
            file_count += len(files)
        if not recursive:
            break
    return True, f"Directory: {directory}\tTotal files{' with extension ' + file_extension if file_extension else ''}: {file_count}"

if __name__ == '__main__':
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    success, output = count_files_in_dir("./excel_data", file_extension=".xlsx", recursive=True)
    print(output)
