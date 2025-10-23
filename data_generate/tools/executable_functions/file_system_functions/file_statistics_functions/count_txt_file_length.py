import re
import os
from dotenv import load_dotenv
load_dotenv()

def count_txt_file_length(file_path: str, include_punctuation: bool = True, include_numbers: bool = True) -> int:
    """
    Calculates the length of a text with options to include/exclude punctuation and numbers.
    Treats English words as one unit and each Chinese character as one unit.

    Parameters:
    - text (str): The input text.
    - include_punctuation (bool): Whether to include punctuation in the count. Default is True.
    - include_numbers (bool): Whether to include numbers in the count. Default is True.

    Returns:
    - int: The calculated length of the text.
    """
    
    
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    # Define patterns for punctuation, numbers, and English words
    punctuation_pattern = r'[^\w\s\u4e00-\u9fff]'  # Matches punctuation
    number_pattern = r'\d'                        # Matches numbers
    english_word_pattern = r'[a-zA-Z]+'           # Matches English words

    # Exclude punctuation if not included
    if not include_punctuation:
        text = re.sub(punctuation_pattern, '', text)

    # Exclude numbers if not included
    if not include_numbers:
        text = re.sub(number_pattern, '', text)

    # Count Chinese characters and English words
    chinese_characters = re.findall(r'[\u4e00-\u9fff]', text)
    english_words = re.findall(english_word_pattern, text)

    # Calculate total length
    total_length = len(chinese_characters) + len(english_words)

    return f"Text length: {total_length}"


if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    # Example usage
    file_path='./txt_data/Friends TV Show Script.txt'
    length = count_txt_file_length(file_path, include_punctuation=False, include_numbers=False)
    print(length)
