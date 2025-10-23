def decimal_to_binary(a: int) -> str:
    """
    Converts a decimal number to its binary equivalent.

    Parameters:
    - a (int): The decimal number.

    Returns:
    - str: The binary equivalent of the decimal number.
    """
    return bin(a)[2:]

if __name__ == "__main__":
    decimal = 13

    result = decimal_to_binary(decimal)
    print(f"Decimal {decimal} to binary is: {result}")
