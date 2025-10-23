import itertools

def calculate_dice_roll_probability(target_sum: int, num_dice: int, num_faces: int = 6) -> float:
    """
    Calculates the probability of rolling a specific sum with a given number of dice, each having a certain number of faces.

    Parameters:
    - target_sum (int): The target sum to calculate the probability for.
    - num_dice (int): The number of dice being rolled.
    - num_faces (int): The number of faces on each die (default is 6).

    Returns:
    - float: The probability of rolling the target sum.
    """
    if target_sum < num_dice or target_sum > num_dice * num_faces:
        raise ValueError(f"Target sum {target_sum} is out of the achievable range for {num_dice} dice.")
    
    # Generate all possible combinations of dice rolls
    all_rolls = list(itertools.product(range(1, num_faces + 1), repeat=num_dice))
    
    # Count the number of ways to get the target sum
    successful_rolls = [roll for roll in all_rolls if sum(roll) == target_sum]
    
    # Calculate the probability
    probability = len(successful_rolls) / len(all_rolls)
    
    return f"The probability of rolling a sum of {target_sum} with {num_dice} dice is {round(probability, 6)}."

# Example usage
if __name__ == "__main__":
    target_sum = 10
    num_dice = 2
    probability = calculate_dice_roll_probability(target_sum, num_dice)
    print(probability)
