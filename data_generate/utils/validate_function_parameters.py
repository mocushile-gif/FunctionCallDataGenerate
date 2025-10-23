# from data_generate.tools.executable_functions.file_system_functions import *
# from data_generate.tools.executable_functions.database_functions import *
# from data_generate.tools.executable_functions.python_functions import *
# from data_generate.tools.tau_bench.tau_bench_retail import *
# from data_generate.tools.tau_bench.tau_bench_airline import *
import inspect
from data_generate.tools.executable_functions import REGISTERED_TOOLS as REGISTERED_EXECUTABLE_TOOLS
from data_generate.tools.tau_bench import REGISTERED_TOOLS as REGISTERED_TAUBENCH_TOOLS
# print(REGISTERED_TOOLS.keys())
# func_obj = REGISTERED_TOOLS.get(tool_key)
REGISTERED_TOOLS={}
REGISTERED_TOOLS.update(REGISTERED_EXECUTABLE_TOOLS)
REGISTERED_TOOLS.update(REGISTERED_TAUBENCH_TOOLS)
# print(REGISTERED_TAUBENCH_TOOLS)

def validate_function_parameters(tool_defines):
    """
    Validates that all tool definitions match their corresponding function signatures,
    and that all functions in executable_functions.py have tool definitions.
    """
    tool_names_from_funcs = set()

    # Check tool_defines -> function
    for tool_key, tool in tool_defines.items():
        if 'xlam' in tool_key:
            continue
        tool_name = tool['name']
        tool_arguments = tool["parameters"]["properties"].keys()
        if 'tool_agent' in tool_arguments:
            raise Exception(f"tool agent should not in tool define：{tool_name}")

        func_obj = REGISTERED_TOOLS.get(tool_key)
        # func_obj = globals().get(tool_name)
        if func_obj is None:
            raise Exception(f"[MISSING FUNCTION] Cannot find function: {tool_key}")

        tool_names_from_funcs.add(tool_name)

        try:
            sig = inspect.signature(func_obj)
        except Exception as e:
            print(f"[WARNING] Cannot get signature for function: {tool_name} ({e})")
            continue

        param_lst = [
            name for name, param in sig.parameters.items()
            if name not in ("tool_agent",)  # Optional internal parameters
        ]

        if "kwargs" in param_lst:
            continue

        # Check tool arguments match function signature
        for argument in tool_arguments:
            if argument not in param_lst:
                raise Exception(f"[DEFINE → FUNC] Tool define error for `{tool_name}`: argument `{argument}` not in function signature {param_lst}")

        for param in param_lst:
            if param not in tool_arguments:
                raise Exception(f"[FUNC → DEFINE] Tool define error for `{tool_name}`: parameter `{param}` not in tool define {list(tool_arguments)}")

    tool_names_from_defines = set([tool_define.split('.')[-1] for tool_define in tool_defines.keys()])
    # Check function -> tool_defines
    for func_name, func_obj in globals().items():
        if callable(func_obj) and not func_name.startswith("_") and func_name not in ['validate_function_parameters','load_tool_defines','validate_function_definitions'] and func_name not in tool_names_from_defines:
            raise Exception(f"[MISSING DEFINE] Function `{func_name}` is defined but not found in tool_defines")

    return True


# Example usage
if __name__ == "__main__":
    import data_generate
    import os
    from load_tool_defines import load_tool_defines
    tool_defines={}
    for category in ['api_functions','file_system_functions','database_functions','python_functions']:
        tool_defines.update(load_tool_defines(
            directory=f"{os.path.dirname(data_generate.__file__)}/tools/defines/{category}",
            recursive=True,
        ))
    # print(tool_defines.keys())

    from validate_function_definitions import validate_function_definitions
    # 批量校验
    validation_results = validate_function_definitions(list(tool_defines.values()))

    # 打印结果
    for result in validation_results:
        print(f"Function: {result['function']}")
        print(f"Valid: {result['valid']}")
        print(f"Error: {result['error']}")
        print("-" * 50)
    print(len(validation_results))
    print(validate_function_parameters(tool_defines))