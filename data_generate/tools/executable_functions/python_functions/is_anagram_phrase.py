import re

def is_anagram_phrase(phrase1: str, phrase2: str, ignore_case: bool = True, ignore_punctuation: bool = True, ignore_whitespaces: bool = True, return_cleaned: bool = False) -> bool:
    """
    Checks if two phrases are anagrams of each other with additional customization options.
    
    Parameters:
    - phrase1 (str): The first phrase.
    - phrase2 (str): The second phrase.
    - ignore_case (bool): If True, ignores case (default is True).
    - ignore_punctuation (bool): If True, ignores punctuation (default is True).
    - ignore_whitespaces (bool): If True, ignores spaces (default is True).
    - return_cleaned (bool): If True, returns the cleaned versions of the phrases (default is False).
    
    Returns:
    - bool: True if the phrases are anagrams, False otherwise.
    - tuple: If `return_cleaned` is True, returns the cleaned phrases as a tuple along with the result.
    """
    
    # Define a function to clean each phrase
    def clean_phrase(phrase: str) -> str:
        # Remove punctuation
        if ignore_punctuation:
            phrase = re.sub(r'[^\w\s]', '', phrase)
        
        # Remove spaces if needed
        if ignore_whitespaces:
            phrase = phrase.replace(" ", "")
        
        # Convert to lowercase if needed
        if ignore_case:
            phrase = phrase.lower()
        
        return phrase

    # Clean both phrases
    cleaned_phrase1 = clean_phrase(phrase1)
    cleaned_phrase2 = clean_phrase(phrase2)

    # Compare the cleaned phrases
    are_anagrams = sorted(cleaned_phrase1) == sorted(cleaned_phrase2)
    
    if return_cleaned:
        return are_anagrams, (cleaned_phrase1, cleaned_phrase2)
    
    return are_anagrams

# Example usage:
if __name__ == "__main__":
    # Test cases with additional options
    phrase1 = "Listen!"
    phrase2 = "Silent."
    
    print(is_anagram_phrase(phrase1, phrase2))  # Output: True
    print(is_anagram_phrase(phrase1, phrase2, ignore_case=False))  # Output: False
    print(is_anagram_phrase(phrase1, phrase2, return_cleaned=True))  # Output: (True, ('listen', 'silent'))
    
    phrase1 = "The Morse Code"
    phrase2 = "Here Come dots"
    print(is_anagram_phrase(phrase1, phrase2))  # Output: True
    print(is_anagram_phrase(phrase1, phrase2, ignore_whitespaces=False))  # Output: False
