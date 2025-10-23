from typing import List

def split_list(lst: List, chunk_size: int) -> List[List]:
    """
    Splits a list into chunks of a specified size.

    Parameters:
    - lst (List): The input list to be split.
    - chunk_size (int): The size of each chunk.

    Returns:
    - List[List]: A list of chunks, each chunk is a list.

    Raises:
    - ValueError: If chunk_size is less than or equal to 0.
    """
    
    # Handle invalid chunk_size
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0.")
    
    if chunk_size > len(lst):
        # If chunk_size is larger than the list, return the entire list as one chunk
        raise ValueError("The chunk_size is larger than the list size.")

    # Split the list into chunks
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

if __name__ == '__main__':
# Example usage
    try:
        print(split_list([1, 2, 3, 4, 5, 6, 7, 8, 9], 20))  # Output: [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        print(split_list([1, 2, 3, 4, 5], 2))  # Output: [[1, 2, 3, 4, 5]]
        print(split_list([1, 2, 3, 4, 5], 0))  # Error: chunk_size must be greater than 0
    except ValueError as e:
        print(f"Error: {e}")
