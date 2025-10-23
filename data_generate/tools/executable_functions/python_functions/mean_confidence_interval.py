import math
from scipy.stats import norm, t

def mean_confidence_interval(mean: float, std_dev: float, sample_size: int, confidence: float = 0.95, distribution: str = 'normal') -> tuple:
    """
    Calculates the confidence interval for a sample mean.

    Parameters:
    - mean (float): The mean of the sample.
    - std_dev (float): The standard deviation of the sample.
    - sample_size (int): The size of the sample.
    - confidence (float): The desired confidence level. Default is 0.95.
    - distribution (str): The type of distribution used for the confidence interval ('normal' or 't'). Default is 'normal'.
    
    Returns:
    - tuple: A tuple containing the lower and upper bounds of the confidence interval.
    """
    # Check if the sample size is valid
    if sample_size < 2:
        raise ValueError("Sample size must be at least 2 to calculate the confidence interval.")
    
    # Standard error of the mean
    sem = std_dev / math.sqrt(sample_size)
    
    # Determine the z or t score depending on the distribution
    if distribution == 'normal':
        # Use z-score for normal distribution
        z_score = norm.ppf(1 - (1 - confidence) / 2)
    elif distribution == 't':
        # Use t-score for t-distribution (Student's t-distribution)
        degrees_of_freedom = sample_size - 1
        z_score = t.ppf(1 - (1 - confidence) / 2, df=degrees_of_freedom)
    else:
        raise ValueError("Unsupported distribution type. Use 'normal' or 't'.")
    
    # Calculate margin of error
    margin_of_error = z_score * sem
    
    # Calculate confidence interval
    lower_bound = mean - margin_of_error
    upper_bound = mean + margin_of_error
    
    return lower_bound, upper_bound

# Example usage:
if __name__ == "__main__":
    mean = 50
    std_dev = 10
    sample_size = 30
    confidence = 0.95

    # For a normal distribution
    ci_normal = mean_confidence_interval(mean, std_dev, sample_size, confidence, distribution='normal')
    print(f"Normal Distribution CI: {ci_normal}")
    
    # For a t-distribution
    ci_t = mean_confidence_interval(mean, std_dev, sample_size, confidence, distribution='t')
    print(f"T-Distribution CI: {ci_t}") 