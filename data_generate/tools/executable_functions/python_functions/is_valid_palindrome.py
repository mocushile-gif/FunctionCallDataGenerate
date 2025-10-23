def is_valid_palindrome(s: str) -> bool:
    """
    Checks if a string is a valid palindrome, considering only alphanumeric characters and ignoring case.

    Parameters:
    - s (str): The input string to check.

    Returns:
    - bool: True if the string is a valid palindrome, False otherwise.
    """
    # Remove non-alphanumeric characters and convert to lowercase
    cleaned_string = ''.join(char.lower() for char in s if char.isalnum())
    
    # Check if the cleaned string is equal to its reverse
    return cleaned_string == cleaned_string[::-1]


if __name__ == '__main__':
    input_string = "A man, a plan, a canal, Panama"
    print(is_valid_palindrome(input_string))  # Output: True

    input_string_invalid = "Hello, World!"
    print(is_valid_palindrome(input_string_invalid))  # Output: False
