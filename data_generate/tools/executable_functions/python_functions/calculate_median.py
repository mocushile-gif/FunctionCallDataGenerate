from typing import List, Union

def calculate_median(numbers: List[Union[int, float]]) -> float:
    """
    Calculates the median of a list of numbers.

    Parameters:
    - numbers (List[Union[int, float]]): A list of numbers (either integers or floats).

    Returns:
    - float: The median of the numbers.
    """
    
    # First, sort the numbers
    numbers_sorted = sorted(numbers)
    
    # Find the number of elements in the list
    n = len(numbers_sorted)
    
    # If the list is empty, return None
    if n == 0:
        return None
    
    # If the list has an odd number of elements, the median is the middle element
    if n % 2 == 1:
        median = numbers_sorted[n // 2]
    # If the list has an even number of elements, the median is the average of the two middle elements
    else:
        median = (numbers_sorted[n // 2 - 1] + numbers_sorted[n // 2]) / 2
    
    return round(median, 2)

if __name__ == "__main__":
    # Example usage
    numbers = [10, 20, 30, 40, 50]
    median = calculate_median(numbers)
    print(f"The median is: {median}")
