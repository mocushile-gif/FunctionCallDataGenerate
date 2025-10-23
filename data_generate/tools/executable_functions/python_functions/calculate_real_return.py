def calculate_real_return(principal: float, annual_rate: float, years: int, inflation_rate: float) -> float:
    """
    Calculates the real return of an investment considering compound interest and inflation.

    Parameters:
    - principal (float): The initial investment amount.
    - annual_rate (float): The annual nominal interest rate in percentage.
    - years (int): The number of years the investment is held.
    - inflation_rate (float): The annual inflation rate in percentage.

    Returns:
    - float: The real value of the investment after inflation.
    """
    compound_interest = principal * (1 + annual_rate / 100) ** years
    real_return = compound_interest / (1 + inflation_rate / 100) ** years
    return round(real_return, 2)

if __name__ == "__main__":
    # Example usage
    principal = 1000  # Initial investment
    annual_rate = 5  # Annual interest rate (7%)
    years = 10  # Investment duration in years
    inflation_rate = 4  # Annual inflation rate (2%)
    real_value = calculate_real_return(principal, annual_rate, years, inflation_rate)
    print(f"Real Value After Inflation: ${real_value}")
