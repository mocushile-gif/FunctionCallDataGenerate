import json
import os
from dotenv import load_dotenv
load_dotenv()

def read_json_file(file_path, limit=10):
    """
    Read a JSON file and return the first 'n' objects.

    Parameters:
    - file_path (str): The path to the JSON file to be read.
    - limit (int): The maximum number of objects to return. Defaults to 10.

    Returns:
    - A list containing the first 'n' objects in the JSON file,
      or an error message if the operation fails.
    """
    try:
        # Open and load the JSON file
        with open(file_path, 'r') as file:
            data = json.load(file)
        
        # Ensure data is a list or a dictionary
        if isinstance(data, list):
            return data[:limit]  # Return the first 'n' items for a list
        elif isinstance(data, dict):
            keys = list(data.keys())[:limit]
            return {key: data[key] for key in keys}  # Limit dictionary keys
        else:
            return f"Error: The JSON structure must be a list or a dictionary."
    
    except FileNotFoundError:
        return f"Error: The file '{file_path}' does not exist."
    except json.JSONDecodeError:
        return f"Error: Failed to decode JSON from the file '{file_path}'."
    except PermissionError:
        return f"Error: Insufficient permissions to read the file '{file_path}'."
    except Exception as e:
        return f"Error: Unexpected error: {str(e)}"

if __name__ == '__main__':
    # Example usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    file_path = "./json_data/Books.json"  # Replace with the actual JSON file path
    limit = 5  # Number of objects to read
    result = read_json_file(file_path, limit=limit)
    print(result)
