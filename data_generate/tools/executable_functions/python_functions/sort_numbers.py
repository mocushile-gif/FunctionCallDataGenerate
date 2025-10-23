from typing import List

def sort_numbers(numbers: List[float], descending: bool = False) -> List[float]:
    """
    Sorts a list of numbers in ascending or descending order.

    Parameters:
    - numbers (List[float]): The list of numbers to be sorted.
    - descending (bool, optional): If True, sorts the numbers in descending order. Defaults to False (ascending).

    Returns:
    - List[float]: The sorted list of numbers.
    """
    return sorted(numbers, reverse=descending)

# Example usage
if __name__ == '__main__':
    print(sort_numbers([5.2, 3.1, 4.6, 2.8]))  # Output: [2.8, 3.1, 4.6, 5.2] (ascending)
    print(sort_numbers([5.2, 3.1, 4.6, 2.8], descending=True))  # Output: [5.2, 4.6, 3.1, 2.8] (descending)
