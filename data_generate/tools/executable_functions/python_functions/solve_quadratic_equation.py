import math

def solve_quadratic_equation(a: float, b: float, c: float):
    """解二次方程"""
    try:
        if a == 0:
            return {"error": "这不是二次方程（a不能为0）"}
        
        discriminant = b**2 - 4*a*c
        
        if discriminant > 0:
            x1 = (-b + math.sqrt(discriminant)) / (2*a)
            x2 = (-b - math.sqrt(discriminant)) / (2*a)
            return {
                "equation": f"{a}x² + {b}x + {c} = 0",
                "discriminant": discriminant,
                "solutions": [x1, x2],
                "type": "Two different real roots"
            }
        elif discriminant == 0:
            x = -b / (2*a)
            return {
                "equation": f"{a}x² + {b}x + {c} = 0",
                "discriminant": discriminant,
                "solution": x,
                "type": "One repeated root"
            }
        else:
            real_part = -b / (2*a)
            imag_part = math.sqrt(abs(discriminant)) / (2*a)
            return {
                "equation": f"{a}x² + {b}x + {c} = 0",
                "discriminant": discriminant,
                "solutions": [
                    f"{real_part} + {imag_part}i",
                    f"{real_part} - {imag_part}i"
                ],
                "type": "Two conjugate complex roots"
            }
    except Exception as e:
        return {"error": f"Failed to solve quadratic equation: {str(e)}"}

# Example usage
if __name__ == "__main__":
    import json
    print(json.dumps(solve_quadratic_equation(3, -5, 2)))  # Output: ((2+0j), (1+0j))
