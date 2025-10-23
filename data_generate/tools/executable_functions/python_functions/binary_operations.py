def binary_operations(a: str, b: str, operation: str) -> str:
    """
    Performs various binary operations (addition, subtraction, multiplication, division) on two binary numbers.
    
    Parameters:
    - a (str): The first binary number.
    - b (str): The second binary number.
    - operation (str): The operation to perform. One of 'add', 'subtract', 'multiply', 'divide'.
    
    Returns:
    - str: The result of the operation, as a binary string.
    """
    
    # Convert binary strings to integers
    num1 = int(a, 2)
    num2 = int(b, 2)
    
    if operation == "add":
        result = num1 + num2
    elif operation == "subtract":
        result = num1 - num2
    elif operation == "multiply":
        result = num1 * num2
    elif operation == "divide":
        # Handle division by zero
        if num2 == 0:
            return "Error: Division by zero"
        quotient = num1 // num2
        remainder = num1 % num2
        return f"Quotient: {bin(quotient)[2:]}, Remainder: {bin(remainder)[2:]}"
    else:
        return "Error: Invalid operation"

    # Convert the result back to binary
    return bin(result)[2:]

# Example usage:
if __name__ == "__main__":
    binary1 = "1101"  # 13 in decimal
    binary2 = "1011"  # 11 in decimal

    print(f"Addition: {binary_operations(binary1, binary2, 'add')}")
    print(f"Subtraction: {binary_operations(binary1, binary2, 'subtract')}")
    print(f"Multiplication: {binary_operations(binary1, binary2, 'multiply')}")
    print(f"Division: {binary_operations(binary1, binary2, 'divide')}")
