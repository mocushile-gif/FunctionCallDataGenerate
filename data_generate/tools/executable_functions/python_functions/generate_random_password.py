import random
import string

def generate_random_password(length: int = 12, include_special: bool = True, complexity: str = "medium") -> str:
    """
    Generates a random password of specified length, character types, and complexity.

    Parameters:
    - length (int, optional): The length of the password. Defaults to 12.
    - include_special (bool, optional): Whether to include special characters in the password. Defaults to True.
    - complexity (str, optional): The complexity level of the password. Options: 'low', 'medium', 'high'. Defaults to 'medium'.

    Returns:
    - str: A randomly generated password.
    """
    
    # Define base character sets
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    special = string.punctuation

    # Create character set based on complexity
    if complexity == "low":
        characters = lowercase + digits  # Only lowercase letters and digits
    elif complexity == "high":
        characters = lowercase + uppercase + digits + special  # Include all character types
    else:  # default to medium complexity
        characters = lowercase + uppercase + digits  # Include lowercase, uppercase, and digits
    
    # Add special characters if required
    if include_special and complexity != "low":
        characters += special

    # Generate the password
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

# Example usage
if __name__ == '__main__':
    password_low = generate_random_password(length=12, include_special=False, complexity="low")
    password_medium = generate_random_password(length=12, complexity="medium")
    password_high = generate_random_password(length=16, complexity="high")
    print("Low complexity:", password_low)
    print("Medium complexity:", password_medium)
    print("High complexity:", password_high)
