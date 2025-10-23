def binary_to_decimal(binary: str) -> int:
    """
    Converts a binary number (as a string) to its decimal equivalent.

    Parameters:
    - binary (str): The binary number (as a string).

    Returns:
    - int: The decimal equivalent of the binary number.
    """
    # Convert the binary string to a decimal integer
    return int(binary, 2)

if __name__ == "__main__":
    # Example usage
    binary = "110100000001"

    result = binary_to_decimal(binary)
    print(f"The decimal equivalent of binary {binary} is: {result}")
