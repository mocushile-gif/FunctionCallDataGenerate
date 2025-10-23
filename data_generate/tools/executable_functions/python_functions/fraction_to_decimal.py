def fraction_to_decimal(numerator: int, denominator: int) -> float:
    """
    Converts a fraction to a decimal.

    Parameters:
    - numerator (int): The numerator of the fraction.
    - denominator (int): The denominator of the fraction.

    Returns:
    - float: The decimal value of the fraction.
    """
    if denominator == 0:
        raise ValueError("Denominator cannot be zero.")
    return round(numerator / denominator, 4)

if __name__ == "__main__":
    # Example usage
    numerator = 3
    denominator = 4
    decimal_value = fraction_to_decimal(numerator, denominator)
    print(f"Decimal Value: {decimal_value}")
