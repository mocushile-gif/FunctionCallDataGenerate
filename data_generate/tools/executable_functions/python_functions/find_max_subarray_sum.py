import time
from typing import List, Tuple

def find_max_subarray_sum(nums: List[float], method: str = 'kadane') -> Tuple[int, List[int], float]:
    """
    Finds the maximum sum of a contiguous subarray within a list of integers using different methods,
    and returns the subarray corresponding to that maximum sum along with the execution time.
    
    Parameters:
    - nums (List[int]): The input list of integers.
    - method (str): The method to use ('kadane', 'brute_force', or 'divide_conquer').
    
    Returns:
    - Tuple[int, List[int], float]: A tuple where the first element is the maximum sum,
      the second element is the subarray corresponding to that sum, and the third element is the time taken in seconds.
    """
    
    if not nums:
        return 0, [], 0.0

    start_time = time.time()  # Start timing the execution

    # Method 1: Kadane's Algorithm (O(n))
    if method == 'kadane':
        max_sum = nums[0]
        current_sum = nums[0]
        start = 0  # Track the start index of the subarray
        end = 0    # Track the end index of the subarray
        temp_start = 0  # Temporary start index for a new subarray
        
        for i in range(1, len(nums)):
            if nums[i] > current_sum + nums[i]:
                current_sum = nums[i]
                temp_start = i  # New subarray starts here
            else:
                current_sum += nums[i]
            
            if current_sum > max_sum:
                max_sum = current_sum
                start = temp_start
                end = i
        
        end_time = time.time()  # End timing the execution
        return max_sum, nums[start:end+1], end_time - start_time

    # Method 2: Brute Force Approach (O(n²)) - Iterate over all possible subarrays
    elif method == 'brute_force':
        n = len(nums)
        max_sum = nums[0]
        subarray = [nums[0]]
        
        for i in range(n):
            current_sum = 0
            for j in range(i, n):
                current_sum += nums[j]
                if current_sum > max_sum:
                    max_sum = current_sum
                    subarray = nums[i:j+1]
        
        end_time = time.time()  # End timing the execution
        return max_sum, subarray, end_time - start_time

    # Method 3: Divide and Conquer (O(n log n)) - Divide the array and calculate max subarray sum recursively
    elif method == 'divide_conquer':
        def divide_and_conquer(arr, left, right):
            if left == right:
                return arr[left], [arr[left]]
            
            mid = (left + right) // 2
            left_max, left_subarray = divide_and_conquer(arr, left, mid)
            right_max, right_subarray = divide_and_conquer(arr, mid + 1, right)
            
            # Find max crossing subarray
            left_cross_sum = float('-inf')
            right_cross_sum = float('-inf')
            temp_sum = 0
            left_cross_subarray = []
            for i in range(mid, left - 1, -1):
                temp_sum += arr[i]
                if temp_sum > left_cross_sum:
                    left_cross_sum = temp_sum
                    left_cross_subarray = arr[i:mid+1]
            
            temp_sum = 0
            right_cross_subarray = []
            for i in range(mid + 1, right + 1):
                temp_sum += arr[i]
                if temp_sum > right_cross_sum:
                    right_cross_sum = temp_sum
                    right_cross_subarray = arr[mid+1:i+1]
            
            cross_sum = left_cross_sum + right_cross_sum
            if left_max >= right_max and left_max >= cross_sum:
                return left_max, left_subarray
            elif right_max >= left_max and right_max >= cross_sum:
                return right_max, right_subarray
            else:
                return cross_sum, left_cross_subarray + right_cross_subarray
        
        max_sum, subarray = divide_and_conquer(nums, 0, len(nums) - 1)
        end_time = time.time()  # End timing the execution
        return max_sum, subarray, end_time - start_time

# Example usage:
if __name__ == "__main__":
    nums = [-2, 1, -3, 4, -1, 2, 1.5, -5, 4]
    
    result_kadane = find_max_subarray_sum(nums, method='kadane')
    result_brute_force = find_max_subarray_sum(nums, method='brute_force')
    result_divide_conquer = find_max_subarray_sum(nums, method='divide_conquer')
    
    print(f"Kadane's method: Sum = {result_kadane[0]}, Subarray = {result_kadane[1]}, Time = {result_kadane[2]:.6f} seconds")
    print(f"Brute force method: Sum = {result_brute_force[0]}, Subarray = {result_brute_force[1]}, Time = {result_brute_force[2]:.6f} seconds")
    print(f"Divide and conquer method: Sum = {result_divide_conquer[0]}, Subarray = {result_divide_conquer[1]}, Time = {result_divide_conquer[2]:.6f} seconds")
