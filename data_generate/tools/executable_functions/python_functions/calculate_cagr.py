def calculate_cagr(start_value: float, end_value: float, years: int) -> float:
    """
    Calculates the Compound Annual Growth Rate (CAGR) of an investment.

    Parameters:
    - start_value (float): The initial value of the investment.
    - end_value (float): The final value of the investment.
    - years (int): The number of years between the initial and final values.

    Returns:
    - float: The CAGR as a percentage.
    """
    # CAGR formula: (End Value / Start Value) ^ (1 / Years) - 1
    cagr = (end_value / start_value) ** (1 / years) - 1
    return round(cagr * 100, 2)  # Return as a percentage

if __name__ == "__main__":
    # Example usage
    start_value = 1000
    end_value = 2000
    years = 5
    result = calculate_cagr(start_value, end_value, years)
    print(f"The CAGR is: {result}%")
