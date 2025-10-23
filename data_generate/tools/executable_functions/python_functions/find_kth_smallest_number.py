import heapq

def find_kth_smallest_number(nums: list[int], k: int) -> int:
    """
    Finds the kth smallest number in a list.

    Parameters:
    - nums (list[int]): The list of numbers.
    - k (int): The position (1-based index) of the smallest number to find.

    Returns:
    - int: The kth smallest number.
    """
    if not nums or k <= 0 or k > len(nums):
        raise ValueError("Invalid input: ensure 'k' is within the range of the list length.")

    # Use heapq to find the kth smallest element efficiently
    return heapq.nsmallest(k, nums)[-1]

if __name__ == '__main__':
    # Example usage
    print(find_kth_smallest_number([3, 2, 1, 5, 4], 2))  # Output: 2
    print(find_kth_smallest_number([10, 7, 8, 15, 12], 3))  # Output: 10
