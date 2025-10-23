import shutil
import os
from dotenv import load_dotenv
load_dotenv()

def delete_file_or_directory(path, is_directory=False):
    
    """
    Delete a file or directory.

    Parameters:
    - path (str): The path to the file or directory.
    - is_directory (bool): Whether the path is a directory. Defaults to False.

    Returns:
    - A tuple containing:
        1. Success status (True/False).
        2. A success message or error message.
    """
    try:
        if not path:
            path='./'
        if is_directory:
            shutil.rmtree(path)
        else:
            os.remove(path)
        return True, f"Deleted {path} successfully."
    except Exception as e:
        return False, str(e)

if __name__ == '__main__':
    # Example usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    success, output = delete_file_or_directory("./line_chart.png")
    print(success, output)
