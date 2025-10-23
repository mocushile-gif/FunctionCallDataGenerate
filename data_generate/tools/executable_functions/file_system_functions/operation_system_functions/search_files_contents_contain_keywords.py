import os
from dotenv import load_dotenv

load_dotenv()

def search_files_contents_contain_keywords(directory, keywords, file_extension=None, max_size_mb=1):
    """
    Search for files containing all specified keywords within a directory.

    Parameters:
    - directory (str): The directory to search in.
    - keywords (list): A list of keywords to search for.
    - file_extension (str): The file extension to filter by (e.g., '.txt'). Defaults to None (all files).
    - max_size_mb (int): The maximum file size in MB to search. Defaults to 1 MB.

    Returns:
    - A tuple containing:
        1. Success status (True/False).
        2. A list of file paths containing all keywords, or an error message.
    """
    # Set the working directory
    
    

    # Default directory to the current directory if not provided
    if not directory:
        directory = './'

    if not os.path.exists(directory):
        raise Exception(f"Error: Directory does not exist: {directory}")
    if not os.path.isdir(directory):
        raise Exception(f"Error: Path is not a directory: {directory}")
        
    # Ensure keywords is a list
    if not isinstance(keywords, list):
        return False, "Keywords must be provided as a list."

    # Initialize results
    matches = []

    try:
        for root, _, files in os.walk(directory):
            for file in files:
                # Filter by file extension if specified
                if file_extension and not file.endswith(file_extension):
                    continue

                file_path = os.path.join(root, file)

                # Skip files exceeding the size limit
                if os.path.getsize(file_path) > max_size_mb * 1024 * 1024:
                    continue

                # Read the file and check for all keywords
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    file_content = f.read()
                    if all(keyword in file_content for keyword in keywords):
                        matches.append(file_path)

        return True, matches
    except Exception as e:
        return False, str(e)

if __name__ == '__main__':
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    success, output = search_files_contents_contain_keywords("./", ["a","r","d"], max_size_mb=2)
    print(output if success else f"Error: {output}")
