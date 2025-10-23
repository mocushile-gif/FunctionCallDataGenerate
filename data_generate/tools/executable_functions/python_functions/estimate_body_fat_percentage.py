import math

def estimate_body_fat_percentage(waist_cm: float, neck_cm: float, height_cm: float, sex: str, hip_cm: float = None) -> float:
    """
    Estimates body fat percentage using the US Navy method based on waist, neck, and height measurements.

    Parameters:
    - waist_cm (float): Waist circumference in centimeters.
    - neck_cm (float): Neck circumference in centimeters.
    - height_cm (float): Height in centimeters.
    - sex (str): Biological sex, either 'male' or 'female'.
    - hip_cm (float, optional): Hip circumference in centimeters, required for females.

    Returns:
    - float: Estimated body fat percentage.
    """
    
    if sex.lower() == 'male':
        body_fat_percentage = 86.010 * math.log10(waist_cm - neck_cm) - 70.041 * math.log10(height_cm) + 36.76
        return f"Estimated Body Fat Percentage (Male): {round(body_fat_percentage, 2)}%"
    elif sex.lower() == 'female':
        if hip_cm is None:
            raise ValueError("Hip circumference (hip_cm) is required for females.")
        body_fat_percentage = 163.205 * math.log10(waist_cm + hip_cm - neck_cm) - 97.684 * math.log10(height_cm) - 78.387
        return f"Estimated Body Fat Percentage (Female): {round(body_fat_percentage, 2)}%"
    else:
        raise ValueError("Invalid sex. Please enter 'male' or 'female'.")

if __name__ == "__main__":
    # Example usage for males
    body_fat_male = estimate_body_fat_percentage(waist_cm=85, neck_cm=40, height_cm=175, sex="male")
    print(body_fat_male)
    
    # Example usage for females
    body_fat_female = estimate_body_fat_percentage(waist_cm=63, neck_cm=28, height_cm=173, sex="female", hip_cm=80)
    print(body_fat_female)
