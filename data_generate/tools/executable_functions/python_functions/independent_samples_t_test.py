import scipy.stats as stats
from typing import List, Tuple

def independent_samples_t_test(sample1: List[float], sample2: List[float], alpha: float = 0.05) -> Tuple[float, float, str]:
    """
    Conducts a two-sample independent t-test and returns the t-statistic, p-value, and conclusion.
    
    Parameters:
    - sample1 (List[float]): The first sample of observations.
    - sample2 (List[float]): The second sample of observations.
    - alpha (float): The significance level of the test. Defaults to 0.05.
    
    Returns:
    - Tuple[float, float, str]: A tuple containing the t-statistic, p-value, and conclusion.
    """
    # Perform the independent t-test
    t_statistic, p_value = stats.ttest_ind(sample1, sample2)
    
    # Determine the conclusion based on p-value
    if p_value <= alpha:
        conclusion = "Reject the null hypothesis (significant difference)."
    else:
        conclusion = "Fail to reject the null hypothesis (no significant difference)."
    
    return f"T-statistic: {t_statistic}"+f"\nP-value: {p_value}"+f"\nConclusion: {conclusion}"

# Example usage:
if __name__ == "__main__":
    # Example samples
    sample1 = [2.3, 2.9, 3.1, 3.7, 3.2]
    sample2 = [4.5, 5.1, 5.3, 4.9, 5.7]
    
    conclusion = independent_samples_t_test(sample1, sample2, alpha=0.05)
    
    print(conclusion)
