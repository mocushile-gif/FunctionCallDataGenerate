import os
import random
import time
from datetime import datetime, timedelta

def randomize_file_mtime(
    directory: str,
    extension: str = None,
    days_range: int = 30,
    recursive: bool = True
):
    """
    Randomly update the modified time (mtime) of files in a directory.

    Parameters:
    - directory (str): The base directory to search.
    - extension (str): File extension filter (e.g., '.txt'). Default: None (all files).
    - days_range (int): Max range in days before now to set mtime. Default: 30 days.
    - recursive (bool): Whether to include subdirectories. Default: True.
    """

    if not os.path.isdir(directory):
        raise ValueError(f"Directory does not exist: {directory}")

    all_files = []
    for root, _, files in os.walk(directory) if recursive else [(directory, [], os.listdir(directory))]:
        for f in files:
            if extension and not f.endswith(extension):
                continue
            full_path = os.path.join(root, f)
            if os.path.isfile(full_path):
                all_files.append(full_path)

    now = time.time()
    modified = []

    for file_path in all_files:
        # Choose a random past time within the range
        offset = random.randint(0, days_range * 24 * 3600)
        new_mtime = now - offset
        os.utime(file_path, (new_mtime, new_mtime))
        modified.append((file_path, datetime.fromtimestamp(new_mtime).isoformat()))

    return modified

# Example usage
if __name__ == "__main__":
    # 随机修改文件系统中的文件修改时间
    random.seed(42)
    modified_files = randomize_file_mtime("/mnt/afs2/qinxinyi/function_call_data/data_generate/working_dir/file_system_new", extension="", days_range=200)
    for path, mtime in modified_files:
        print(f"Modified: {path} → {mtime}")
