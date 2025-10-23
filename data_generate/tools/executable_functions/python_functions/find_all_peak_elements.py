def find_all_peak_elements(nums: list) -> list:
    """
    Finds all peak elements in a list of integers.

    Parameters:
    - nums (List[int]): The list of integers.

    Returns:
    - List[int]: A list containing all peak elements.
    """
    peaks = []
    n = len(nums)

    # Check the first element
    if n > 1 and nums[0] >= nums[1]:
        peaks.append(nums[0])

    # Check the last element
    if n > 1 and nums[-1] >= nums[-2]:
        peaks.append(nums[-1])

    # Check the middle elements
    for i in range(1, n - 1):
        if nums[i] >= nums[i - 1] and nums[i] >= nums[i + 1]:
            peaks.append(nums[i])

    return peaks


# Example usage
if __name__ == '__main__':
    nums = [1, 3, 20, 4, 23, 0]
    print(find_all_peak_elements(nums))  # Output: [20]
