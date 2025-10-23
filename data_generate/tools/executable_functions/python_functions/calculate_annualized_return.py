def calculate_annualized_return(beginning_value: float, ending_value: float, years: int) -> float:
    """
    Calculates the annualized return (AR) over a given number of years.

    Parameters:
    - beginning_value (float): The value at the beginning of the period.
    - ending_value (float): The value at the end of the period.
    - years (int): The number of years.

    Returns:
    - float: The annualized return.
    """
    return round(((ending_value / beginning_value) ** (1 / years) - 1) * 100, 2)

if __name__ == "__main__":
    # Example usage
    beginning_value = 1000
    ending_value = 1500
    years = 5
    ar = calculate_annualized_return(beginning_value, ending_value, years)
    print(f"Annualized Return: {ar}%")
