def is_valid_parentheses(s: str) -> bool:
    """
    Checks if a string contains valid parentheses.

    Parameters:
    - s (str): The input string containing parentheses.

    Returns:
    - bool: True if the parentheses are valid, False otherwise.
    """
    stack = []
    # Map of valid pairs
    parentheses_map = {')': '(', '}': '{', ']': '['}

    for char in s:
        if char in parentheses_map.values():  # Opening parentheses
            stack.append(char)
        elif char in parentheses_map.keys():  # Closing parentheses
            # Check if stack is not empty and top of stack matches the opening parentheses
            if stack and stack[-1] == parentheses_map[char]:
                stack.pop()
            else:
                return False
    
    # If stack is empty, all parentheses are matched
    return len(stack) == 0

# Example usage
if __name__ == '__main__':
    print(is_valid_parentheses("()"))  # True
    print(is_valid_parentheses("()[]{}"))  # True
    print(is_valid_parentheses("(]"))  # False
    print(is_valid_parentheses("([)]"))  # False
    print(is_valid_parentheses("{[]}"))  # True
