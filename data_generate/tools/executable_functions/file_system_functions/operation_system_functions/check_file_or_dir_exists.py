import os
from dotenv import load_dotenv
load_dotenv()

def check_file_or_dir_exists(path):
    """
    Check if a file or directory exists.

    Parameters:
    - path (str): The path to check.

    Returns:
    - A tuple containing:
        1. Success status (True/False).
        2. A boolean indicating whether the file exists or an error message.
    """
    
    if not path:
        path='./'
    try:
        if os.path.exists(path):
            return True, f'"{path}" exists.'
        else:
            return True, f'"{path}" does not exists.'
    except Exception as e:
        return False, str(e)

if __name__ == '__main__':
    # Example usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    success, output = check_file_or_dir_exists('./image_data')
    print(success, output)
