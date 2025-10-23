def is_power(num: int, base: int) -> bool:
    """
    Checks if a number is a power of a given base.

    Parameters:
    - num (int): The number to check.
    - base (int): The base to check against.

    Returns:
    - bool: True if the number is a power of the base, False otherwise.
    """
    if num <= 0 or base <= 1:
        return False

    # Keep dividing num by base as long as it's divisible by base
    while num % base == 0:
        num //= base

    # If num becomes 1, it means it was a power of the base
    return num == 1


if __name__ == '__main__':
    # Example usage
    print(is_power(27, 3))  # Output: True (3^3 = 27)
    print(is_power(64, 2))  # Output: True (2^6 = 64)
    print(is_power(10, 2))  # Output: False (10 is not a power of 2)
