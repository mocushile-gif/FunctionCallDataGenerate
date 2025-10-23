def calculate_trapezoidal_integration(func: str, a: float, b: float, n: int = 10000) -> float:
    import numpy as np
    import math
    """
    Calculates the definite integral of a function using the trapezoidal rule.

    Parameters:
    - func (str): The function to integrate, expressed as a string (e.g., "x**2 + 2*x").
    - a (float): The lower limit of integration.
    - b (float): The upper limit of integration.
    - n (int): The number of subdivisions for the trapezoidal approximation. Defaults to 10000.

    Returns:
    - float: The approximated integral value.
    """
    # Ensure that n is positive
    if n <= 0:
        raise ValueError("The number of subdivisions 'n' must be a positive integer.")
    
    # Convert the function string to a lambda function
    try:
        # Ensure that 'math' or 'np' is available in the context of eval
        f = eval(f"lambda x: {func}", {"np": np, "x": 0})
    except Exception as e:
        raise ValueError(f"Invalid function: {func}. Error: {e}")

    # Generate n evenly spaced points between a and b
    x = np.linspace(a, b, n + 1)
    y = f(x)

    # Apply the trapezoidal rule
    h = (b - a) / n
    integral = (h / 2) * (y[0] + 2 * sum(y[1:-1]) + y[-1])

    return f"Definite integral of '{func}' from {a} to {b}: {round(integral, 6)}"

if __name__ == "__main__":
    # Example usage
    function = "np.cos(x) - x"  # Function to integrate
    lower_limit = 0  # Lower limit of integration
    upper_limit = 3  # Upper limit of integration
    subdivisions = 10000  # Number of subdivisions
    result = calculate_trapezoidal_integration(function, lower_limit, upper_limit, subdivisions)
    print(result)
