import os
from dotenv import load_dotenv
load_dotenv()

def merge_txt_files(file_paths, output_file, encoding='utf-8'):

    """
    Merge the content of multiple files into a single file.

    Parameters:
    - file_paths (list): List of file paths to merge.
    - output_file (str): Path to the output file.
    - encoding (str): The file encoding. Defaults to 'utf-8'.

    Returns:
    - A tuple containing:
        1. Success status (True/False).
        2. A formatted success message or an error message.
    """
    with open(output_file, 'w', encoding=encoding) as outfile:
        for file_path in file_paths:
            with open(file_path, 'r', encoding=encoding) as infile:
                outfile.write(infile.read())
                outfile.write("\n")  # Add a newline between files
    return True, f"Merged files: {', '.join(file_paths)}\tOutput: {output_file}"

if __name__ == '__main__':
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    success, output = merge_txt_files(["./txt_data/Friends TV Show Script.txt", "./txt_data/birth_rate_and_life_expectancy_2010.txt"], "merged_file.txt")
    print(output)
