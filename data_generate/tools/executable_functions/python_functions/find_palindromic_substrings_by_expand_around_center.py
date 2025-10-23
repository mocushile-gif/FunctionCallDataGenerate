def find_palindromic_substrings_by_expand_around_center(s: str, left: int, right: int) -> str:
    """
    Helper function to expand around a center for finding palindromic substrings.

    Parameters:
    - s (str): The input string.
    - left (int): The left index of the center.
    - right (int): The right index of the center.

    Returns:
    - str: The longest palindromic substring found by expanding around the center.
    """
    while left >= 0 and right < len(s) and s[left] == s[right]:
        left -= 1
        right += 1
    
    # Return the palindrome substring found
    return s[left + 1:right]

# Example Usage
if __name__ == "__main__":
    s = "babad"
    left, right = 2, 2
    result = find_palindromic_substrings_by_expand_around_center(s, left, right)
    print(result)  # Output: "bab"
