def calculate_photoelectric_effect_energy(frequency: float, work_function: float) -> float:
    """
    Calculates the kinetic energy of an ejected electron in the photoelectric effect.

    Parameters:
    - frequency (float): The frequency of the incident light (Hz).
    - work_function (float): The work function of the material (eV).

    Returns:
    - float: The kinetic energy of the ejected electron (eV).
    """
    h = 6.62607015e-34  # Planck's constant in J·s
    c = 3.0e8  # Speed of light in m/s
    e = 1.60218e-19  # Electron charge in Coulombs

    # Energy of the photon
    photon_energy = (h * frequency) / e  # Convert from Joules to eV

    # Kinetic energy of the electron
    kinetic_energy = photon_energy - work_function
    return round(kinetic_energy, 2)

if __name__ == '__main__':
    # Example usage
    frequency = 5.0e14  # Frequency of light in Hz
    work_function = 2.0  # Work function in eV
    energy = calculate_photoelectric_effect_energy(frequency, work_function)
    print(f"Kinetic Energy of Ejected Electron: {energy} eV")
