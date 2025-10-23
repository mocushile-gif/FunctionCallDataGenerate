import numpy as np

def matrix_multiply(matrix_a, matrix_b):
    """
    Multiplies two matrices.

    Parameters:
    - matrix_a (list of lists): The first matrix.
    - matrix_b (list of lists): The second matrix.

    Returns:
    - list of lists: The resulting matrix after multiplication.
    """
    return np.dot(matrix_a, matrix_b).tolist()

if __name__ == "__main__":
    # Example usage
    matrix_a = [[1, 2], [3, 4]]
    matrix_b = [[5, 6], [7, 8]]
    result = matrix_multiply(matrix_a, matrix_b)
    print("Matrix Product:")
    for row in result:
        print(row)
