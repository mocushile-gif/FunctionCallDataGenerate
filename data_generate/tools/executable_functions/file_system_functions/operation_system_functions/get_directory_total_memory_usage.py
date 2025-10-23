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

def get_directory_size(path):
    """
    Recursively calculate the total size of the specified directory and its contents.

    Parameters:
    - path (str): The path to the directory.

    Returns:
    - The total size of the directory in bytes.
    """
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            if os.path.isfile(file_path):
                total_size += os.path.getsize(file_path)
    return total_size

def get_directory_total_memory_usage(path):
    """
    Check the memory usage (size of files) for a given path.

    Parameters:
    - path (str): The path to check memory usage.

    Returns:
    - A tuple containing:
        1. Success status (True/False).
        2. A formatted string with memory usage details or an error message.
    """
    if not path:
        path = './'  # Default to current directory if path is empty

    if not os.path.exists(path) or not os.path.isdir(path):
        raise Exception(f"Error: Directory '{path}' does not exist.")
    try:
        total_size = get_directory_size(path)
        total_size_formatted = format_size(total_size)
        
        result = (
            f"Memory Usage for '{path}':\n"
            f"  Total Size: {total_size_formatted}\n"
        )
        return True, result
    except Exception as e:
        return False, str(e)

# Allow testing as a standalone script
if __name__ == '__main__':
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    success, output = get_directory_total_memory_usage("./txt_data")  # Check the memory usage of the current directory
    print(output)
