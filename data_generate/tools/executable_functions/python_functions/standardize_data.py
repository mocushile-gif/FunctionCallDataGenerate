def standardize_data(data: list) -> list:
    """
    Standardizes a list of numbers to have a mean of 0 and standard deviation of 1.

    Parameters:
    - data (list): A list of numerical values.

    Returns:
    - list: The standardized data.
    """
    mean_value = sum(data) / len(data)
    std_dev = (sum([(x - mean_value) ** 2 for x in data]) / len(data)) ** 0.5
    standardized_data = [(x - mean_value) / std_dev for x in data]
    return standardized_data

# Example usage
if __name__ == "__main__":
    data = [1, 2, 3, 4, 5]
    standardized = standardize_data(data)
    print(f"Standardized Data: {standardized}")
