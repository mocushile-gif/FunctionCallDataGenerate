import ast
import operator as op

# 支持的运算符
allowed_operators = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.USub: op.neg,
}

def calculator(expression: str):
    if not all(char in "0123456789+-*/(). " for char in expression):
        return "Error: invalid characters in expression"
    def _eval(node):
        if isinstance(node, ast.Num):  # 常数
            return node.n
        elif isinstance(node, ast.BinOp):  # 二元操作
            return allowed_operators[type(node.op)](_eval(node.left), _eval(node.right))
        elif isinstance(node, ast.UnaryOp):  # 负号等
            return allowed_operators[type(node.op)](_eval(node.operand))
        else:
            raise TypeError(f"不支持的表达式：{node}")

    parsed = ast.parse(expression, mode='eval').body
    return _eval(parsed)

# Example usage:
if __name__ == "__main__":
    print(calculator("2**5"))  # 输出 288
