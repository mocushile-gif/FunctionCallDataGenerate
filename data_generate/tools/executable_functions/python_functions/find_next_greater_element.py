def find_next_greater_element(nums: list) -> list:
    """
    Finds the next greater element for each element in the list.

    Parameters:
    - nums (List[int]): The list of numbers.

    Returns:
    - List[int]: A list where each element is replaced with the next greater element
                 from the original list. If no greater element exists, -1 is placed.
    """
    # Stack to keep track of the elements and their indices
    stack = []
    result = [-1] * len(nums)  # Initialize the result list with -1 for each element

    for i, num in enumerate(nums):
        # Pop elements from the stack while the current number is greater than
        # the element at the index stored in the stack.
        while stack and nums[stack[-1]] < num:
            idx = stack.pop()
            result[idx] = num  # Update the result with the next greater element
        
        # Push the current index onto the stack
        stack.append(i)

    return result

if __name__ == '__main__':
    # Example usage
    nums = [4, 5, 2, 10, 8]
    print(find_next_greater_element(nums))  # Output: [5, 10, 10, -1, -1]
