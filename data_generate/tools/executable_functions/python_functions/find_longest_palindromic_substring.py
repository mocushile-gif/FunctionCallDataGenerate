def find_longest_palindromic_substring(s: str) -> str:
    """
    Finds the longest palindromic substring in a string.

    Parameters:
    - s (str): The input string.

    Returns:
    - str: The longest palindromic substring.
    """
    def expand_around_center(left: int, right: int) -> str:
        while left >= 0 and right < len(s) and s[left] == s[right]:
            left -= 1
            right += 1
        return s[left+1:right]

    if not s:
        return ""
    
    longest_palindrome = ""
    
    for i in range(len(s)):
        # Odd length palindromes (expand around single character)
        odd_palindrome = expand_around_center(i, i)
        if len(odd_palindrome) > len(longest_palindrome):
            longest_palindrome = odd_palindrome
        
        # Even length palindromes (expand around pair of characters)
        even_palindrome = expand_around_center(i, i+1)
        if len(even_palindrome) > len(longest_palindrome):
            longest_palindrome = even_palindrome
    
    return longest_palindrome

# Example usage
if __name__ == '__main__':
    print(find_longest_palindromic_substring("babad"))  # Output: "bab" or "aba"
    print(find_longest_palindromic_substring("cbbd"))   # Output: "bb"
