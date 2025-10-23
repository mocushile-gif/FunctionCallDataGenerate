import math

def compute_circle_properties(radius: float) -> dict:
    """
    Computes the area, circumference, and diameter of a circle given its radius.
    Optionally checks if the radius is a valid positive number.

    Parameters:
    - radius (float): The radius of the circle.

    Returns:
    - dict: A dictionary containing the area, circumference, diameter, and radius.
    """
    # Check for valid radius
    if radius <= 0:
        raise ValueError("Radius must be a positive number.")

    # Calculate area, circumference, and diameter
    area = math.pi * (radius ** 2)  # Area = π * r^2
    circumference = 2 * math.pi * radius  # Circumference = 2 * π * r
    diameter = 2 * radius  # Diameter = 2 * r

    return {
        "radius": radius,
        "diameter": round(diameter, 2),
        "circumference": round(circumference, 2),
        "area": round(area, 2)
    }

# Example usage
if __name__ == "__main__":
    radius = 5.0  # radius
    result = compute_circle_properties(radius)
    print(result)
