import tarfile
import os
from dotenv import load_dotenv
load_dotenv()

def compress_to_tar_gz(source_dir, output_filename, compress_level=5):
    """
    Compress a directory into a tar.gz file.

    Parameters:
    - source_dir (str): The directory to compress.
    - output_filename (str): The output tar.gz file name.
    - compress_level (int): Compression level (1-9). Defaults to 5.

    Returns:
    - A tuple containing:
        1. Success status (True/False).
        2. A success message or an error message.
    """
    
    if not source_dir:
        source_dir='./'
    if not os.path.exists(source_dir):
        raise Exception(f"Error: Directory does not exist: {source_dir}")
    if not os.path.isdir(source_dir):
        raise Exception(f"Error: Path is not a directory: {source_dir}")
    try:
        with tarfile.open(output_filename, "w:gz", compresslevel=compress_level) as tar:
            tar.add(source_dir, arcname=os.path.basename(source_dir))
        return True, f"Directory {source_dir} compressed to {output_filename}."
    except Exception as e:
        return False, str(e)

if __name__ == '__main__':
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    success, output = compress_to_tar_gz("image_data", "compressed.tar.gz")
    print(output)
