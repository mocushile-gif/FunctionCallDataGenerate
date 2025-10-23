import os
import pandas as pd
from dotenv import load_dotenv
import json
load_dotenv()

def search_and_highlight(file_path, keyword, limit=10, case_sensitive=False):
    """
    Search for a keyword in a file and highlight matches.
    Supports text files (.txt), CSV files (.csv), Excel files (.xlsx, .xls), and JSON files (.json, .jsonl).

    Parameters:
    - file_path (str): The path to the file.
    - keyword (str): The keyword to search for.
    - encoding (str): The file encoding. Defaults to 'utf-8'.
    - case_sensitive (bool): Whether the search should be case-sensitive. Defaults to False.

    Returns:
    - A tuple containing:
        1. Success status (True/False).
        2. A formatted message with highlighted matches or an error message.
    """

    def highlight_text_in_line(line, keyword, case_sensitive):
        """ Helper function to highlight keyword matches in a line. """
        if case_sensitive:
            return line.replace(keyword, f"\033[91m{keyword}\033[0m")
        else:
            return line.lower().replace(keyword.lower(), f"\033[91m{keyword}\033[0m")
    
    try:
        file_extension = os.path.splitext(file_path)[1].lower()

        if file_extension in ['.txt', '.json', '.jsonl']:
            # For .txt, .json, and .jsonl files
            matches = []
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_extension == '.json':
                    data=json.load(f)
                    for line in data:
                        line_str = json.dumps(line,ensure_ascii=False)
                        if (case_sensitive and keyword in line_str) or (not case_sensitive and keyword.lower() in line_str.lower()):
                            highlighted_line = highlight_text_in_line(line_str, keyword, case_sensitive)
                            matches.append(highlighted_line)
                else:
                    # For .txt files
                    for line in f:
                        if (case_sensitive and keyword in line) or (not case_sensitive and keyword.lower() in line.lower()):
                            highlighted_line = highlight_text_in_line(line, keyword, case_sensitive)
                            matches.append(highlighted_line)

            if matches:
                return True, f"File: {file_path}\n{len(matches)} matches found for '{keyword}':\n" + "\n".join(matches[:10])
            else:
                return True, f"File: {file_path}\tNo matches found for '{keyword}'."


    except Exception as e:
        return False, f"Error: {str(e)}"


if __name__ == '__main__':
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    # Example usage
    # success, output = search_and_highlight("./json_data/quotes.json", "growth")
    # print(output)

    # success, output = search_and_highlight("./json_data/mental_health_counseling_conversations.jsonl", "growth")
    # print(output)

    success, output = search_and_highlight("./json_data/Top 100 Largest Banks.json", "Bank")
    print(output)
