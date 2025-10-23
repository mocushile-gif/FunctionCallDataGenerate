import math

def calculate_standard_deviation(data: list) -> float:
    """
    Calculates the standard deviation of a list of numbers.

    Parameters:
    - data (list): The list of numbers.

    Returns:
    - float: The standard deviation of the numbers.
    """
    mean = sum(data) / len(data)
    variance = sum((x - mean) ** 2 for x in data) / len(data)
    return round(math.sqrt(variance), 2)

if __name__ == "__main__":
    # Example usage
    data = [10, 12, 23, 23, 16, 23, 21, 16]
    std_dev = calculate_standard_deviation(data)
    print(f"Standard Deviation: {std_dev}")
