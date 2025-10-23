import os
import time
import hashlib
from dotenv import load_dotenv
load_dotenv()

def get_file_metadata(
    file_path, 
    include_permissions=True, 
    include_hash=False, 
    hash_algorithm="md5", 
    time_format="human-readable",
):
    """
    Retrieve metadata for a given file with customization options.

    Parameters:
    - file_path (str): Path to the file.
    - include_permissions (bool): Whether to include file permissions (default: True).
    - include_hash (bool): Whether to compute a hash checksum of the file (default: False).
    - hash_algorithm (str): Hashing algorithm to use if include_hash=True (default: "md5"). Options: "md5", "sha256".
    - time_format (str): Format for timestamps. Options:
        - "human-readable" (default): Returns times in a human-readable string.
        - "timestamp": Returns times as Unix timestamps.

    Returns:
    - dict: Metadata including size, creation time, modification time, permissions, and optional hash checksum.
    """    

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    file_stats = os.stat(file_path)

    # Format timestamps based on user preference
    if time_format == "timestamp":
        created_at = file_stats.st_ctime
        modified_at = file_stats.st_mtime
    else:
        created_at = time.ctime(file_stats.st_ctime)
        modified_at = time.ctime(file_stats.st_mtime)

    metadata = {
        "file_path": file_path,
        "size_bytes": file_stats.st_size,
        "created_at": created_at,
        "modified_at": modified_at
    }

    # Include file permissions
    if include_permissions:
        metadata["permissions"] = {
            "numeric": oct(file_stats.st_mode)[-3:],  # Last 3 digits (e.g., "644")
            "symbolic": get_symbolic_permissions(file_path)  # e.g., "rw-r--r--"
        }

    # Include file hash checksum
    if include_hash:
        metadata["hash"] = compute_file_hash(file_path, hash_algorithm)

    return metadata


def get_symbolic_permissions(file_path):
    """Retrieve file permissions in symbolic format (e.g., 'rw-r--r--')."""
    return "".join([
        "r" if os.access(file_path, os.R_OK) else "-",
        "w" if os.access(file_path, os.W_OK) else "-",
        "x" if os.access(file_path, os.X_OK) else "-"
    ])


def compute_file_hash(file_path, algorithm="md5", buffer_size=8192):
    """
    Compute hash checksum of a file using the specified algorithm.

    Parameters:
    - file_path (str): Path to the file.
    - algorithm (str): Hashing algorithm. Options: "md5", "sha256" (default: "md5").
    - buffer_size (int): Size of chunks read from the file to optimize performance.

    Returns:
    - str: Computed hash checksum.
    """
    hash_func = hashlib.md5() if algorithm == "md5" else hashlib.sha256()

    with open(file_path, "rb") as f:
        while chunk := f.read(buffer_size):
            hash_func.update(chunk)

    return hash_func.hexdigest()


# Example Usage
if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    metadata = get_file_metadata(
        file_path="./excel_data/BikeBuyers_Data.xlsx",
        include_permissions=True,
        include_hash=True,
        hash_algorithm="sha256",
        time_format="human-readable",
    )
    print(metadata)
