import math

def binomial_probability(n: int, k: int, p: float) -> float:
    """
    Calculates the probability of getting exactly k successes in n independent trials.

    Parameters:
    - n (int): The total number of trials.
    - k (int): The number of successes.
    - p (float): The probability of success in each trial.

    Returns:
    - float: The probability of getting exactly k successes in n trials.
    """
    # Calculate binomial coefficient (n choose k)
    binomial_coeff = math.comb(n, k)
    
    # Calculate probability using the binomial distribution formula
    probability = binomial_coeff * (p**k) * ((1 - p)**(n - k))
    
    return probability

# Example usage:
if __name__ == "__main__":
    n = 10  # Total number of trials
    k = 3   # Number of successes
    p = 0.5 # Probability of success in each trial
    
    prob = binomial_probability(n, k, p)
    print(f"The probability of {k} successes in {n} trials is: {prob:.4f}")
