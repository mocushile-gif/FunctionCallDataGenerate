def calculate_medication_dosage(
    weight_kg: float,
    dose_per_kg: float,
    frequency_per_day: int = 1,
    max_daily_dose: float = None
) -> dict:
    """
    Calculates the daily dosage of a medication based on weight and standard dose per kg.

    Parameters:
    - weight_kg (float): Patient's weight in kilograms.
    - dose_per_kg (float): Standard dose of the medication per kilogram of body weight.
    - frequency_per_day (int): Number of doses per day. Defaults to 1.
    - max_daily_dose (float, optional): Maximum allowable daily dose to prevent overdosing.

    Returns:
    - dict: A dictionary containing the total daily dose and per-dose amount.
    """
    if weight_kg <= 0 or dose_per_kg <= 0 or frequency_per_day <= 0:
        raise ValueError("Weight, dose, and frequency must be positive values.")

    # Calculate total daily dosage
    total_daily_dose = weight_kg * dose_per_kg * frequency_per_day

    # Apply maximum daily dose restriction if provided
    if max_daily_dose and total_daily_dose > max_daily_dose:
        total_daily_dose = max_daily_dose

    # Calculate per-dose amount
    per_dose_amount = total_daily_dose / frequency_per_day

    return {
        "total_daily_dose": round(total_daily_dose, 2),
        "per_dose_amount": round(per_dose_amount, 2),
        "frequency_per_day": frequency_per_day
    }


# 示例调用
if __name__ == "__main__":
    result = calculate_medication_dosage(weight_kg=70, dose_per_kg=0.5, frequency_per_day=3, max_daily_dose=100)
    print(result)
    # 输出：{'total_daily_dose': 100.0, 'per_dose_amount': 33.33, 'frequency_per_day': 3}
