def flatten_list(nested_list: list) -> list:
    """
    Flattens a nested list into a single-level list.

    Parameters:
    - nested_list (list): The nested list to be flattened.

    Returns:
    - list: A single-level list with all elements from the nested list.
    """
    flattened = []
    
    for item in nested_list:
        if isinstance(item, list):
            flattened.extend(flatten_list(item))  # Recursively flatten nested lists
        else:
            flattened.append(item)  # Add non-list items directly
    
    return flattened

if __name__ == "__main__":
    # Example usage
    nested_list = [1, [2, 3], [4, [5, 6]], 7]
    flattened = flatten_list(nested_list)
    print(flattened)  # Output: [1, 2, 3, 4, 5, 6, 7]
