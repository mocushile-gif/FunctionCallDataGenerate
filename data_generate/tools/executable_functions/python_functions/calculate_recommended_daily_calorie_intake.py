def calculate_recommended_daily_calorie_intake(weight_kg: float, height_cm: float, age: int, sex: str, 
                             activity_level: int, goal: str):
    """
    Calculates the recommended daily calorie intake and macronutrient distribution based on personal characteristics and goals.

    Parameters:
    - weight_kg (float): Body weight in kilograms.
    - height_cm (float): Height in centimeters.
    - age (int): Age in years.
    - sex (str): Biological sex, either 'male' or 'female'.
    - activity_level (int): Activity level on a scale of 1 to 5 (1 = sedentary, 5 = extremely active).
    - goal (str): Fitness goal, either 'lose', 'maintain', or 'gain'.

    Returns:
    - dict: Daily calorie intake and macronutrient distribution.
    """
    
    # Harris-Benedict BMR equation
    if sex.lower() == 'male':
        bmr = 66.5 + (13.75 * weight_kg) + (5.003 * height_cm) - (6.75 * age)
    elif sex.lower() == 'female':
        bmr =  655.1 + (9.563 * weight_kg) + (1.850 * height_cm) - (4.676 * age)
    else:
        raise ValueError("Invalid sex. Please enter 'male' or 'female'.")
    
    # Adjusting for activity level (using a multiplier for each level)
    activity_multipliers = {1: 1.2, 2: 1.375, 3: 1.55, 4: 1.725, 5: 1.9}
    bmr = bmr * activity_multipliers.get(activity_level, 1)
    
    # Adjusting for fitness goal (gain, lose, maintain)
    if goal == 'lose':
        calorie_intake = bmr - 500  # Deficit for weight loss (approx.)
    elif goal == 'maintain':
        calorie_intake = bmr
    elif goal == 'gain':
        calorie_intake = bmr + 500  # Surplus for weight gain (approx.)
    else:
        raise ValueError("Invalid goal. Please enter 'lose', 'maintain', or 'gain'.")
    
    # Macronutrient distribution (assumes 40% carbs, 30% protein, 30% fat)
    carbs = (calorie_intake * 0.4) / 4  # 4 calories per gram of carbs
    protein = (calorie_intake * 0.3) / 4  # 4 calories per gram of protein
    fat = (calorie_intake * 0.3) / 9  # 9 calories per gram of fat

    return {
        "calories": round(calorie_intake, 2),
        "carbs_grams": round(carbs, 2),
        "protein_grams": round(protein, 2),
        "fat_grams": round(fat, 2)
    }

if __name__ == "__main__":
    # Example usage
    intake = calculate_recommended_daily_calorie_intake(weight_kg=54, height_cm=173, age=25, sex="female", 
                                       activity_level=3, goal="maintain")
    print(intake)
