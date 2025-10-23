def assess_diabetes_risk(weight_lbs, height_inches, activity):
    """
    Assesses the risk of developing type 2 diabetes based on BMI and physical activity level.

    Parameters:
    - weight_lbs (int): Body weight in pounds.
    - height_inches (int): Height in inches.
    - activity (str): Physical activity level. Allowed values: "sedentary", "lightly active",
                      "moderately active", "very active".

    Returns:
    - str: The risk level ("Low risk", "Moderate risk", "High risk") with a brief explanation.
    """
    # Validate activity input
    allowed_activities = ["sedentary", "lightly active", "moderately active", "very active"]
    if activity not in allowed_activities:
        return "Error: Invalid activity level. Choose from: 'sedentary', 'lightly active', 'moderately active', 'very active'."

    # Calculate BMI
    try:
        bmi = (weight_lbs * 703) / (height_inches ** 2)
    except ZeroDivisionError:
        return "Error: Height cannot be zero."

    # Determine BMI category
    if bmi < 18.5:
        bmi_category = "underweight"
    elif 18.5 <= bmi < 24.9:
        bmi_category = "normal weight"
    elif 25 <= bmi < 29.9:
        bmi_category = "overweight"
    else:
        bmi_category = "obese"

    # Adjust risk based on activity level
    if activity == "sedentary":
        if bmi_category in ["overweight", "obese"]:
            risk = "High risk"
        elif bmi_category == "normal weight":
            risk = "Moderate risk"
        else:
            risk = "Low risk"
    elif activity == "lightly active":
        if bmi_category == "obese":
            risk = "High risk"
        elif bmi_category == "overweight":
            risk = "Moderate risk"
        else:
            risk = "Low risk"
    elif activity == "moderately active":
        if bmi_category == "obese":
            risk = "Moderate risk"
        else:
            risk = "Low risk"
    elif activity == "very active":
        risk = "Low risk"

    # Create a detailed explanation
    explanation = (
        f"Your BMI is {bmi:.1f}, which falls into the '{bmi_category}' category. "
        f"Given your activity level ('{activity}'), your diabetes risk is assessed as: {risk}."
    )
    return explanation

if __name__ == '__main__':
    # Example usage
    result = assess_diabetes_risk(weight_lbs=54, height_inches=173, activity="sedentary")
    print(result)

