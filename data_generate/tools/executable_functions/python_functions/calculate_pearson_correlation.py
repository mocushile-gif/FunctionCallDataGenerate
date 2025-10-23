import math
from typing import List


def calculate_pearson_correlation(x: List[float], y: List[float]) -> float:
    """
    Calculates the Pearson correlation coefficient between two sets of data.

    Parameters:
    - x (List[float]): The first dataset.
    - y (List[float]): The second dataset.

    Returns:
    - float: The Pearson correlation coefficient between the two datasets.
    """
    if len(x) != len(y):
        raise ValueError("Datasets must have the same length.")
    
    n = len(x)
    mean_x = sum(x) / n
    mean_y = sum(y) / n
    
    numerator = sum((x_i - mean_x) * (y_i - mean_y) for x_i, y_i in zip(x, y))
    denominator = math.sqrt(sum((x_i - mean_x)**2 for x_i in x) * sum((y_i - mean_y)**2 for y_i in y))
    
    if denominator == 0:
        return 0.0  # Avoid division by zero
    
    correlation = numerator / denominator
    
    return f"Pearson correlation coefficient: {round(correlation, 4)}"
    return round(correlation, 4)

if __name__ == "__main__":
    x = [1, 2, 3, 4, 5]
    y = [5, 4, 3, 2, 1]
    correlation = calculate_pearson_correlation(x, y)
    print(correlation)
