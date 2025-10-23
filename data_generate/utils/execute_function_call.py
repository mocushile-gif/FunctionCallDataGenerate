from data_generate.tools.executable_functions.file_system_functions import *

# Script to execute function calls dynamically
def execute_function_call(tool_calls):
    """
    Extracts the function name and arguments from the tool_calls and executes the function.

    Parameters:
    - tool_calls (dict): A dictionary containing 'name' and 'arguments' for the function call.
    """
    # Extract function name and arguments
    function_name = tool_calls['function']['name']
    arguments = tool_calls['function']['arguments']
    print(globals())
    # Check if the function exists in the current namespace
    if function_name in globals():
        # Call the function dynamically using its name
        try:
            res=globals()[function_name](**arguments)
            return res
        except Exception as e:
            return {'status':'failed','message':f'Something went wrong with tool "{function_name}". Reason:{str(e)}'}
    else:
        return {'status':'failed','message':f"Function '{function_name}' not recognized."}

if __name__ == "__main__":
    tool_calls={'role': 'assistant', 'tool_calls': [{'function': {'name': 'execute_linux_system_command', 'arguments': {'command': 'ls -l ./'}}, 'id': 'call_01a292de-4ef9-457e-b03f-202ade2b93a8', 'type': 'function'}]}
    # tool_calls={'role': 'assistant', 'tool_calls': [{'function': {'name': 'execute_linux_system_command', 'arguments': {'command': 'find /mnt/nvme0/qinxinyi/function_call_data/data_generate/ -name "*.jsonl"'}}, 'id': 'call_01a292de-4ef9-457e-b03f-202ade2b93a8', 'type': 'function'}]}
    tool_messages=[]
    for tool_call in tool_calls['tool_calls']:
        tool_res=execute_function_call(tool_call)
        message={'role': 'tool', 'content':tool_res,'tool_call_id':tool_call['id']}
        tool_messages.append(message)
    print(tool_messages)