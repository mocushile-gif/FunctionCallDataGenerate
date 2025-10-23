def calculate_exponential_growth_decay(initial_value: float, rate: float, time: float, decay: bool = False) -> float:
    """
    Calculates exponential growth or decay of a quantity over time.

    Parameters:
    - initial_value (float): The initial value of the quantity.
    - rate (float): The growth or decay rate (in percentage).
    - time (float): The time over which the calculation is performed.
    - decay (bool): If True, the function calculates decay; if False, it calculates growth. Defaults to False.

    Returns:
    - float: The quantity after the specified time.
    """
    rate = rate / 100  # Convert to decimal form
    if decay:
        result = initial_value * (1 - rate) ** time
        decay=round(result, 2)
        return f"Decay after {time} years: {decay}"
    else:
        result = initial_value * (1 + rate) ** time
        growth=round(result, 2)
        return f"Growth after {time} years: {growth}"


if __name__ == "__main__":
    # Example usage
    initial_value = 1000
    rate = 5
    time = 10
    growth = calculate_exponential_growth_decay(initial_value, rate, time)
    decay = calculate_exponential_growth_decay(initial_value, rate, time, decay=True)
    print(growth,decay)
