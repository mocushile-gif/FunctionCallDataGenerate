def calculate_factorial(n: int) -> int:
    """
    Calculates the factorial of a non-negative integer.

    Parameters:
    - n (int): The non-negative integer.

    Returns:
    - int: The factorial of n.
    """
    
    # Error handling for invalid input
    if n < 0 or not isinstance(n, int):
        raise ValueError("Input must be a non-negative integer.")
    
    result = 1
    for i in range(1, n + 1):
        result *= i
    return f"Factorial of {n} is: {result}"

if __name__ == "__main__":
    # Example usage
    n = 10
    print(calculate_factorial(n))
