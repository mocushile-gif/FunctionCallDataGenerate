import numpy as np

def remove_outliers(data: list, threshold: float = 3.0) -> list:
    """
    Removes outliers from the dataset based on Z-score.

    Parameters:
    - data (list): A list of numerical values.
    - threshold (float): The Z-score threshold beyond which a point is considered an outlier.

    Returns:
    - list: The data without outliers.
    """
    data = np.array(data)
    mean = np.mean(data)
    std_dev = np.std(data)
    z_scores = (data - mean) / std_dev
    count=len(data[np.abs(z_scores) >= threshold])
    outliers=data[np.abs(z_scores) >= threshold]
    removed_data=list(data[np.abs(z_scores) < threshold])
    return f'Found {count} outliers', f"Outliers: {outliers}", f"Data without outliers: {list(data[np.abs(z_scores) < threshold])}"

if __name__ == "__main__":
    # Example usage
    data = [19, 3, 6, 10, 9, 4, 4, 22, 8, 7, 5, 7, 4, 4, 8, 13, 5, 5, 11, 7, 13, 24, 12, 5, 8, 10, 7, 8, 8, 7, 10, 12, 15, 17, 5, 6, 4, 4]
    clean_data = remove_outliers(data)
    print(f"{clean_data}")
