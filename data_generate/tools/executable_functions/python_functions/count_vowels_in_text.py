import string

def count_vowels_in_text(text: str) -> dict:
    """
    Counts the number of vowels (a, e, i, o, u) in a given text and provides a breakdown.
    Ignores punctuation and considers vowels case-insensitively.

    Parameters:
    - text (str): The input text.

    Returns:
    - dict: A dictionary with the total count of vowels and counts for each vowel type.
    """
    # Define vowels
    vowels = "aeiouAEIOU"
    
    # Initialize vowel count dictionary
    vowel_count = {'total': 0, 'a': 0, 'e': 0, 'i': 0, 'o': 0, 'u': 0}

    # Clean the text: remove punctuation and consider only alphabetic characters
    cleaned_text = ''.join(char.lower() for char in text if char.isalpha())
    
    # Count vowels
    for char in cleaned_text:
        if char in vowels.lower():
            vowel_count['total'] += 1
            vowel_count[char] += 1
    
    return vowel_count

# Example usage
if __name__ == "__main__":
    text = "Hello, how many vowels are in this sentence?"
    result = count_vowels_in_text(text)
    
    print(f"Total vowels: {result['total']}")
    for vowel, count in result.items():
        if vowel != 'total':
            print(f"Vowel '{vowel}': {count}")
