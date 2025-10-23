from typing import List, Tuple

def polygon_area_shoelace(vertices: List[Tuple[float, float]]) -> float:
    """
    Calculates the area of a polygon using the Shoelace formula (Gauss's area formula).
    
    Parameters:
    - vertices (List[Tuple[float, float]]): A list of vertices of the polygon where each vertex is represented as a tuple (x, y).
    
    Returns:
    - float: The area of the polygon.
    """
    n = len(vertices)
    
    if n < 3:
        raise ValueError("A polygon must have at least 3 vertices.")
    
    area = 0.0
    for i in range(n):
        j = (i + 1) % n  # next vertex, wrapping around to the first vertex
        x_i, y_i = vertices[i]
        x_j, y_j = vertices[j]
        area += x_i * y_j - y_i * x_j
    
    return abs(area) / 2.0

# Example usage:
if __name__ == "__main__":
    # Example polygon vertices (a square)
    vertices = [[0, 0], [4, 0], [4, 4], [0, 4]]
    area = polygon_area_shoelace(vertices)
    print(f"Area of the polygon: {area}")
