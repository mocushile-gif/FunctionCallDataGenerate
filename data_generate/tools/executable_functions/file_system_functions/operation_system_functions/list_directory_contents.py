import os
import subprocess
from dotenv import load_dotenv
load_dotenv()

def list_directory_contents(path, show_hidden=False, long_format=False):
    """
    List the contents of a directory with options for hidden files and detailed output.

    Parameters:
    - path (str): The path of the directory to list.
    - show_hidden (bool): Whether to include hidden files. Defaults to False.
    - long_format (bool): Whether to use long format listing (similar to `ls -l`). Defaults to False.

    Returns:
    - A tuple containing:
        1. Success status (True/False).
        2. The directory contents or error message.
    """
    options = []
    if show_hidden:
        options.append("-a")
    if long_format:
        options.append("-l")

    command = ["ls"]
    if options:
        command += options 
    command += [path] if path else ['./']

    try:
        result = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            return False, result.stderr.strip()
    except Exception as e:
        return False, str(e)

if __name__ == '__main__':
    # Example usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    success, output = list_directory_contents("./database", show_hidden=True, long_format=True)
    print(success, output)
