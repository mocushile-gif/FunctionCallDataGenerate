import os
from dotenv import load_dotenv
load_dotenv()
import shutil

def move_or_rename_file_or_directory(src, dest):
    """
    Move a file or directory to a new location.

    Parameters:
    - src (str): The source file or directory.
    - dest (str): The destination path.

    Returns:
    - A tuple containing:
        1. Success status (True/False).
        2. A success message or error message.
    """
    if not src:
        src = './'
    if not dest:
        dest = './'

    # 确保目标目录存在
    dest_dir = os.path.dirname(dest)
    if dest_dir and not os.path.exists(dest_dir):
        os.makedirs(dest_dir, exist_ok=True)

    shutil.move(src, dest)
    return True, f"Moved {src} to {dest} successfully."

if __name__ == '__main__':
    # Example usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    success, output = move_or_rename_file_or_directory("./bar_chart.png", "./bar.png")
    print(success, output)
