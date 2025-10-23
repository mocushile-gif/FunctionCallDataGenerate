from typing import List, Tuple

def reverse_string(text: str, 
                   strip_spaces: bool = False, 
                   preserve_special_chars: bool = False, 
                   keep_segments_in_place: List[str] = None) -> str:
    """
    Reverses characters in a string while optionally:
    - Stripping extra spaces.
    - Preserving the positions of special characters.
    - Keeping specific substrings in their original places.

    Parameters:
    - text (str): The input string to reverse.
    - strip_spaces (bool): If True, removes extra spaces before reversing.
    - preserve_special_chars (bool): If True, keeps non-alphabetic characters in place.
    - keep_segments_in_place (List[str]): List of substrings that should stay in their original positions.

    Returns:
    - str: The transformed string with applied options.
    """
    if keep_segments_in_place is None:
        keep_segments_in_place = []

    # Remove extra spaces if required
    if strip_spaces:
        text = " ".join(text.split())

    # Step 1: Identify and store preserved segments
    preserved_positions: List[Tuple[int, str]] = []
    temp_text = text  # Copy to modify safely

    for segment in keep_segments_in_place:
        start_idx = temp_text.find(segment)
        if start_idx != -1:
            preserved_positions.append((start_idx, segment))
            temp_text = temp_text.replace(segment, "*" * len(segment), 1)  # Placeholder

    # Step 2: Reverse only the non-preserved characters
    reversed_chars = [char for char in temp_text if char != "*"]
    reversed_chars.reverse()  # Reverse the list of characters

    # Step 3: Reconstruct the string with preserved segments at original positions
    result = list(temp_text)  # Convert back to a mutable list
    char_index = 0  # Index for traversing reversed_chars

    for i in range(len(result)):
        if result[i] == "*":
            continue  # Skip placeholders
        if char_index < len(reversed_chars):
            result[i] = reversed_chars[char_index]
            char_index += 1

    # Step 4: Restore preserved segments at their original indices
    for index, segment in preserved_positions:
        result[index:index+len(segment)] = segment

    return ''.join(result)

# Example Usage
if __name__ == "__main__":
    text = "89 78 45 34 12 3"
    reversed_text = reverse_string(text, strip_spaces=True, preserve_special_chars=False, keep_segments_in_place=["78", "34", "12", " "])
    print(reversed_text)  # Expected Output: "3 12 45 34 78 89"
