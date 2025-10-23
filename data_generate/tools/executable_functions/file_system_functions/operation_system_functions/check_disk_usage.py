import shutil
import os
from dotenv import load_dotenv
load_dotenv()

def format_size(size_bytes):
    """
    Format the size in bytes to a human-readable format (e.g., KB, MB, GB, TB).
    
    Parameters:
    - size_bytes (int): Size in bytes.

    Returns:
    - A human-readable string representing the size.
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0

def check_disk_usage():
    
    """
    Check the disk usage and return a formatted string.
    """
    try:
        work_dir=os.getcwd()
        usage = shutil.disk_usage(work_dir)
        total = format_size(usage.total)
        used = format_size(usage.used)
        free = format_size(usage.free)
        result = (
            f"Disk Usage:\n"
            f"  Total: {total}\n"
            f"  Used: {used}\n"
            f"  Free: {free}"
        )
        return True, result
    except Exception as e:
        return False, str(e)

# Allow testing as a standalone script
if __name__ == '__main__':
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    success, output = check_disk_usage()
    print(output)
