def calculate_average(numbers,weights=None,exclude_outliers=False,rounding=2):
    """
    Calculates the arithmetic mean of a list of numbers with additional options.

    Parameters:
    - data (dict): A dictionary containing:
        - numbers (list of float): The list of numbers.
        - weights (list of float, optional): Weights for weighted average. Must match the length of 'numbers'.
        - exclude_outliers (bool, optional): Whether to exclude statistical outliers. Defaults to False.
        - rounding (int, optional): The number of decimal places to round the result. Defaults to 2.

    Returns:
    - float: The calculated average, or None if no valid numbers are provided.
    """

    # Validate input
    if not numbers or not isinstance(numbers, list) or not all(isinstance(n, (int, float)) for n in numbers):
        raise ValueError("Error: 'numbers' must be a non-empty list of numbers.")
    if weights and (len(weights) != len(numbers) or not all(isinstance(w, (int, float)) for w in weights)):
        raise ValueError("Error: 'weights' must be a list of the same length as 'numbers' with numeric values.")

    # Remove outliers if requested
    if exclude_outliers:
        mean = sum(numbers) / len(numbers)
        std_dev = (sum((x - mean) ** 2 for x in numbers) / len(numbers)) ** 0.5
        numbers = [x for x in numbers if (mean - 2 * std_dev) <= x <= (mean + 2 * std_dev)]

    # Calculate average
    if weights:
        weighted_sum = sum(n * w for n, w in zip(numbers, weights))
        total_weight = sum(weights)
        average = weighted_sum / total_weight if total_weight != 0 else None
    else:
        average = sum(numbers) / len(numbers) if numbers else None

    # Round the result if specified
    if average is not None:
        average = round(average, rounding)

    return average


if __name__ == '__main__':
    # Example usage
    numbers=[6303.44, 5623.12, 5400.28, 4578.28, 3875.39]
    weights=[1, 1, 1, 1, 1]
    exclude_outliers=True
    rounding=2

    result = calculate_average(numbers,exclude_outliers=True,rounding=rounding)
    print(result)
