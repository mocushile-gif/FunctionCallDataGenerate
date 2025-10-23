def calculate_cell_density(od: float = 1000000000.0, dilution: int = 1000000000, factor: float = 1e9) -> float:
    """
    Calculates the cell density based on the optical density (OD) and dilution factor.

    Parameters:
    - od (float): The optical density of the sample (default is 1e9).
    - dilution (int): The dilution factor applied to the sample (default is 1e9).
    - factor (float): The calibration factor for converting OD to cell density (optional, default is 1e9).

    Returns:
    - float: The calculated cell density.
    """
    # Calculate cell density
    cell_density = od * dilution * factor
    return f"Cell Density: {round(cell_density, 2)} cells/mL"

if __name__ == "__main__":
    # Example usage
    od_value = 0.5  # Example optical density
    dilution_factor = 1000  # Example dilution factor
    calibration_factor = 1e9  # Example calibration factor

    density = calculate_cell_density(od=od_value, dilution=dilution_factor, factor=calibration_factor)
    print(density)
