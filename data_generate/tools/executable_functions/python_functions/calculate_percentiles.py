import numpy as np

def calculate_percentiles(data: list) -> dict:
    """
    Calculate the median, lower quartile (Q1), upper quartile (Q3), and interquartile range (IQR) of a dataset.

    Parameters:
    - data (list): A list of numerical values.

    Returns:
    - dict: A dictionary containing median, Q1, Q3, and IQR.
    """
    data = np.array(data)
    median = np.median(data)
    q1 = np.percentile(data, 25)
    q3 = np.percentile(data, 75)
    iqr = q3 - q1
    return {
        "median": median,
        "Q1": q1,
        "Q3": q3,
        "IQR": iqr
    }

if __name__ == "__main__":
    data = [10, 12, 13, 15, 200, 17, 20, 21]
    stats = calculate_percentiles(data)
    print(stats)
