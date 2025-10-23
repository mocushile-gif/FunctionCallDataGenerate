import os
import glob

# 获取当前目录下的所有 .py 文件（不包括 __init__.py）
modules = glob.glob(os.path.join(os.path.dirname(__file__), "*.py"))
__all__ = [os.path.basename(f)[:-3] for f in modules if os.path.isfile(f) and not f.endswith("__init__.py")]

# 动态导入所有模块
for module in __all__:
    exec(f"from .{module} import {module}")

