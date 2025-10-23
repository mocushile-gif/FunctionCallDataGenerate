from typing import List

def calculate_order_total(items: List[str], quantities: List[int], prices: List[float]) -> float:
    """
    Calculates the total cost of an order based on the items, quantities, and prices.

    Parameters:
    - items (List[str]): A list of item names.
    - quantities (List[int]): A list of corresponding quantities for each item.
    - prices (List[float]): A list of corresponding prices for each item.

    Returns:
    - float: The total cost of the order.
    """
    # Check if all lists have the same length
    if not (len(items) == len(quantities) == len(prices)):
        raise ValueError("The lengths of items, quantities, and prices lists must be the same.")
    
    # Calculate the total cost
    total_cost = sum(qty * price for qty, price in zip(quantities, prices))
    
    return round(total_cost, 2)

if __name__ == "__main__":
    # Example usage
    items = ["Apple", "Banana", "Orange"]
    quantities = [2, 3, 1]
    prices = [0.5, 0.3, 0.8]
    
    total = calculate_order_total(items, quantities, prices)
    print(f"The total cost of the order is: ${total}")
