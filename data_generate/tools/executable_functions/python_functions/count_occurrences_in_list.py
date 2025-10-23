from collections import Counter
from typing import List, Dict

def count_occurrences_in_list(lst: List) -> Dict:
    """
    Counts the occurrences of each element in a list and returns a dictionary with the counts.

    Parameters:
    - lst (List): The input list.

    Returns:
    - dict: A dictionary where keys are the elements from the list, and values are their corresponding counts.
    """
    # Using Counter from collections module to count the occurrences efficiently
    counts = Counter(lst)
    
    return dict(counts)

# Example usage
if __name__ == "__main__":
    sample_list = ['a', 2, 2, 3, 3, 3, 4, 5, 5]
    result = count_occurrences_in_list(sample_list)
    print(result)
