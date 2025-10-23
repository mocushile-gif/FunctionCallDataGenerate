import random
import string

def generate_random_string(
    length: int,
    uppercase: bool = True,
    lowercase: bool = True,
    digits: bool = True,
    special_chars: bool = False
) -> str:
    """
    Generates a random string of specified length and character types.

    Parameters:
    - length (int): The length of the random string.
    - uppercase (bool, optional): Include uppercase letters. Defaults to True.
    - lowercase (bool, optional): Include lowercase letters. Defaults to True.
    - digits (bool, optional): Include digits. Defaults to True.
    - special_chars (bool, optional): Include special characters. Defaults to False.

    Returns:
    - str: A random string based on the specified parameters.
    """
    char_pool = ""
    
    if uppercase:
        char_pool += string.ascii_uppercase
    if lowercase:
        char_pool += string.ascii_lowercase
    if digits:
        char_pool += string.digits
    if special_chars:
        char_pool += string.punctuation

    if not char_pool:
        raise ValueError("At least one character type must be selected.")
    
    return ''.join(random.choice(char_pool) for _ in range(length))

if __name__ == "__main__":
    random_string = generate_random_string(12, uppercase=True, lowercase=True, digits=True, special_chars=True)
    print(random_string)
