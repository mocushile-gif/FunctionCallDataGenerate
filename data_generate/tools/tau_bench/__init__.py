import os
import glob
import importlib

base_dir = os.path.dirname(__file__)
pattern = os.path.join(base_dir, "**", "*.py")
modules = glob.glob(pattern, recursive=True)

REGISTERED_TOOLS = {}

for path in modules:
    if path.endswith("__init__.py"):
        continue

    rel_path = os.path.relpath(path, base_dir)                  # 相对路径
    module_name = rel_path[:-3].replace(os.sep, ".")            # 模块路径
    function_name = os.path.basename(path)[:-3]                 # py 文件名（不带 .py）
    parent_dir = os.path.basename(os.path.dirname(path))        # 上一级文件夹名

    try:
        full_module = importlib.import_module(f".{module_name}", package=__package__)

        if hasattr(full_module, function_name):
            key = f"{parent_dir}.{function_name}"               # 仅保留文件夹.文件名
            REGISTERED_TOOLS[key] = getattr(full_module, function_name)
        else:
            print(f"⚠️ Module '{module_name}' does not contain function '{function_name}'.")

    except Exception as e:
        print(f"❌ Failed to import from '{module_name}': {e}")
