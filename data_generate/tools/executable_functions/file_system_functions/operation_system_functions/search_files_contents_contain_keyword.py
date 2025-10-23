import os
from dotenv import load_dotenv
load_dotenv()

def search_files_contents_contain_keyword(directory, keyword, file_extension=None, max_size_mb=1):
    """
    Search for files within a directory which contain specific keyword within a directory.

    Parameters:
    - directory (str): The directory to search in.
    - keyword (str): The keyword to search for.
    - file_extension (str): The file extension to filter by (e.g., '.txt'). Defaults to None (all files).
    - max_size_mb (int): The maximum file size in MB to search. Defaults to 1 MB.

    Returns:
    - A tuple containing:
        1. Success status (True/False).
        2. A list of file paths containing the keyword or an error message.
    """
    if not directory:
        directory='./'

    # 目录存在性检查
    if not os.path.exists(directory):
        raise Exception(f"Error: Directory does not exist: {directory}")
    if not os.path.isdir(directory):
        raise Exception(f"Error: Path is not a directory: {directory}")
        
    matches = []
    try:
        for root, _, files in os.walk(directory):
            for file in files:
                if file_extension and not file.endswith(file_extension):
                    continue
                file_path = os.path.join(root, file)
                if os.path.getsize(file_path) > max_size_mb * 1024 * 1024:
                    continue
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    if keyword in f.read():
                        matches.append(file_path)
        return True, matches
    except Exception as e:
        return False, str(e)

if __name__ == '__main__':
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    success, output = search_files_contents_contain_keyword("./", "mental health", file_extension=None, max_size_mb=100)
    print(output if success else f"Error: {output}")
