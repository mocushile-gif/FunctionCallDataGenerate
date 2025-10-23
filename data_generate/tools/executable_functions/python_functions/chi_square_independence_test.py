import scipy.stats as stats

def chi_square_independence_test(contingency_table: list, significance_level: float = 0.05) -> dict:
    """
    Performs a Chi-Square test for independence on a 2x2 contingency table.

    Parameters:
    - contingency_table (List[List[int]]): A 2x2 contingency table.
    - significance_level (float): The significance level for the Chi-Square test. Defaults to 0.05.

    Returns:
    - dict: A dictionary containing the test statistic, p-value, and result.
    """
    # Perform the Chi-Square test
    chi2_stat, p_value, dof, expected = stats.chi2_contingency(contingency_table)

    # Determine if the null hypothesis is rejected or not
    result = "Reject null hypothesis (independent)" if p_value < significance_level else "Fail to reject null hypothesis (dependent)"

    return {
        "chi2_statistic": round(chi2_stat, 4),
        "p_value": round(p_value, 4),
        "degree_of_freedom": dof,
        "expected_values": expected.tolist(),
        "result": result
    }

# Example usage:
if __name__ == "__main__":
    contingency_table = [[50, 30], [20, 40]]
    result = chi_square_independence_test(contingency_table)
    print(result)
