def get_fibonacci_number(n: int) -> int:
    """
    Calculates the n-th Fibonacci number.

    Parameters:
    - n (int): The index of the Fibonacci sequence.

    Returns:
    - int: The n-th Fibonacci number.
    """
    
    # Error handling for invalid input
    if n < 0 or not isinstance(n, int):
        raise ValueError("Input must be a non-negative integer.")
    
    # First two Fibonacci numbers are 0 and 1
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

if __name__ == "__main__":
    # Example usage
    n = 24
    print(f"The {n}-th Fibonacci number is: {get_fibonacci_number(n)}")
