def calculate_exercise_target_heart_rate(age: int, intensity_percentage: float) -> float:
    """
    Calculates the target heart rate based on age and the intensity of the exercise.

    Parameters:
    - age (int): Age in years.
    - intensity_percentage (float): The intensity of the exercise, between 50-85%.

    Returns:
    - float: Target heart rate in beats per minute.
    """
    
    # Calculate the maximum heart rate (220 - age)
    max_heart_rate = 220 - age
    
    # Calculate the target heart rate based on the intensity percentage
    target_heart_rate = (max_heart_rate - 60) * (intensity_percentage / 100) + 60
    
    return f"Target Heart Rate: {round(target_heart_rate, 2)} bpm"

if __name__ == "__main__":
    target_hr = calculate_exercise_target_heart_rate(age=25, intensity_percentage=50)
    print(target_hr)
