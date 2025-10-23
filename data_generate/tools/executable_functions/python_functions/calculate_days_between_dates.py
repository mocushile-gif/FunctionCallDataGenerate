from datetime import datetime

def calculate_days_between_dates(start_date: str, end_date: str) -> int:
    """
    Calculates the number of days between two dates.

    Parameters:
    - start_date (str): The start date in 'YYYY-MM-DD' format.
    - end_date (str): The end date in 'YYYY-MM-DD' format.

    Returns:
    - int: The number of days between the two dates.
    """
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        return (end - start).days
    except ValueError:
        raise ValueError("Invalid date format. Please use 'YYYY-MM-DD'.")

if __name__ == "__main__":
    # Example usage
    start_date = "2021-01-01"
    end_date = "2022-01-01"
    days = calculate_days_between_dates(start_date, end_date)
    print(f"Days between dates: {days} days")
