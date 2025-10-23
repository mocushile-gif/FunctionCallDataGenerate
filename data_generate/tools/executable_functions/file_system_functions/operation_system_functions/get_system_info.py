import platform
import os
from dotenv import load_dotenv
load_dotenv()

def get_system_info():
    """
    Get basic system information.

    Returns:
    - A tuple containing:
        1. Success status (True/False).
        2. A dictionary with system details or an error message.
    """
    try:
        info = {
            "system": platform.system(),
            "node": platform.node(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor()
        }
        return True, info
    except Exception as e:
        return False, str(e)

if __name__ == '__main__':
    # Example usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    success, output = get_system_info()
    print(success, output)
