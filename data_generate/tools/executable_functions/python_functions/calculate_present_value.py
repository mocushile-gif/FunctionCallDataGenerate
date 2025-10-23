def calculate_present_value(future_value: float, rate: float, periods: int) -> float:
    """
    Calculates the Present Value (PV) of a future sum.

    Parameters:
    - future_value (float): The future value.
    - rate (float): The interest rate as a percentage (e.g., 5 for 5%).
    - periods (int): The number of periods.

    Returns:
    - float: The present value.
    """
    rate = rate / 100  # Convert percentage to decimal
    pv = future_value / (1 + rate) ** periods
    return round(pv, 2)

if __name__ == "__main__":
    # Example usage
    future_value = 1500
    rate = 5  # 5%
    periods = 5
    pv = calculate_present_value(future_value, rate, periods)
    print(f"Present Value (PV): ${pv}")
