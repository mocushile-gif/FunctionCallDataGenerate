import math
from typing import List

def calculate_distance_between_two_points(point1: List[float], point2: List[float], distance_type: str = "euclidean") -> float:
    """
    Calculates the distance between two points in n-dimensional space.

    Parameters:
    - point1 (List[float]): The coordinates of the first point.
    - point2 (List[float]): The coordinates of the second point.
    - distance_type (str): The type of distance to calculate, either 'euclidean' or 'manhattan'.

    Returns:
    - float: The calculated distance between the two points.
    """
    if len(point1) != len(point2):
        raise ValueError("Points must have the same number of dimensions.")
    
    if distance_type.lower() == "manhattan":
        # Manhattan Distance: Sum of absolute differences
        distance = sum(abs(p1 - p2) for p1, p2 in zip(point1, point2))
    elif distance_type.lower() == "euclidean":
        # Euclidean Distance: Square root of sum of squared differences
        distance = math.sqrt(sum((p1 - p2) ** 2 for p1, p2 in zip(point1, point2)))
    else:
        raise ValueError("Invalid distance type. Please choose 'euclidean' or 'manhattan'.")
    
    return round(distance, 4)

if __name__ == "__main__":
    point1 = [1, 2, 3]
    point2 = [4, 5, 6]
    
    manhattan_distance = calculate_distance_between_two_points(point1, point2, "manhattan")
    euclidean_distance = calculate_distance_between_two_points(point1, point2, "euclidean")
    
    print(f"Manhattan Distance: {manhattan_distance}")
    print(f"Euclidean Distance: {euclidean_distance}")
