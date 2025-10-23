def is_prime(n: int) -> bool:
    """
    Checks if a number is prime.

    Parameters:
    - n (int): The number to check.

    Returns:
    - bool: True if the number is prime, False otherwise.
    """
    if n <= 1:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

if __name__ == "__main__":
    # Example usage
    print(is_prime(7))  # Output: True
    print(is_prime(4))  # Output: False
