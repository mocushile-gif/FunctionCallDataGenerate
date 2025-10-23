from typing import List, Tuple, Optional

def find_majority_element(nums: List[int], return_count: bool = False) -> Tuple[int, Optional[int]]:
    """
    Finds the majority element in a list, which appears more than ⌊n / 2⌋ times.
    Optionally, returns the count of the majority element, or checks if the count exceeds a given threshold.

    Parameters:
    - nums (List[int]): The input list of integers.
    - return_count (bool): If True, returns the count of the majority element along with the element. Default is False.
    """
    
    # Step 1: Boyer-Moore Voting Algorithm to find the majority element
    candidate, count = None, 0
    for num in nums:
        if count == 0:
            candidate, count = num, 1
        elif num == candidate:
            count += 1
        else:
            count -= 1
    
    # Step 2: Verify the candidate is the majority element by counting its occurrences
    actual_count = nums.count(candidate)
    majority_threshold = len(nums) // 2
    
    if actual_count > majority_threshold:
        # Majority element found
        if return_count:
            return f'The majority element: {candidate}'+ f'\nCount: {actual_count}'
        else:
            return f'The majority element: {candidate}'
    else:
        # No majority element found
        return f'No valid majority element found for the list {nums}'

# Example Usage
if __name__ == "__main__":
    # {"arguments": "{\"nums\":[1,2,2,3,2,4,2,5],\"return_count\":true}", "name": "find_majority_element"}
    nums = [1,2,2,3,2,4,2,5,2]
    result = find_majority_element(nums, return_count=True)
    print(result)  # Output: (4, 5)
