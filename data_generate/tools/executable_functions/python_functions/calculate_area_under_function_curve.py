import numpy as np

def calculate_area_under_function_curve(function: str = "x^3", start_x: int = 0, end_x: int = 10, method: str = "trapezoid") -> float:
    """
    Calculate the area under a curve for a specified function between two x values.

    Parameters:
    - function (str): The function to integrate, represented as a string. For example, 'x^3'.
    - start_x (int): The starting x-value to integrate over.
    - end_x (int): The ending x-value to integrate over.
    - method (str): The method of numerical integration to use. Choices are 'trapezoid' or 'simpson'.

    Returns:
    - float: The calculated area under the curve.
    """

    # Convert the function string to a callable function
    function=function.replace('^','**')
    def func(x):
        return eval(function)

    # Check which method to use for numerical integration
    x_values = np.linspace(start_x, end_x, 1000)  # Create a range of x-values
    y_values = func(x_values)  # Compute the function values at those x-values
    
    if method == "trapezoid":
        # Trapezoidal rule for integration
        area = np.trapz(y_values, x_values)
    elif method == "simpson":
        # Simpson's rule for integration
        area = np.simpson(y_values, x_values)
    else:
        raise ValueError("Method must be 'trapezoid' or 'simpson'")

    return area

# Example usage:
if __name__ == "__main__":
    area = calculate_area_under_function_curve(function="2*x^2 + 3*x + 1", start_x=1, end_x=5, method="trapezoid")
    print(f"Calculated area: {area}")
