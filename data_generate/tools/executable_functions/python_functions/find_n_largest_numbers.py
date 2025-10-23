import heapq

def find_n_largest_numbers(nums: list, n: int) -> list:
    """
    Finds the n largest numbers in a list.

    Parameters:
    - nums (List[int]): The list of numbers.
    - n (int): The number of largest numbers to find.

    Returns:
    - List[int]: A list containing the n largest numbers.
    """
    # Use heapq.nlargest to find the n largest numbers in the list
    return heapq.nlargest(n, nums)


if __name__ == '__main__':
    # Example usage
    nums = [12, 5, 7, 19, 2, 15, 10]
    n = 3
    print(find_n_largest_numbers(nums, n))  # Output: [19, 15, 12]
