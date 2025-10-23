import os
from dotenv import load_dotenv
load_dotenv()

def get_recent_files(directory, top_n, file_extension=None):
    
    """
    Get the most recently modified files in a directory and its subdirectories.

    Parameters:
    - directory (str): The directory to search for files.
    - top_n (int): The number of recent files to return.
    - file_extension (str): The file extension to filter by (e.g., '.txt'). Defaults to None (all files).

    Returns:
    - A tuple (success: bool, result: str): 
        - If success: result is a formatted string listing recent files.
        - If failed: result is an error message.
    """
    if not directory:
        directory = './'
    if not os.path.exists(directory) or not os.path.isdir(directory):
        raise Exception(f"Error: Directory '{directory}' does not exist.")
    try:
        files = []
        for root, _, file_names in os.walk(directory):
            for file_name in file_names:
                if file_extension and not file_name.endswith(file_extension):
                    continue
                file_path = os.path.join(root, file_name)
                if os.path.isfile(file_path):
                    files.append((file_path, os.path.getmtime(file_path)))

        files.sort(key=lambda x: x[1], reverse=True)
        recent_files = [f[0] for f in files[:top_n]]
        return True, f"Most recent {top_n} files:\n" + "\n".join(recent_files)

    except Exception as e:
        return False, f"Error: {str(e)}"

if __name__ == '__main__':
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    success, output = get_recent_files("./", 5, "")
    print(output)
