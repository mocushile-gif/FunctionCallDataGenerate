def get_angle_of_a_clock(hour: int, minute: int) -> float:
    """
    Calculates the angle between the hour and minute hands of a clock, 
    supporting both 12-hour and 24-hour formats.

    Parameters:
    - hour (int): The hour value.
    - minute (int): The minute value (0-59).

    Returns:
    - float: The angle between the hour and minute hands in degrees.
    """
    # Ensure valid input for hour and minute
    if not (0 <= minute < 60):
        raise ValueError("Minute must be between 0 and 59.")
    
    if hour < 0 or hour > 23:
        raise ValueError("Hour must be between 0 and 23.")

    # Determine if the hour is in 24-hour or 12-hour format
    is_24hr_format = hour >= 12

    # Convert hour to 12-hour format
    hour = hour % 12  # Convert 24-hour time to 12-hour equivalent if necessary

    # Calculate the position of the hour hand
    hour_angle = (hour * 30) + (minute / 60) * 30  # 30 degrees per hour, adjust for minutes
    
    # Calculate the position of the minute hand
    minute_angle = minute * 6  # 6 degrees per minute
    
    # Calculate the angle between the two hands
    angle = abs(hour_angle - minute_angle)
    
    # Return the smaller angle between the two hands
    if angle > 180:
        angle = 360 - angle
    
    hour=hour + 12 if is_24hr_format else hour
    return f"The angle of the clock at {hour}:{minute} is {round(angle, 2)} degrees."


if __name__ == "__main__":
    # Example usage for both formats
    hour = 14  # 2:00 PM in 24-hour format
    minute = 30
    angle = get_angle_of_a_clock(hour, minute)
    print(angle)
