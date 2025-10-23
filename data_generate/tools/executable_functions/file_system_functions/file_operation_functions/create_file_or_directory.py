import os
from dotenv import load_dotenv
load_dotenv()

def create_file_or_directory(path, is_directory=False, mode=493):

    """
    Create a file or directory with specified permissions.

    Parameters:
    - path (str): The path of the file or directory to create.
    - is_directory (bool): Whether to create a directory instead of a file. Defaults to False.
    - mode (int): The permissions to set. Defaults to 493.

    Returns:
    - A tuple containing:
        1. Success status (True/False).
        2. A success message or error message.
    """
    try:
        if not path:
            path='./'
        if is_directory:
            os.makedirs(path, mode=mode, exist_ok=True)
            return True, f"Directory created: {path}"
        else:
            with open(path, "w") as f:
                pass
            os.chmod(path, mode)
            return True, f"File created: {path}"
    except Exception as e:
        return False, str(e)

if __name__ == '__main__':
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    success, output = create_file_or_directory("virtual", is_directory=True)
    print(success, output)
