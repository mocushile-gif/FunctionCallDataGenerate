import pwd
import grp
import os
from dotenv import load_dotenv
load_dotenv()

def get_file_permissions_and_owner(path):
    """
    Get the permissions and ownership details of a file or directory.

    Parameters:
    - path (str): The path of the file or directory.

    Returns:
    - A tuple containing:
        1. Success status (True/False).
        2. A dictionary with permissions, owner, and group details or an error message.
    """
    if not path:
        path='./'

    try:
        stat_info = os.stat(path)
        permissions = oct(stat_info.st_mode)[-3:]
        owner = pwd.getpwuid(stat_info.st_uid).pw_name
        group = grp.getgrgid(stat_info.st_gid).gr_name

        return True, {
            "permissions": permissions,
            "owner": owner,
            "group": group
        }
    except Exception as e:
        return False, str(e)

if __name__ == '__main__':
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    # Example usage
    success, output = get_file_permissions_and_owner("./image_data/dog.jpg")
    print(success, output)
