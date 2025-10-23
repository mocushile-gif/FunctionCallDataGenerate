VIRTUAL_TOOL_RESPONSE_PROMPT="""You are a tool simulator, capable of simulating the output of a given tool based on a specific use case.

###Function Definition of the Tool:
{tool_define}

###Output Format:
{response}

###Examples:
{usage_examples}

###Current Input:
{request}

Based on the examples above, please provide the simulated output of the tool for the current input. The output should conform to the specified JSON format as outlined above."""
