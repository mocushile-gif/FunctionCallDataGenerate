import time
import os
from dotenv import load_dotenv
load_dotenv()

def delete_old_files(directory, days, file_extension=None):
    
    """
    Delete files older than a specified number of days in a directory.

    Parameters:
    - directory (str): The directory to search for files.
    - days (int): The age threshold in days for deletion.
    - file_extension (str): The file extension to filter by (e.g., '.log'). Defaults to None (all files).

    Returns:
    - A tuple containing:
        1. Success status (True/False).
        2. A success message or an error message.
    """
    try:
        if not directory:
            directory='./'
        if not os.path.exists(directory) or not os.path.isdir(directory):
            raise Exception(f"Error: Directory '{directory}' does not exist.")
        now = time.time()
        threshold = now - (days * 86400)
        deleted_files = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file_extension and not file.endswith(file_extension):
                    continue
                file_path = os.path.join(root, file)
                if os.path.getmtime(file_path) < threshold:
                    os.remove(file_path)
                    deleted_files.append(file_path)
        if deleted_files:
            return True, f"Deleted files older than {days} days:\n" + "\n".join(deleted_files)
        else:
            return True, f"No files older than {days} days found."
    except Exception as e:
        return False, f"Error: {str(e)}"

if __name__ == '__main__':
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    success, output = delete_old_files("./", 30, ".log")
    print(output)
