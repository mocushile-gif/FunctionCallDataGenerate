def calculate_electric_field(charge: float, distance: float) -> float:
    """
    Calculates the electric field produced by a charge at a certain distance.

    Parameters:
    - charge (float): The charge in coulombs producing the electric field.
    - distance (float): The distance from the charge in meters where the field is being measured.

    Returns:
    - float: The electric field at the given distance.
    """
    
    # Coulomb's constant (k) = 8.9875e9 N·m² / C²
    k = 8.9875e9  # Coulomb's constant
    
    # Calculate electric field using Coulomb's law formula
    electric_field = k * charge / (distance ** 2)
    
    return round(electric_field, 4)

if __name__ == "__main__":
    # Example usage
    charge = 4e+10  # Charge in coulombs
    distance = 2.0  # Distance in meters
    
    field = calculate_electric_field(charge, distance)
    print(f"Electric Field: {field} N/C")
