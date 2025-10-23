import os
from dotenv import load_dotenv
load_dotenv()

def delete_files_by_extension(directory, file_extension, recursive=True):
    """
    Delete all files with a specific extension in a directory.

    Parameters:
    - directory (str): The directory to search in.
    - file_extension (str): The file extension to delete (e.g., '.log').
    - recursive (bool): Whether to search subdirectories. Defaults to True.

    Returns:
    - A tuple containing:
        1. Success status (True/False).
        2. A formatted success message or an error message.
    """
    try:
        if not directory:
            directory='./'
        deleted_files = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(file_extension):
                    file_path = os.path.join(root, file)
                    os.remove(file_path)
                    deleted_files.append(file_path)
            if not recursive:
                break
        if deleted_files:
            return True, f"Deleted files:\n" + "\n".join(deleted_files)
        else:
            return True, f"No files with extension '{file_extension}' found in {directory}."
    except Exception as e:
        return False, f"Error: {str(e)}"

if __name__ == '__main__':
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    success, output = delete_files_by_extension("./", ".txt")
    print(output)
