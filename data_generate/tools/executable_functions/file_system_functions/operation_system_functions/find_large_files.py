import os
from dotenv import load_dotenv
load_dotenv()

def parse_size(size):
    """
    Convert a human-readable size string (e.g., 10K, 5M, 2G) to bytes.

    Parameters:
    - size (str): The size string with a unit suffix (K, M, G).

    Returns:
    - int: The size in bytes.
    """
    size = size.upper()
    if size.endswith('K'):
        return int(size[:-1]) * 1024
    elif size.endswith('M'):
        return int(size[:-1]) * 1024 ** 2
    elif size.endswith('G'):
        return int(size[:-1]) * 1024 ** 3
    else:
        return int(size)

def find_large_files(directory, size_threshold):
    """
    Find all files in a directory and its subdirectories that are larger than a specified size.

    Parameters:
    - directory (str): The directory to search in.
    - size_threshold (str): The size threshold as a human-readable string (e.g., 10K, 5M, 2G).

    Returns:
    - A list of tuples, each containing the file path and its size in bytes.
    """
    if not directory:
        directory='./'
    size_in_bytes = parse_size(size_threshold)
    large_files = []

    if not os.path.exists(directory):
        raise Exception(f"Error: Directory does not exist: {directory}")
    if not os.path.isdir(directory):
        raise Exception(f"Error: Path is not a directory: {directory}")

    try:
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    file_size = os.path.getsize(file_path)
                    if file_size > size_in_bytes:
                        large_files.append((file_path, file_size))
                except FileNotFoundError:
                    # Handle files that may no longer exist
                    continue
                except PermissionError:
                    # Skip files without permission to access
                    continue
    except Exception as e:
        return f"Error: Unexpected error occurred: {str(e)}"

    return large_files

if __name__ == '__main__':
    # Example usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    directory_to_search = "./"  # Replace with the target directory
    size_threshold = "100K"  # Example: 1 MB

    large_files = find_large_files(directory_to_search, size_threshold)
    print(large_files)