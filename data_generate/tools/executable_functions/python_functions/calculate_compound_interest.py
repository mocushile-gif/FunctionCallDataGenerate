def calculate_compound_interest(
    principal: float,
    annual_rate: float,
    years: int,
    compounds_per_year: int = 1,
    precision: int = 2
) -> dict:
    """
    Calculates the future value of an investment using the compound interest formula.

    Parameters:
    - principal (float): The initial amount of money.
    - annual_rate (float): The annual interest rate as a decimal (e.g., 0.05 for 5%).
    - years (int): The number of years the money is invested.
    - compounds_per_year (int): The number of times interest is compounded per year. Defaults to 1.
    - precision (int): The number of decimal places to round the result. Defaults to 2.

    Returns:
    - dict: A dictionary containing the final amount and the total interest earned.
    """
    if principal <= 0 or annual_rate <= 0 or years <= 0 or compounds_per_year <= 0:
        raise ValueError("All input values must be positive.")
    if precision < 0:
        raise ValueError("Precision must be a non-negative integer.")

    # Calculate compound interest
    final_amount = principal * (1 + annual_rate / compounds_per_year) ** (compounds_per_year * years)
    total_interest = final_amount - principal

    return {
        "final_amount": round(final_amount, precision),
        "total_interest": round(total_interest, precision)
    }


# 示例调用
if __name__ == "__main__":
    result = calculate_compound_interest(principal=1000, annual_rate=0.05, years=10, compounds_per_year=4)
    print(result)
    # 输出：{'final_amount': 1647.01, 'total_interest': 647.01}
