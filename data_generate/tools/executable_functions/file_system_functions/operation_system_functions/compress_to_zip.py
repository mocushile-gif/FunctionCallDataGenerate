import zipfile
import os
from dotenv import load_dotenv
load_dotenv()

def compress_to_zip(src, zip_name, include_root=True):
    
    """
    Compress a file or directory into a ZIP archive.

    Parameters:
    - src (str): The source file or directory.
    - zip_name (str): The name of the ZIP file to create.
    - include_root (bool): Whether to include the root directory in the archive. Defaults to True.

    Returns:
    - A tuple containing:
        1. Success status (True/False).
        2. A success message or error message.
    """
    if not src:
        src='./'

    if not os.path.exists(src):
        raise Exception(f"Error: Directory or file does not exist: {src}")

    with zipfile.ZipFile(zip_name, 'w') as zipf:
        if os.path.isdir(src):
            for root, dirs, files in os.walk(src):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = file_path if include_root else os.path.relpath(file_path, src)
                    zipf.write(file_path, arcname)
        else:
            zipf.write(src, os.path.basename(src))
    return True, f"Compressed {src} to {zip_name} successfully."

if __name__ == '__main__':
    # Example usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    success, output = compress_to_zip("image_data", "data.zip", include_root=False)
    print(success, output)
