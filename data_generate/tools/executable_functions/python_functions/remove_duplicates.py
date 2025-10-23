from typing import List, Callable, Optional, Union

def remove_duplicates(
    lst: List[Union[int, str, float]], 
    key: Optional[Callable[[Union[int, str, float]], Union[int, str]]] = None,
    case_sensitive: bool = True
) -> List[Union[int, str, float]]:
    """
    Removes duplicate elements from a list while preserving the order. You can also specify a custom key function to determine
    whether two elements are considered duplicates, and control case sensitivity for string values.

    Parameters:
    - lst (List): The input list, which can contain integers, strings, floats, etc.
    - key (Callable, optional): A custom function to determine if two elements are duplicates.
      If not provided, the function uses the element itself.
    - case_sensitive (bool, optional): If True, string comparisons are case-sensitive. Defaults to True.

    Returns:
    - List: A new list with duplicates removed and order preserved.
    """
    seen = set()  # Set to track seen elements
    result = []   # List to store the result

    def normalize(item):
        """Normalize the item based on the case sensitivity."""
        if isinstance(item, str) and not case_sensitive:
            return item.lower()
        return item

    for item in lst:
        normalized_item = normalize(item)
        comparison_key = key(normalized_item) if key else normalized_item
        
        if comparison_key not in seen:
            result.append(item)
            seen.add(comparison_key)
    
    return result

# Example Usage
if __name__ == "__main__":
    input_list = ['apple', 'banana', 'Apple', 'banana', 1, 2, 2, 3, 4, 5, 1]
    
    # Case-insensitive removal of duplicates
    print(remove_duplicates(input_list, case_sensitive=False))
    
    # Removing duplicates based on custom key (e.g., based on length of string)
    print(remove_duplicates(input_list, key=lambda x: len(str(x))))
