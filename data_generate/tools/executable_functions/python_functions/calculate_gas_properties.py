def calculate_gas_properties(
    pressure: float = None,
    volume: float = None,
    moles: float = 1.0,
    temperature: float = 273.15,
    gas_constant: float = 0.0821
) -> dict:
    """
    Calculates a missing property of an ideal gas using the ideal gas law (PV = nRT).

    Parameters:
    - pressure (float, optional): The pressure of the gas (in atm).
    - volume (float, optional): The volume of the gas (in liters).
    - moles (float): The number of moles of gas. Defaults to 1.0.
    - temperature (float): The temperature of the gas (in Kelvin). Defaults to 273.15 K.
    - gas_constant (float): The gas constant R. Defaults to 0.0821 L·atm/(mol·K).

    Returns:
    - dict: A dictionary containing the calculated property and other inputs.
    """
    if not pressure and not volume:
        raise ValueError("Either pressure or volume must be provided.")

    if pressure is None:
        # Solve for pressure
        pressure = (moles * gas_constant * temperature) / volume
        property_calculated = "pressure"
    elif volume is None:
        # Solve for volume
        volume = (moles * gas_constant * temperature) / pressure
        property_calculated = "volume"
    else:
        raise ValueError("Only one of pressure or volume can be calculated.")

    return {
        "pressure": round(pressure, 2) if pressure else None,
        "volume": round(volume, 2) if volume else None,
        "temperature": temperature,
        "moles": moles,
        "gas_constant": gas_constant,
        "property_calculated": property_calculated
    }


# 示例调用
if __name__ == "__main__":
    result = calculate_gas_properties(volume=10, moles=2, temperature=300)
    print(result)
    # 输出：{'pressure': 4.92, 'volume': 10, 'temperature': 300, 'moles': 2, 'gas_constant': 0.0821, 'property_calculated': 'pressure'}
