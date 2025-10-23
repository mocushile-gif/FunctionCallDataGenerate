def find_equilibrium_index(arr: list[int]) -> list[int]:
    """
    Finds all equilibrium indices in a list, where the sum of elements on the left
    is equal to the sum of elements on the right.

    Parameters:
    - arr (List[int]): The input list of integers.

    Returns:
    - List[int]: A list of equilibrium indices. If no equilibrium index exists, returns an empty list.
    """
    total_sum = sum(arr)
    left_sum = 0
    equilibrium_indices = []

    for i, value in enumerate(arr):
        # Calculate the right sum as total_sum - left_sum - value
        right_sum = total_sum - left_sum - value
        if left_sum == right_sum:
            equilibrium_indices.append(i)
        left_sum += value

    if equilibrium_indices:
        return f"Equilibrium indices: {equilibrium_indices}"
    else:
        return "No equilibrium index found."


if __name__ == "__main__":
    # Example usage
    arr = [1, 3, 5, 2, 2]
    result = find_equilibrium_index(arr)
    print(result)
