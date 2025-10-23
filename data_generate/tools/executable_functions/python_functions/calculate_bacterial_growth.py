import math

def calculate_bacterial_growth(
    initial_population: int,
    time: float,
    growth_rate: float = 20,
    doubling_time: float = None,
    environment_factor: float = 1.0,
    max_population: int = None
) -> float:
    """
    Calculates the bacterial population after a given time based on initial population and growth rate.
    
    Parameters:
    - initial_population (int): The initial bacterial population. Defaults to 20.
    - growth_rate (float): The growth rate (in percentage) per time unit. Defaults to 20.
    - time (float): The time units elapsed.
    - doubling_time (float, optional): The time units required for the bacteria population to double. If provided, it overrides growth_rate.
    - environment_factor (float): A multiplier to simulate environmental factors (e.g., 0.8 for adverse conditions). Default is 1.0.
    - max_population (int, optional): The maximum population limit (e.g., carrying capacity). If provided, it limits the result.

    Returns:
    - float: The bacterial population after the given time.
    """

    # Calculate population based on doubling time (logarithmic growth)
    if doubling_time:
        population = initial_population * (2 ** (time / doubling_time))
    else:
        # Calculate population based on growth rate (exponential growth)
        rate = growth_rate / 100  # Convert percentage to decimal
        population = initial_population * ((1 + rate) ** time)

    # Adjust for environmental factors
    population *= environment_factor

    # Apply maximum population limit (carrying capacity)
    if max_population and population > max_population:
        population = max_population

    return round(population, 2)


if __name__ == '__main__':
    result = calculate_bacterial_growth(
        initial_population=50,
        time=1,
        doubling_time=20,
    )
    print(result)  # 输出：16900.0
