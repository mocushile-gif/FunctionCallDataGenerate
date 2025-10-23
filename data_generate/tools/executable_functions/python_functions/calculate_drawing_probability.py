from math import comb

def calculate_drawing_probability(total_items: int, satisfying_items: int, drawn_items: int, expect_items: int) -> float:
    """
    Calculates the probability of drawing at least 'expect_items' satisfying items 
    from a pool using the Hypergeometric Probability Distribution.

    Parameters:
    - total_items (int): The total number of items in the pool.
    - satisfying_items (int): The number of items that satisfy the condition.
    - drawn_items (int): The total number of items drawn.
    - expect_items (int): The minimum number of satisfying items required.

    Returns:
    - float: The probability of drawing at least 'expect_items' satisfying items.
    """
    if satisfying_items > total_items or drawn_items > total_items or expect_items > drawn_items or expect_items > satisfying_items:
        return 0.0  # Invalid case

    # Compute probability of drawing fewer than `expect_items` satisfying items
    prob_fewer_than_expect = sum(
        (comb(satisfying_items, k) * comb(total_items - satisfying_items, drawn_items - k)) / comb(total_items, drawn_items)
        for k in range(expect_items)
    )

    # Probability of drawing at least `expect_items` satisfying items
    probability = 1 - prob_fewer_than_expect

    return round(probability,6)

# Example Usage
if __name__ == "__main__":
    probability = calculate_drawing_probability(total_items=12, satisfying_items=6, expect_items=1, drawn_items=5)
    print(f"Probability of drawing at least 1 satisfying item: {probability:.6f}")
