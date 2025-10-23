def calculate_wire_resistance(length_m: float, area_sq_m: float, material: str = "copper") -> float:
    """
    Calculates the resistance of a wire based on its length, cross-sectional area, and material resistivity.

    Parameters:
    - length_m (float): The length of the wire in meters.
    - area_sq_m (float): The cross-sectional area of the wire in square meters.
    - material (str): The material of the wire. Allowed values: "copper" (default) or "aluminum".

    Returns:
    - float: The resistance of the wire in ohms.
    """
    # Resistivity values in ohm meters (Ω·m)
    resistivity_values = {
        "copper": 1.68e-8,  # Ω·m
        "aluminum": 2.82e-8  # Ω·m
    }

    # Validate material input
    if material.lower() not in resistivity_values:
        raise ValueError("Invalid material. Allowed values are 'copper' or 'aluminum'.")

    # Get the resistivity of the specified material
    resistivity = resistivity_values[material.lower()]

    # Calculate resistance using the formula R = ρ * L / A
    resistance = resistivity * length_m / area_sq_m
    return f"Resistance of the wire: {round(resistance, 6)} ohms"

if __name__ == "__main__":
    # Example usage
    length = 10.0  # meters
    area = 1e-6  # square meters
    material = "copper"  # material type

    resistance = calculate_wire_resistance(length, area, material)
    print(resistance)
