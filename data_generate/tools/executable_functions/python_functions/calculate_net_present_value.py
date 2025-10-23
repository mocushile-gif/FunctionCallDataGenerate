def calculate_net_present_value(cash_flows: list, discount_rate: float) -> float:
    """
    Calculates the Net Present Value (NPV) of a series of cash flows.

    Parameters:
    - cash_flows (list): A list of cash flows (can be negative for outflows and positive for inflows).
    - discount_rate (float): The discount rate as a decimal (e.g., 0.1 for 10%).

    Returns:
    - float: The NPV of the investment.
    """
    npv = sum([cf / (1 + discount_rate) ** t for t, cf in enumerate(cash_flows)])
    return round(npv, 2)

if __name__ == "__main__":
    # Example usage
    cash_flows = [-1000, 200, 300, 400, 500]
    discount_rate = 0.1  # 10% discount rate
    npv = calculate_net_present_value(cash_flows, discount_rate)
    print(f"Net Present Value (NPV): ${npv}")
