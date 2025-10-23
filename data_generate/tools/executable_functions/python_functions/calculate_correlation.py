import numpy as np

def calculate_correlation(x: list, y: list) -> float:
    """
    Calculate the Pearson correlation coefficient between two datasets.

    Parameters:
    - x (list): First dataset.
    - y (list): Second dataset.

    Returns:
    - float: The Pearson correlation coefficient.
    """
    return np.corrcoef(x, y)[0, 1]

if __name__ == "__main__":
    x = [1, 2, 3, 4, 5]
    y = [5, 4, 3, 2, 1]
    correlation = calculate_correlation(x, y)
    print(f"Pearson correlation coefficient: {correlation}")
