def is_valid_sudoku(board: list[list[str]]) -> bool:
    """
    Checks if a 9x9 Sudoku board is valid.

    Parameters:
    - board (List[List[str]]): The Sudoku board represented as a 2D list of strings.

    Returns:
    - bool: True if the Sudoku board is valid, False otherwise.
    """
    # Checking rows and columns
    for i in range(9):
        row = set()
        col = set()
        for j in range(9):
            # Check row
            if board[i][j] != '.' and board[i][j] in row:
                return False
            if board[i][j] != '.':
                row.add(board[i][j])
            
            # Check column
            if board[j][i] != '.' and board[j][i] in col:
                return False
            if board[j][i] != '.':
                col.add(board[j][i])
    
    # Checking 3x3 sub-grids
    for i in range(3):
        for j in range(3):
            sub_grid = set()
            for row in range(i*3, i*3 + 3):
                for col in range(j*3, j*3 + 3):
                    if board[row][col] != '.' and board[row][col] in sub_grid:
                        return False
                    if board[row][col] != '.':
                        sub_grid.add(board[row][col])
    
    return True

# Example usage
if __name__ == '__main__':
    board_valid = [
        ["5", "3", ".", ".", "7", ".", ".", ".", "."],
        ["6", ".", ".", "1", "9", "5", ".", ".", "."],
        [".", "9", "8", ".", ".", ".", ".", "6", "."],
        ["8", ".", ".", ".", "6", ".", ".", ".", "3"],
        ["4", ".", ".", "8", ".", "3", ".", ".", "1"],
        ["7", ".", ".", ".", "2", ".", ".", ".", "6"],
        [".", "6", ".", ".", ".", ".", "2", "8", "."],
        [".", ".", ".", "4", "1", "9", ".", ".", "5"],
        [".", ".", ".", ".", "8", ".", ".", "7", "9"]
    ]

    board_invalid = [
        ["5", "3", ".", ".", "7", ".", ".", ".", "."],
        ["6", ".", ".", "1", "9", "5", ".", ".", "."],
        [".", "9", "8", ".", ".", ".", ".", "6", "."],
        ["8", ".", ".", ".", "6", ".", ".", ".", "3"],
        ["4", ".", ".", "8", ".", "3", ".", ".", "1"],
        ["7", ".", ".", ".", "2", ".", ".", ".", "6"],
        [".", "6", ".", ".", ".", ".", "2", "8", "."],
        [".", ".", ".", "4", "1", "9", ".", ".", "5"],
        [".", ".", ".", ".", "8", ".", ".", "7", "7"]  # Invalid: Two '7's in the last row.
    ]

    print(is_valid_sudoku(board_valid))   # True
    print(is_valid_sudoku(board_invalid)) # False
