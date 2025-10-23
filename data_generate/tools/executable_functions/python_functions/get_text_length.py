import re

def get_text_length(text: str, include_punctuation: bool = True, include_numbers: bool = True) -> int:
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
    # Example usage
    sample_text = "这是一个测试文本，包含中文和English words，以及标点符号！123"
    length = get_text_length(sample_text, include_punctuation=False, include_numbers=False)
    print(length)
