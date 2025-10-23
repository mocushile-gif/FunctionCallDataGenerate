import math
from typing import List

def calculate_cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculates the cosine similarity between two vectors.

    Parameters:
    - vec1 (List[float]): The first vector.
    - vec2 (List[float]): The second vector.

    Returns:
    - float: The cosine similarity between the two vectors.
    """
    if len(vec1) != len(vec2):
        raise ValueError("Vectors must have the same number of dimensions.")
    
    # Calculate the dot product of the vectors
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    
    # Calculate the magnitudes of the vectors
    magnitude_vec1 = math.sqrt(sum(a * a for a in vec1))
    magnitude_vec2 = math.sqrt(sum(b * b for b in vec2))
    
    # Avoid division by zero
    if magnitude_vec1 == 0 or magnitude_vec2 == 0:
        return 0.0
    
    # Calculate the cosine similarity
    similarity = dot_product / (magnitude_vec1 * magnitude_vec2)
    
    return round(similarity, 4)

if __name__ == "__main__":
    vec1 = [1, 2, 3]
    vec2 = [4, 5, 6]
    similarity = calculate_cosine_similarity(vec1, vec2)
    print(f"Cosine similarity: {similarity}")
