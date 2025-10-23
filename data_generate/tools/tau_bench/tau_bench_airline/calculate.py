# Copyright Sierra

from typing import Any, Dict

def calculate(expression: str) -> str:
    if not all(char in "0123456789+-*/(). " for char in expression):
        return "Error: invalid characters in expression"
    try:
        # Evaluate the mathematical expression safely
        return str(round(float(eval(expression, {"__builtins__": None}, {})), 2))
    except Exception as e:
        return f"Error: {e}"

# Example usage:
if __name__ == "__main__":
    print(calculate('155.33 - 147.05 + 268.77 - 235.13'))