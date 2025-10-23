import math

def greatest_common_divisor(a: int, b: int) -> int:
    """
    Computes the greatest common divisor (GCD) of two non-negative integers.

    Parameters:
    - a (int): The first non-negative integer.
    - b (int): The second non-negative integer.

    Returns:
    - int: The greatest common divisor of the two integers.
    """
    return f"The greatest common divisor of {a} and {b} is: {math.gcd(a, b)}"

# Example usage
if __name__ == "__main__":
    a = 56
    b = 98
    gcd = greatest_common_divisor(a, b)
    print(gcd)
