def calculate_bernoulli_pressure(velocity: float, height: float, density: float, pressure_1: float = 101325) -> float:
    """
    Calculates the pressure of a fluid using Bernoulli's equation.

    Parameters:
    - velocity (float): The velocity of the fluid (m/s).
    - height (float): The height of the fluid (m).
    - density (float): The density of the fluid (kg/m³).
    - pressure_1 (float): The pressure at the first point (Pascal, optional, defaults to standard atmospheric pressure).

    Returns:
    - float: The pressure at the second point in the fluid (Pascal).
    """
    g = 9.81  # Gravitational acceleration in m/s²
    pressure_2 = pressure_1 + 0.5 * density * velocity ** 2 + density * g * height
    return round(pressure_2, 2)

if __name__ == "__main__":
    # Example usage
    velocity = 10  # Velocity in m/s
    height = 5  # Height in meters
    density = 1000  # Density of water in kg/m³
    pressure = calculate_bernoulli_pressure(velocity, height, density)
    print(f"Pressure: {pressure} Pa")
