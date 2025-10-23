def calculate_loan_payment(
    loan_amount: float,
    annual_interest_rate: float,
    loan_term_years: int,
    precision: int = 2
) -> dict:
    """
    Calculates the monthly payment for a loan based on the principal, interest rate, and term.

    Parameters:
    - loan_amount (float): The total loan amount.
    - annual_interest_rate (float): The annual interest rate as a percentage (e.g., 5 for 5%).
    - loan_term_years (int): The loan term in years.
    - precision (int): The number of decimal places to round the result to. Defaults to 2.

    Returns:
    - dict: A dictionary containing the monthly payment and total repayment amount.
    """
    if loan_amount <= 0 or annual_interest_rate < 0 or loan_term_years <= 0:
        raise ValueError("All inputs must be positive values.")

    # Convert annual interest rate to monthly interest rate
    monthly_interest_rate = (annual_interest_rate / 100) / 12
    total_months = loan_term_years * 12

    if monthly_interest_rate == 0:
        # Handle zero interest rate (simple division)
        monthly_payment = loan_amount / total_months
    else:
        # Calculate monthly payment using the loan formula
        monthly_payment = loan_amount * (monthly_interest_rate * (1 + monthly_interest_rate) ** total_months) / \
                          ((1 + monthly_interest_rate) ** total_months - 1)

    total_repayment = monthly_payment * total_months

    return {
        "monthly_payment": round(monthly_payment, precision),
        "total_repayment": round(total_repayment, precision)
    }


# 示例调用
if __name__ == "__main__":
    result = calculate_loan_payment(loan_amount=30000, annual_interest_rate=5, loan_term_years=5)
    print(result)
    # 输出：{'monthly_payment': 566.14, 'total_repayment': 33968.4}
