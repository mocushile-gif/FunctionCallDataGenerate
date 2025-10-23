def calculate_gpa(scores: list, credits: list) -> float:
    """
    Calculates the weighted average grade (GPA) based on scores and their corresponding credit hours.

    Parameters:
    - scores (list): A list of scores (float or int).
    - credits (list): A list of credit hours corresponding to each score (float).

    Returns:
    - float: The weighted average GPA.
    """
    
    # Error handling: check if lengths of scores and credits match
    if len(scores) != len(credits):
        raise ValueError("The number of scores must be equal to the number of credit hours.")
    
    # Calculating the weighted sum (score * credit for each course)
    weighted_sum = sum(score * credit for score, credit in zip(scores, credits))
    
    # Calculating the total credit hours
    total_credits = sum(credits)
    
    # If total credits are 0, return 0 (or raise an error depending on your use case)
    if total_credits == 0:
        return 0.0
    
    # GPA is the weighted sum divided by total credits
    gpa = weighted_sum / total_credits
    return round(gpa, 2)

if __name__ == "__main__":
    # Example usage
    scores = [90, 85, 88, 92]
    credits = [3, 4, 3, 2]
    
    gpa = calculate_gpa(scores, credits)
    print(f"The calculated GPA is: {gpa}")
