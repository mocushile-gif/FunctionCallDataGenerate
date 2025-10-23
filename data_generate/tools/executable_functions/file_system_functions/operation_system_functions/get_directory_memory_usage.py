import os
from dotenv import load_dotenv
load_dotenv()
import csv
import json

def get_directory_memory_usage(directory, recursive=True, file_extension=None, sort_by_size=False, output_file=None):
    """
    Calculate memory usage for files and subdirectories in a given directory.

    Parameters:
    - directory (str): The directory to analyze.
    - recursive (bool): Whether to include subdirectories. Defaults to True.
    - file_extension (str): Filter files by extension (e.g., '.txt'). Defaults to None (all files).
    - sort_by_size (bool): Whether to sort results by size in descending order. Defaults to False.
    - output_file (str): Path to save the results as a CSV or JSON file. Defaults to None (no saving).

    Returns:
    - A tuple containing:
        1. Success status (True/False).
        2. A dictionary with file/subdirectory memory usage in bytes or an error message.
    """
    if not directory:
        directory='./'

    if not os.path.exists(directory) or not os.path.isdir(directory):
        raise Exception(f"Error: Directory '{directory}' does not exist.")
    try:
        usage_stats = {}

        # Walk through the directory
        for root, dirs, files in os.walk(directory):
            if not recursive:
                dirs.clear()  # Prevent descending into subdirectories

            # Calculate file sizes
            for file in files:
                if file_extension and not file.endswith(file_extension):
                    continue
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path)
                usage_stats[file_path] = file_size

            if not recursive:
                break

        # Calculate total size for the summary row
        total_size = sum(usage_stats.values())

        # Sort by size if required
        if sort_by_size:
            usage_stats = dict(sorted(usage_stats.items(), key=lambda item: item[1], reverse=True))

        # Convert file sizes to human-readable format
        usage_stats_human = {path: format_size(size) for path, size in usage_stats.items()}

        # Add a summary row for the total size
        usage_stats_human['TOTAL'] = format_size(total_size)

        # Save results to a file if specified
        if output_file:
            save_results(output_file, usage_stats_human)

        return True, usage_stats_human

    except Exception as e:
        return False, f"Error: {str(e)}"
    
def format_size(size_bytes):
    """
    Format the size in bytes to a human-readable format (e.g., KB, MB, GB).
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"

def save_results(output_file, data):
    """
    Save the results to a file in CSV or JSON format.

    Parameters:
    - output_file (str): The path to the output file.
    - data (dict): The data to save.
    """
    try:
        if output_file.endswith('.csv'):
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Path', 'Size'])
                for path, size in data.items():
                    writer.writerow([path, size])
        elif output_file.endswith('.json'):
            with open(output_file, 'w', encoding='utf-8') as jsonfile:
                json.dump(data, jsonfile, indent=4)
        else:
            raise ValueError("Unsupported file format. Use .csv or .json")
    except Exception as e:
        raise RuntimeError(f"Failed to save results: {e}")

if __name__ == '__main__':
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    success, output = get_directory_memory_usage(
        directory="./database",
        recursive=True,
        file_extension="",
        sort_by_size=True,
        # output_file="output.csv"
    )
    print(output)