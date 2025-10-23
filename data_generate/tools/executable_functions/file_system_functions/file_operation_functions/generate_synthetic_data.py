import numpy as np
import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()

def generate_synthetic_data(size: int,
                         distribution_type: str = 'normal',
                         return_type: str = 'list',
                         seed: int = None,
                         dimensions: int = 1,
                         save_path: str = None,
                         **kwargs):

    """
    Generate random data based on specified distribution and optionally save to a CSV file.

    Parameters:
    - size (int): Number of samples to generate (per dimension).
    - distribution_type (str): 'normal', 'uniform', 'poisson', 'binomial', 'exponential'.
    - return_type (str): 'list', 'numpy', 'dict', or 'dataframe'.
    - seed (int): Optional random seed.
    - dimensions (int): Number of dimensions/features to generate.
    - save_path (str): Optional. If specified and return_type is dataframe or dict, save to CSV.
    - kwargs: Additional parameters for distribution.

    Returns:
    - The generated data in the specified format.
    """
    if seed is not None:
        np.random.seed(seed)

    if dimensions < 1:
        raise ValueError("dimensions must be >= 1")

    shape = (size, dimensions) if dimensions > 1 else (size,)

    if distribution_type == 'normal':
        mean = kwargs.get('mean', 0)
        std_dev = kwargs.get('std_dev', 1)
        data = np.random.normal(mean, std_dev, shape)
    elif distribution_type == 'uniform':
        low = kwargs.get('low', 0)
        high = kwargs.get('high', 1)
        data = np.random.uniform(low, high, shape)
    elif distribution_type == 'poisson':
        lam = kwargs.get('lam', 1)
        data = np.random.poisson(lam, shape)
    elif distribution_type == 'binomial':
        n = kwargs.get('n', 10)
        p = kwargs.get('p', 0.5)
        data = np.random.binomial(n, p, shape)
    elif distribution_type == 'exponential':
        scale = kwargs.get('scale', 1.0)
        data = np.random.exponential(scale, shape)
    else:
        raise ValueError(f"Unsupported distribution type: {distribution_type}")

    # Convert to desired format
    if return_type == 'list':
        return_data = data.tolist()
    elif return_type == 'numpy':
        return_data = data
    elif return_type == 'dict':
        return_data = {f'feature_{i}': data[:, i].tolist() if dimensions > 1 else data.tolist()
                       for i in range(dimensions)}
    elif return_type == 'dataframe':
        cols = [f'feature_{i}' for i in range(dimensions)]
        return_data = pd.DataFrame(data, columns=cols) if dimensions > 1 else pd.DataFrame(data, columns=['feature_0'])
    else:
        raise ValueError(f"Unsupported return_type: {return_type}")

    # Optionally save to file
    if save_path:
        os.makedirs(os.path.dirname(save_path) or '.', exist_ok=True)
        if return_type == 'dataframe':
            return_data.to_csv(save_path, index=False)
        elif return_type == 'dict':
            df = pd.DataFrame(return_data)
            df.to_csv(save_path, index=False)
        elif return_type == 'list':
            df = pd.DataFrame({'value': return_data})
            df.to_csv(save_path, index=False)
        elif return_type == 'numpy':
            df = pd.DataFrame(data)
            df.to_csv(save_path, index=False)
        else:
            raise ValueError("Cannot save unknown return type.")

    return return_data

if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    df = generate_synthetic_data(
        size=1000,
        distribution_type='normal',
        mean=5,
        std_dev=2,
        dimensions=3,
        return_type='list',
        save_path='output/normal_3d.csv',
        seed=42
    )
    print(df)
