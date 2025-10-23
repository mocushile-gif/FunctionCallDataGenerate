def calculate_wind_chill(temperature: float, wind_speed: float, precision: int = 2) -> float:
    """
    Calculates the wind chill index (perceived temperature) based on temperature and wind speed.

    Parameters:
    - temperature (float): The actual air temperature in Celsius.
    - wind_speed (float): The wind speed in kilometers per hour.
    - precision (int): The number of decimal places to round the result to. Defaults to 2.

    Returns:
    - float: The wind chill temperature in Celsius.
    """
    if temperature > 10 or wind_speed <= 4.8:
        raise ValueError("Wind chill calculation is only valid for temperatures ≤10°C and wind speeds >4.8 km/h.")
    
    # Wind chill formula (using the formula: T_wc = 13.12 + 0.6215T - 11.37v^0.16 + 0.3965Tv^0.16)
    wind_chill = (
        13.12 +
        0.6215 * temperature -
        11.37 * (wind_speed ** 0.16) +
        0.3965 * temperature * (wind_speed ** 0.16)
    )

    return round(wind_chill, precision)

# Example usage
if __name__ == "__main__":
    try:
        temp = -5  # Example temperature in °C
        speed = 20  # Example wind speed in km/h
        wc = calculate_wind_chill(temp, speed)
        print(f"Wind Chill Temperature: {wc}°C")
    except ValueError as e:
        print(f"Error: {e}")
