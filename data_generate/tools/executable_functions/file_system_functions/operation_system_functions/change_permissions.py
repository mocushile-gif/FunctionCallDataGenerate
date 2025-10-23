import os
from dotenv import load_dotenv
load_dotenv()

def change_permissions(path, mode):
    
    """
    Change the permissions of a file or directory.

    Parameters:
    - path (str): The path of the file or directory.
    - mode (int): The permissions to set (e.g., 493).

    Returns:
    - A tuple containing:
        1. Success status (True/False).
        2. A success message or error message.
    """
    if not path:
        path='./'
    try:
        os.chmod(path, mode)
        return True, f"Permissions changed for {path} to {oct(mode)}"
    except Exception as e:
        return False, str(e)

if __name__ == '__main__':
    # Example usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH")+'2')
    success, output = change_permissions("image_data", 493)
    print(success, output)
