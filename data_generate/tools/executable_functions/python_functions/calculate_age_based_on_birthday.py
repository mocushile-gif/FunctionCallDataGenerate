from datetime import datetime

def calculate_age_based_on_birthday(birthdate: str) -> int:
    """
    Calculates the age based on the birthdate.

    Parameters:
    - birthdate (str): The birthdate in the format 'YYYY-MM-DD'.

    Returns:
    - int: The age in years.
    """
    try:
        birth_date = datetime.strptime(birthdate, "%Y-%m-%d")
        today = datetime.today()
        # Calculate age by year difference and adjust if birthday hasn't occurred this year
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age
    except ValueError:
        raise ValueError("Invalid date format. Please use 'YYYY-MM-DD'.")

if __name__ == "__main__":
    # Example usage
    birthdate = "1990-06-15"
    age = calculate_age_based_on_birthday(birthdate)
    print(f"Age: {age} years")
