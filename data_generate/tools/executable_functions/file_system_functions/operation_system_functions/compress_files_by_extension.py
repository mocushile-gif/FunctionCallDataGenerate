import zipfile
import os
from dotenv import load_dotenv
load_dotenv()

def compress_files_by_extension(source_dir, output_zip, save_dir=None, file_extension=None, recursive=True):
    """
    Compress files with a specific extension into a ZIP archive.

    Parameters:
    - source_dir (str): The directory to search for files.
    - output_zip (str): The output ZIP file name.
    - save_dir (str): The directory to save the output ZIP file, defaults to source_dir.
    - file_extension (str): The file extension to compress (e.g., '.txt'), defaults to None (all files).
    - recursive (bool): Whether to include files in subdirectories. Defaults to True.

    Returns:
    - A tuple containing:
        1. Success status (True/False).
        2. A success message or an error message.
    """
    
    
    try:
        # Set save_dir to source_dir if not provided
        if not source_dir:
            source_dir='./'

        if not os.path.exists(source_dir):
            raise Exception(f"Error: Directory does not exist: {source_dir}")
        if not os.path.isdir(source_dir):
            raise Exception(f"Error: Path is not a directory: {source_dir}")
        save_dir = save_dir or source_dir

        # Construct the full path for the output ZIP file
        zip_path = os.path.join(save_dir, output_zip)

        # Create the ZIP archive
        cnt=0
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for root, _, files in os.walk(source_dir):
                for file in files:
                    # Check file extension if specified
                    if not file_extension or file.endswith(file_extension):
                        file_path = os.path.join(root, file)
                        cnt+=1
                        arcname = file_path if recursive else os.path.relpath(file_path, source_dir)
                        zipf.write(file_path, arcname)

        return True, f"{cnt} files with extension '{file_extension or 'all'}' compressed to {zip_path}."
    except Exception as e:
        return False, str(e)

if __name__ == '__main__':
    success, output = compress_files_by_extension("excel_data", "output.zip", file_extension=".xls")
    print(output)
