import os
from dotenv import load_dotenv
load_dotenv()

def display_directory_tree(path='./', indent=0, depth=2):
    """
    Display the directory structure in a tree-like format with depth control.

    Parameters:
    - path (str): The root directory path to display.
    - indent (int): The current indentation level (used internally for recursion).
    - depth (int): The maximum depth to traverse (default is 1).
    """

    tree = ""
    if not path:
        path = './'

    if not os.path.exists(path) or not os.path.isdir(path):
        raise Exception(f"Error: Directory '{path}' does not exist.")
    try:
        if indent == 0:
            tree += f"Root Directory: {path}\n"
        if depth <= 0:
            return tree  # Stop recursion if depth limit is reached

        entries = sorted(os.listdir(path))

        for entry in entries:
            entry_path = os.path.join(path, entry)
            is_dir = os.path.isdir(entry_path)

            # Mark directories with "[DIR]"
            if is_dir:
                tree += "  " * indent + f"|- [DIR] {entry}\n"
                tree += display_directory_tree(entry_path, indent + 1, depth - 1)
            else:
                tree += "  " * indent + f"|- {entry}\n"
    except PermissionError:
        tree += "  " * indent + f"|- [Permission Denied]\n"
    except Exception as e:
        return f"Error: Unexpected error: {str(e)}\n"

    return tree

if __name__ == '__main__':
    # Example usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    root_path = f"./"  # Replace with the desired directory path
    max_depth = 3  # Adjust the depth as needed
    result = display_directory_tree(root_path, depth=max_depth)
    print(result)
