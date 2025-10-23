def linear_regression(x: list, y: list) -> tuple:
    """
    Performs linear regression (least squares method) to find the best-fit line.

    Parameters:
    - x (list): A list of independent variable values.
    - y (list): A list of dependent variable values.

    Returns:
    - tuple: A tuple containing the slope and intercept of the best-fit line.
    """
    n = len(x)
    x_mean = sum(x) / n
    y_mean = sum(y) / n

    # Calculate the slope (m) and intercept (b) for the equation y = mx + b
    numerator = sum([(x[i] - x_mean) * (y[i] - y_mean) for i in range(n)])
    denominator = sum([(x[i] - x_mean) ** 2 for i in range(n)])

    slope = numerator / denominator
    intercept = y_mean - slope * x_mean

    return round(slope, 2), round(intercept, 2)

if __name__ == "__main__":
    # Example usage
    x = [1, 2, 3, 4, 5]
    y = [2, 4, 5, 4, 5]
    slope, intercept = linear_regression(x, y)
    print(f"Slope: {slope}, Intercept: {intercept}")
