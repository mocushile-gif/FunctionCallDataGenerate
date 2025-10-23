import os
from dotenv import load_dotenv
load_dotenv()

def find_files_with_extension(directory, extension):
    """
    Find all files with a specific extension in a directory.

    Parameters:
    - directory (str): The directory to search.
    - extension (str): The file extension to search for (e.g., ".txt").

    Returns:
    - A tuple containing:
        1. Success status (True/False).
        2. A list of matching file paths or an error message.
    """
    if not directory:
        directory='./'

    if not os.path.exists(directory) or not os.path.isdir(directory):
        raise Exception(f"Error: Directory '{directory}' does not exist.")
    try:
        matches = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(extension):
                    matches.append(os.path.join(root, file))
        return True, matches
    except Exception as e:
        return False, str(e)

if __name__ == '__main__':
    # Example usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    success, output = find_files_with_extension("./image_data", ".gif")
    print(success, output)
