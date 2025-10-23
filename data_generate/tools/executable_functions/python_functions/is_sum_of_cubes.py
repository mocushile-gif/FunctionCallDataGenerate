def is_sum_of_cubes(num: int) -> bool:
    """
    Checks if a number is the sum of the cubes of its digits.

    Parameters:
    - num (int): The number to check.

    Returns:
    - bool: True if the number is the sum of the cubes of its digits, False otherwise.
    """
    # Convert the number to a string to easily iterate over its digits
    digits = str(num)
    
    # Calculate the sum of the cubes of the digits
    sum_of_cubes = sum(int(digit)**3 for digit in digits)
    
    # Check if the sum of cubes equals the original number
    return sum_of_cubes == num

# Example usage
if __name__ == '__main__':
    print(is_sum_of_cubes(153))  # True: 1^3 + 5^3 + 3^3 = 153
    print(is_sum_of_cubes(370))  # True: 3^3 + 7^3 + 0^3 = 370
    print(is_sum_of_cubes(371))  # True: 3^3 + 7^3 + 1^3 = 371
    print(is_sum_of_cubes(123666611))  # False: 1^3 + 2^3 + 3^3 = 36, not 123
