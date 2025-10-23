def normalize_data(data: list) -> list:
    """
    Normalizes a list of numbers to a 0-1 range.

    Parameters:
    - data (list): A list of numerical values.

    Returns:
    - list: The normalized data, with values between 0 and 1.
    """
    min_value = min(data)
    max_value = max(data)
    normalized_data = [(x - min_value) / (max_value - min_value) for x in data]
    return normalized_data

# Example usage
if __name__ == "__main__":
    data = [1, 2, 3, 4, 5]
    normalized = normalize_data(data)
    print(f"Normalized Data: {normalized}")
