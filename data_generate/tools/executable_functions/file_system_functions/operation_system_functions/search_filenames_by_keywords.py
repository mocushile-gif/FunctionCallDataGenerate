import os
from dotenv import load_dotenv
load_dotenv()

def search_filenames_by_keywords(directory, keywords, case_sensitive=False):
    """
    Search for files in a directory and its subdirectories where the filename contains any of the specified keywords.

    Parameters:
    - directory (str): The absolute path of the directory to search within.
    - keywords (list of str): A list of keywords to search for in filenames.
    - case_sensitive (bool): Whether the search should be case-sensitive. Defaults to False.

    Returns:
    - A tuple containing:
        1. Success status (True/False).
        2. A list of file paths that match any of the specified keywords.
        3. A success message or error message.
    """
    
    try:
        if not os.path.exists(directory):
            return False, [], f"Error: Directory '{directory}' does not exist."
        
        if not keywords or not isinstance(keywords, list):
            return False, [], "Error: Keywords must be a non-empty list of strings."

        matched_files = []
        for root, _, files in os.walk(directory):
            for file in files:
                # 检查文件名是否包含任意关键词
                if any(
                    (case_sensitive and keyword in file) or 
                    (not case_sensitive and keyword.lower() in file.lower()) 
                    for keyword in keywords
                ):
                    matched_files.append(os.path.join(root, file))

        if matched_files:
            return True, f"Found {len(matched_files)} matching files in '{directory}'.", matched_files
        else:
            return True, f"No files found in '{directory}' containing the specified keywords.", []

    except Exception as e:
        return False, [], f"Error: {str(e)}"

# Example usage
if __name__ == '__main__':
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    success, file_paths, message = search_filenames_by_keywords("./", ["c"], case_sensitive=False)
    print(success, file_paths, message)
