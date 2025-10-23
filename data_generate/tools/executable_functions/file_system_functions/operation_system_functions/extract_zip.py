import zipfile
import os
from dotenv import load_dotenv
load_dotenv()

def extract_zip(zip_file, dest_dir):
    
    """
    Extract a ZIP archive to a directory.

    Parameters:
    - zip_file (str): The path to the ZIP file.
    - dest_dir (str): The destination directory.

    Returns:
    - A tuple containing:
        1. Success status (True/False).
        2. A success message or error message.
    """
    if not dest_dir:
        dest_dir='./'
    try:
        if not os.path.exists(zip_file):
            return False, f"not exist this zip file: {zip_file}"
        with zipfile.ZipFile(zip_file, 'r') as zipf:
            zipf.extractall(dest_dir)
        return True, f"Extracted {zip_file} to {dest_dir} successfully."
    except Exception as e:
        return False, str(e)

if __name__ == '__main__':
    # Example usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    success, output = extract_zip("/tmp/test_dir.zip", "/tmp/extracted_dir")
    print(success, output)
