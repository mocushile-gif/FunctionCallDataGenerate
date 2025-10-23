import numpy_financial as npf

def calculate_internal_rate_of_return(cash_flows: list) -> float:
    """
    Calculates the Internal Rate of Return (IRR) for a series of cash flows.

    Parameters:
    - cash_flows (list): A list of cash flows (can be negative for outflows and positive for inflows).

    Returns:
    - float: The IRR, expressed as a percentage.
    """
    irr = npf.irr(cash_flows) * 100
    return round(irr, 2)

# Example usage
if __name__ == "__main__":
    cash_flows = [-1000, 200, 300, 400, 500]
    irr = calculate_internal_rate_of_return(cash_flows)
    print(f"Internal Rate of Return (IRR): {irr}%")
