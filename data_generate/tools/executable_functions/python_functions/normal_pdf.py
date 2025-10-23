import scipy.stats as stats

def normal_pdf(x: float, mean: float = 0, std_dev: float = 1) -> float:
    """
    Calculate the probability density function (PDF) of a normal distribution.

    Parameters:
    - x (float): The point at which the PDF is evaluated.
    - mean (float): The mean of the distribution (default is 0).
    - std_dev (float): The standard deviation of the distribution (default is 1).

    Returns:
    - float: The value of the PDF at point x.
    """
    return stats.norm.pdf(x, mean, std_dev)

if __name__ == "__main__":
    value = normal_pdf(0.0)  # Evaluate the PDF at x=1.0 for standard normal distribution
    print(value)
