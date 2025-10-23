import os
from dotenv import load_dotenv
load_dotenv()

def get_file_size(path, human_readable=False):
    
    """
    Get the size of a file.

    Parameters:
    - path (str): The path to the file.
    - human_readable (bool): Whether to return the size in a human-readable format. Defaults to False.

    Returns:
    - A tuple containing:
        1. Success status (True/False).
        2. The file size in bytes or a human-readable format, or an error message.
    """
    size = os.path.getsize(path)
    if human_readable:
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return True, f"{size:.2f} {unit}"
            size /= 1024.0
    return True, size

if __name__ == '__main__':
    # Example usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    success, output = get_file_size("./excel_data/BikeBuyers_Data.xlsx", human_readable=True)
    print(success, output)
