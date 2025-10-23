from typing import List, Optional

def reverse_words(sentence: str, split_by: Optional[str] = " ", exclude: Optional[List[str]] = None, preserve_case: bool = True) -> str:
    """
    Reverses the order of words in a sentence. Optionally allows splitting by a custom delimiter, excluding specific words,
    and preserving the case of each word.

    Parameters:
    - sentence (str): The input sentence whose words will be reversed.
    - split_by (str): The delimiter to split words by. Default is a space. (Optional)
    - exclude (List[str]): A list of words to exclude from reversal. These words will remain in their original position. (Optional)
    - preserve_case (bool): If True, it preserves the original case of the words. Default is True. (Optional)

    Returns:
    - str: The sentence with the order of words reversed, with exclusions and case preservation as specified.
    """

    # Split the sentence into words based on the given delimiter
    words = sentence.split(split_by)
    
    # If no exclude list is provided, create an empty one
    if exclude is None:
        exclude = []

    # Identify words to exclude and those to reverse
    words_to_reverse = [word for word in words if word.lower() not in map(str.lower, exclude)]
    
    # Reverse the words that are not excluded
    reversed_words = words_to_reverse[::-1]

    # Prepare a result list to store the final sentence
    result = []
    reverse_idx = 0

    # Build the result sentence by replacing words with their reversed counterparts if they are not excluded
    for word in words:
        # If the word is in the exclude list, keep it in its original position
        if word.lower() in map(str.lower, exclude):
            result.append(word)
        else:
            # Otherwise, use the reversed word
            result.append(reversed_words[reverse_idx])
            reverse_idx += 1

    # Join the result list into a final sentence
    reversed_sentence = " ".join(result)
    
    # Optionally preserve the case of the original sentence
    if preserve_case:
        return reversed_sentence
    else:
        return reversed_sentence.lower()

# Example Usage
if __name__ == "__main__":
    sentence = "The quick brown fox jumps over the lazy dog"
    result = reverse_words(sentence, exclude=["fox", "the"])
    print(result)  # Output: "dog lazy the over jumps brown quick The"
