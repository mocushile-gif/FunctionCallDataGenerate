import os
from dotenv import load_dotenv
load_dotenv()

def write_to_file(file_path, data, mode="w", encoding="utf-8",):
    """
    Write data to a file.

    Parameters:
    - file_path (str): Path to the file.
    - data (str): Data to write.
    - mode (str): File write mode ('w' for overwrite, 'a' for append).
    - encoding (str): Encoding of the file.

    Returns:
    - str: Confirmation message.
    """
    with open(file_path, mode, encoding=encoding) as file:
        file.write(data)
    return f"Data written to {file_path}"

if __name__ == '__main__':
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    file_path = "output.txt"  # Replace with the desired file path
    content = "This is an example content to be written to the file."
    result = write_to_file(file_path, content)
    print(result)
