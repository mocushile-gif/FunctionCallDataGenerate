import os
from dotenv import load_dotenv
load_dotenv()

def change_owner(path: str, user_id: int, group_id: int):
    """
    Change the owner and group of a file or directory within a work directory.

    Parameters:
    - path (str): Relative path to the file or directory under work_dir.
    - user_id (int): The new owner's user ID.
    - group_id (int): The new group's group ID.

    Returns:
    - A tuple: (True, success message) or (False, error message)
    """
    work_dir=os.getcwd()
    full_path = os.path.join(work_dir, path)

    try:
        if not os.path.exists(full_path):
            return False, f"Path does not exist: {path}"
        
        os.chown(full_path, user_id, group_id)
        return True, f"Ownership changed successfully for '{path}' to UID:GID = {user_id}:{group_id}"
    
    except PermissionError:
        return False, f"Permission denied. You need root privileges to change ownership for '{path}'."
    except Exception as e:
        return False, f"Failed to change ownership for '{path}': {str(e)}"

if __name__ == '__main__':
    # Example usage
    # os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    os.chdir(os.environ.get("FILE_SYSTEM_PATH")+'2')
    success, output = change_owner("./image_data/dog.jpg", 1000, 2000)
    print(success, output)
