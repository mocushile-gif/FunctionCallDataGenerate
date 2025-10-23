import shutil
import os
from dotenv import load_dotenv
load_dotenv()

def copy_file_or_directory(src, dest, overwrite=False):
    
    """
    Copy a file or directory to a new location.

    Parameters:
    - src (str): The source file or directory.
    - dest (str): The destination path.
    - overwrite (bool): Whether to overwrite the destination if it exists. Defaults to False.

    Returns:
    - A tuple containing:
        1. Success status (True/False).
        2. A success message or error message.
    """
    try:
        if not src:
            src='./'
        if not dest:
            dest='./'
        if os.path.exists(dest) and not overwrite:
            return False, f"Destination {dest} already exists. Use overwrite=True to replace it."
        if os.path.isdir(src):
            shutil.copytree(src, dest, dirs_exist_ok=overwrite)
        else:
            shutil.copy2(src, dest)
        return True, f"Copied {src} to {dest} successfully."
    except Exception as e:
        return False, str(e)

if __name__ == '__main__':
    # Example usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    success, output = copy_file_or_directory("./csv_data/TED Talks.csv", "./", overwrite=True)
    print(success, output)
