def binary_search(arr: list, target: float) -> int:
    """
    Performs binary search on a sorted list to find the index of a target value.

    Parameters:
    - arr (list): An ascending sorted list of integers.
    - target (int): The target value to search for.

    Returns:
    - int: The index of the target value in the list, or -1 if not found.
    """
    left, right = 0, len(arr) - 1

    while left <= right:
        mid = (left + right) // 2

        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1  # Target not found

# Example usage:
if __name__ == "__main__":
    arr = [1, 3, 5, 7, 9, 11, 13]
    arr = [2800, 2600, 1400, 1400, 1200, 1200, 1000, 860, 800, 800, 800, 800, 700, 600, 550, 500, 500, 500, 500, 500, 500, 500, 500, 440, 400, 400, 400, 400, 400, 400, 399, 368, 350, 350, 325, 308, 300, 300, 300, 300, 300, 280, 280, 280, 270, 268, 250, 240, 230, 200, 200, 200, 200, 200, 200, 200, 195, 180, 175, 170, 166, 160, 150, 120]
    print(arr.sort())
    target = 800
    result = binary_search(arr, target)
    print(result)
