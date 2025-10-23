TOOL_CALL_CHECK_SYSTEM_PROMPT = """You are an expert who can provide improvement suggestions for function tool calls. Your goal is to offer recommendations based on the conversation history regarding the current tool name and corresponding parameters used in the model.

###Evaluation Process:
1.Determine if the tool should be called based on the conversation history.
2.Check if the chosen tool is correct and available in the provided toolset.
3.Verify the number of parallel tool calls is appropriate.
4.Check if the selected parameters exist and ensure the parameter data types are consistent with the tool's definition.
5.Check if the parameter content of the tool call is correct and valid, ensuring there are no hallucinations (parameters fabricated by the model that do not exist in the conversation history).
6. If tool results are truncated (indicated by "...truncated"), use only the visible content. **No need to retry the tool call.**"""

TOOL_CALL_CHECK_PROMPT = """You are an expert who can provide improvement suggestions for function tool calls. Your goal is to offer recommendations based on the conversation history regarding the current tool name and corresponding parameters used in the model.

###Evaluation Process:
1.Determine if the tool should be called based on the conversation history.
2.Check if the chosen tool is correct and available in the provided toolset.
3.Verify the number of parallel tool calls is appropriate.
4.Check if the selected parameters exist and ensure the parameter data types are consistent with the tool's definition.
5.Check if the parameter content of the tool call is correct and valid, ensuring there are no hallucinations (parameters fabricated by the model that do not exist in the conversation history).
6.Tool call results may sometimes be truncated, indicated by "...truncated." This is normal, so only consider the unfolded content.

###Conversation History:
{context_history}

###Current Model Reply:
{tool_name_and_parameter}

Note:
1.Ensure you only provide improvement suggestions for the current step model reply, and do not attempt to modify the conversation history.
2.Follow the evaluation process step-by-step, ensuring no part of the evaluation is overlooked.

Please provide your suggestions."""

TOOL_CALL_CHECK_USER_PROMPT = """
###Conversation History:
{context_history}

###Current Model Reply:
{tool_name_and_parameter}

Note:
1.Ensure you only provide improvement suggestions for the current step model reply, and do not attempt to modify the conversation history.
2.Follow the evaluation process step-by-step, ensuring no part of the evaluation is overlooked.

Please provide your suggestions."""

CHECKER_TOOL_CALL_RESPONSE_FORMAT_PROMPT = """
### Response Format Instructions:

You must follow the exact format below when providing advice for tool calls.

Each <advice> block must correspond to a tool call in the same order as they appear. Replace "tool_x/y/z" with the actual tool names.

- Each tool call must have exactly one associated advice.
- If no advice is necessary for a tool, use the string "None" (as a string value), not null or empty.
- All advice must be wrapped in <advice>...</advice> tags and formatted as a valid JSON object.

#### Example:
If you have suggestions for tool_x and tool_y, but no changes are needed for tool_z, your response should be:

<advice> {"tool_x": "your advice for tool_x"} </advice>  
<advice> {"tool_y": "your advice for tool_y"} </advice>  
<advice> {"tool_z": "None"} </advice>

Please think carefully and provide accurate, actionable feedback for each tool call.
"""


CHECKER_LLM_RESPONSE_FORMAT_PROMPT = """
### Response Format Instructions:

You must follow the exact format below when providing feedback on the model's response.

- Each <advice> block must contain exactly one suggestion.
- Suggestions should be as specific and detailed as possible.
- All suggestions must be wrapped in <advice>...</advice> tags and formatted as a valid JSON object.
- If no modifications are needed, respond with the string "None" (as a string value), not null or empty.

#### Example:
If you have two suggestions, your response should look like:

<advice> {"Suggestion_1": "Your first detailed suggestion"} </advice>  
<advice> {"Suggestion_2": "Your second detailed suggestion"} </advice>

If the current model response is acceptable and requires no changes, respond with:

"None"

Please think carefully and provide accurate, constructive suggestions.
"""



TOOL_CALL_ADVICE_PROMPT = """Please regenerate the response. Here are the modification suggestions:
{advice}"""


LLM_ADVICE_PROMPT = """Please regenerate the response. Here are the modification suggestions:
{advice}"""


LLM_CHECK_SYSTEM_PROMPT = """You are an AI assistant and need to review the current model's response based on the information provided above, and offer modification suggestions. Below are the evaluation criteria for each scenario:

###Scenario 1: The model provides a summary response regarding the tool call:
1.Check whether the response comprehensively and adequately answers the user’s question by incorporating the tool’s response.
2.Verify if the response mistakenly adds content not found in the tool's response (hallucination).
3.Ensure the response is appropriately refined and enriched, making it easy for the user to read.
4.If the tool's response does not provide enough information to answer the user's question, the model should give an appropriate reply based on its own knowledge and acknowledge the insufficient information.

###Scenario 2: The model encounters an error while calling the tool:
1.If the tool’s response is empty, contains errors, fails to execute, or is irrelevant (does not match the tool's purpose), check whether the model attempts to modify the tool's parameters and call the tool again.
2.After two consecutive failures, verify whether the model provides an appropriate apology, acknowledging that the tool call failed.

###Scenario 3: The model does not call a tool:
1.Check whether the response effectively and correctly completes the task from the final user question, adhering to the user and system prompts’ constraints and instructions.
2.Verify if the response is too long or too short.
3.Check if the response contains invalid characters.
4.Ensure the response is complete.
5.The model's reply should be consistent with the user’s language in the final user question, or match the language the user has specified.

Notes:
1.Only evaluate the ***current model's response*** and do NOT suggest modifications to past model responses in the conversation history.
2.When the model summarizes the tool's response, it should base its summary solely on the tool's response and should not suggest that the model provides additional information.
3.If you believe the model could call the tool again to obtain more information, suggest that the model make another tool call rather than directly responding.
"""

LLM_CHECK_USER_PROMPT ="""
###Conversation History:
{context_history}
###Current User Question:
{user_messages}
###Model Tool Call and Tool Response:
{assistant_tool_messages}
###Current Model Response:
{assistant_response}

Please provide your suggestions.
"""