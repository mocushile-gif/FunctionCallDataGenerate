import os
import getpass
from dotenv import load_dotenv
load_dotenv()

def get_current_user():
    """
    Get the current system user in a safe and portable way.

    Returns:
    - A tuple containing:
        1. Success status (True/False).
        2. The username or an error message.
    """
    try:        
        user = getpass.getuser()
        return True, user
    except Exception as e:
        return False, str(e)

if __name__ == '__main__':
    success, output = get_current_user()
    print(success, output)
