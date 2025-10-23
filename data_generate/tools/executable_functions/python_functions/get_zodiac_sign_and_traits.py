from datetime import datetime

def get_zodiac_sign_and_traits(birthdate: str) -> dict:
    """
    Returns the zodiac sign and associated traits based on the birthdate.
    
    Parameters:
    - birthdate (str): The birthdate in 'YYYY-MM-DD' format.

    Returns:
    - dict: A dictionary containing the zodiac sign and its associated personality traits.
    """
    try:
        birth_date = datetime.strptime(birthdate, "%Y-%m-%d")
        month = birth_date.month
        day = birth_date.day
        sign = ""
        traits = ""
        
        # Checking for cusp dates if the parameter is set to True
        cusp_margin = 2  # days considered to be on the cusp

        if (month == 3 and day >= 21) or (month == 4 and day <= 19):
            sign = "Aries"
            traits = "Energetic, adventurous, and a natural leader."
        elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
            sign = "Taurus"
            traits = "Reliable, practical, and determined."
        elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
            sign = "Gemini"
            traits = "Adaptable, curious, and sociable."
        elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
            sign = "Cancer"
            traits = "Emotional, nurturing, and protective."
        elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
            sign = "Leo"
            traits = "Confident, passionate, and charismatic."
        elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
            sign = "Virgo"
            traits = "Analytical, detail-oriented, and helpful."
        elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
            sign = "Libra"
            traits = "Diplomatic, charming, and fair-minded."
        elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
            sign = "Scorpio"
            traits = "Intense, secretive, and passionate."
        elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
            sign = "Sagittarius"
            traits = "Optimistic, independent, and adventurous."
        elif (month == 12 and day >= 22) or (month == 1 and day <= 19):
            sign = "Capricorn"
            traits = "Disciplined, responsible, and ambitious."
        elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
            sign = "Aquarius"
            traits = "Innovative, independent, and humanitarian."
        else:
            sign = "Pisces"
            traits = "Empathetic, artistic, and compassionate."

        return {"sign": sign, "traits": traits}
    
    except ValueError:
        raise ValueError("Invalid date format. Please use 'YYYY-MM-DD'.")

if __name__ == "__main__":
    # Example usage
    birthdate = "2000-01-22"
    result = get_zodiac_sign_and_traits(birthdate)
    print(f"Zodiac Sign: {result['sign']}")
    print(f"Traits: {result['traits']}")
