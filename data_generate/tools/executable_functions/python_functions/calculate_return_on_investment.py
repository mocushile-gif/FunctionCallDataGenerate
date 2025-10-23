def calculate_return_on_investment(profit: float, investment_cost: float) -> float:
    """
    Calculates the Return on Investment (ROI).

    Parameters:
    - profit (float): The profit from the investment.
    - investment_cost (float): The cost of the investment.

    Returns:
    - float: The ROI percentage.
    """
    roi = (profit / investment_cost) * 100
    return round(roi, 2)

if __name__ == "__main__":
    # Example usage
    profit = 500
    investment_cost = 2000
    roi = calculate_return_on_investment(profit, investment_cost)
    print(f"Return on Investment (ROI): {roi}%")
