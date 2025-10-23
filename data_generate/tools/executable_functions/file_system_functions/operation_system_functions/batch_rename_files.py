import os
import json
import re
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
load_dotenv()

def batch_rename_files(directory: str, pattern: str = "*", new_name_pattern: str = "file_{n}",
                       start_number: int = 1, extension: Optional[str] = None,
                       ):
    """
    Batch rename files in a directory.

    Parameters:
    - directory (str): Directory containing files to rename.
    - pattern (str): File pattern to match (e.g., "*.jpg", "image*").
    - new_name_pattern (str): New name pattern with {n} for number placeholder.
    - start_number (int): Starting number for renaming.
    - extension (str, optional): Keep specific extension, if None keeps original.

    Returns:
    - dict: Processing result information.
    """
    
    try:
        # Check if directory exists
        if not os.path.exists(directory):
            return {"error": f"Directory not found: {directory}"}
        
        if not os.path.isdir(directory):
            return {"error": f"Path is not a directory: {directory}"}
        
        # Validate parameters
        if start_number < 0:
            return {"error": "start_number must be non-negative"}
        
        # Get all files in directory
        all_files = os.listdir(directory)
        
        # Filter files based on pattern
        if pattern == "*":
            files_to_rename = [f for f in all_files if os.path.isfile(os.path.join(directory, f))]
        else:
            # Convert pattern to regex
            pattern_regex = pattern.replace("*", ".*").replace("?", ".")
            files_to_rename = [f for f in all_files 
                             if os.path.isfile(os.path.join(directory, f)) 
                             and re.match(pattern_regex, f)]
        
        if not files_to_rename:
            return {"error": f"No files found matching pattern: {pattern}"}
        
        # Sort files for consistent ordering
        files_to_rename.sort()
        
        # Perform renaming
        renamed_files = []
        current_number = start_number
        
        for old_name in files_to_rename:
            old_path = os.path.join(directory, old_name)
            
            # Get file extension
            if extension:
                file_ext = extension if extension.startswith('.') else f'.{extension}'
            else:
                file_ext = os.path.splitext(old_name)[1]
            
            # Generate new name
            new_name = new_name_pattern.replace("{n}", str(current_number)) + file_ext
            new_path = os.path.join(directory, new_name)
            
            # Check if new name already exists
            if os.path.exists(new_path) and old_path != new_path:
                # Find next available number
                counter = 1
                while os.path.exists(new_path):
                    new_name = new_name_pattern.replace("{n}", f"{current_number}_{counter}") + file_ext
                    new_path = os.path.join(directory, new_name)
                    counter += 1
            
            # Rename file
            try:
                os.rename(old_path, new_path)
                renamed_files.append({
                    "old_name": old_name,
                    "new_name": new_name,
                    "old_path": old_path,
                    "new_path": new_path,
                    "number": current_number
                })
                current_number += 1
            except Exception as e:
                return {"error": f"Error renaming {old_name}: {str(e)}"}
        
        result = {
            "directory": directory,
            "operation": "batch_rename_files",
            "parameters": {
                "pattern": pattern,
                "new_name_pattern": new_name_pattern,
                "start_number": start_number,
                "extension": extension
            },
            "files_renamed": len(renamed_files),
            "renamed_files": renamed_files,
            "success": True
        }
        
        return result
        
    except Exception as e:
        return {"error": f"Error in batch rename: {str(e)}"}

if __name__ == "__main__":
    # Example usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    result = batch_rename_files("./", pattern="*.txt", new_name_pattern="text_{n}")
    print(json.dumps(result, indent=2)) 