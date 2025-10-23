import zipfile
import os
from dotenv import load_dotenv
load_dotenv()

def compress_files_to_zip(file_paths, zip_name):
    """
    Compress multiple files into a ZIP archive.

    Parameters:
    - file_paths (list of str): A list of file paths to compress.
    - zip_name (str): The name of the ZIP file to create.

    Returns:
    - A tuple containing:
        1. Success status (True/False).
        2. A success message or error message.
    """

    try:
        if not file_paths:
            return False, "No files provided for compression."

        with zipfile.ZipFile(zip_name, 'w') as zipf:
            for file_path in file_paths:
                if os.path.isfile(file_path):
                    zipf.write(file_path)
                else:
                    return False, f"Warning: File '{file_path}' does not exist and will not be included."

        return True, f"Compressed {len(file_paths)} files to {zip_name} successfully."

    except Exception as e:
        return False, str(e)

if __name__ == '__main__':
    # Example usage
    files_to_compress = ["/mnt/nvme0/qinxinyi/function_call_data/data_generate/tools/executable_functions/file_system_functions/compress_to_tar_gz.py", 
                         "/mnt/nvme0/qinxinyi/function_call_data/data_generate/tools/executable_functions/file_system_functions/compress_files_by_extension.py"]
    files_to_compress = ['[OUTPUT FROM find_large_files.file_paths]']
    success, output = compress_files_to_zip(files_to_compress, "compressed_files.zip")
    print(success, output)
