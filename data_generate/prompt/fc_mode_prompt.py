PARALLEL_TOOL_MODE = """The generated query must involve calling **the same tool multiple times** within a single request. 
This means that although only one tool is used, it should be invoked multiple times to fulfill different but related sub-tasks.

Each call should be structured clearly, with appropriate and complete parameters. The calls should be **parallel and independent of each other**, with no dependency between them.

For example:
- If a weather query tool is available, a valid query could be: 
  "What is the weather like in Beijing and Shanghai tomorrow?"
  → The same weather tool is used twice with different locations.
- If a flight booking tool is available, a good query could be:
  "Check flights from New York to London and from London to Paris for next Monday."
  → Same flight tool called with two different route queries.

The query should remain **clear, concise, and cohesive**, with each tool call contributing meaningfully to the overall request.
"""


MULTIPLE_TOOL_MODE = """The generated query must involve calling **two or more tools**, where each tool addresses a distinct but related part of the user's overall request. 
Unlike DEPENDENT_TOOL_MODE, the tools here are used in a **parallel and independent** manner — the output of one tool is **not required** for the execution of another.

Each tool invocation should be **logically coherent within the same query context**, but **can be executed independently without needing results from previous tools**.

For example:
- If weather and travel route planning tools are available, a valid query could be: 
  "I'm planning a trip to Shanghai tomorrow. Please check the weather there and suggest the best travel route"
  → These are two parallel tasks that don't rely on each other's output.
- If a news tool and a stock price query tool are available, a good query could be:
  "Analyze Tesla's stock performance lately. Also, give me some recent news articles about Tesla."

Avoid generating totally unrelated tool calls. The tools should contribute to a **shared goal**, but each tool call could be **standalone and executable in parallel**.
"""

DEPENDENT_TOOL_MODE = """The generated query must involve calling multiple tools in a sequential order, 
where the parameters for subsequent tool calls depend on the results of previous tool calls. 
Each tool invocation should be structured to ensure logical flow and meaningful dependency.

The query should include all necessary parameters required for executing the tool calls correctly.

For example:
- If a schedule query tool and a meeting booking tool are available, a valid query could be: 
  "Check my schedule for today, and if I have no appointments at 2 PM, book a meeting room for two hours."
- If only a restaurant finder tool is available, a good query could be:
  "Locate ten affordable Chinese restaurants in San Francisco (under $20 per person). If not enough options are available, include Taiwanese restaurants as well."

Ensure that the tool calls are **logically connected**, maintaining a clear dependency between them.
"""

TASK_TOOL_MODE = """
Design a complete task that requires invoking **multiple tools in sequence**, where the output of earlier tools is used as input or condition for subsequent ones. Each step should contribute toward accomplishing a well-defined, practical objective.

Your generated task must:
- Involve at least **three or more tool calls**.
- Establish **clear parameter dependencies** between steps.
- Ensure the steps are executed in a **logically coherent order** to achieve the goal.

For example, given tools like:
- `write_to_file`: Write content into a file.
- `move_or_rename_file_or_directory`: Move or rename a file/folder.
- `check_file_or_dir_exists`: Check if a file or directory exists.
- `code_intepreter`: Execute Python code.

A good multi-step task would be:
"Generate Python code to compute a Fibonacci sequence, run it to ensure it works, and then write it to a file named `fibonacci.py`, move the file to a folder named `python/`, and finally verify that the file exists in the target directory."

Each tool should be invoked in a way that naturally contributes to the next step, demonstrating thoughtful coordination.

Avoid trivial or independent tool calls — the task must **require interdependent tool invocations** to succeed.
"""


SINGLE_TOOL_MODE = """The generated query should be resolved using **only a single tool call**. 
The query must include all necessary parameters required for the tool to execute correctly.

For example:
- If a weather query tool is available, a valid query could be: 
  "Tell me the weather in Shanghai today."

Ensure that the query is **clear, concise, and directly relevant** to the tool being used, without unnecessary complexity.
"""

NO_TOOL_MODE = """The generated query must **not require any tool to be called** in order to answer.  
Even if tools are available, the query can be answered using general knowledge or **should be rejected as it cannot be answered using the available tools**.
For the latter situation, the query is close to what the tools are meant to solve but **cannot be resolved using the currently available tools** — it requires a different or more advanced tool not provided. 

**Examples:**
- If a basic calculator tool is available, a query could be:  
  → "Solve the quadratic equation with a = 1, b = 2, and c = 3."  
- If a real-time weather tool is provided, a query could be:  
  → "What was the temperature in New York exactly one year ago today at noon?"
These queries should be politely rejected, rather than force-fitted into a tool call.
"""

MISS_PARAM_MODE= """The generated query should involve tool calls, but it must **lack one or more critical parameters** required for execution. This simulates a missing-parameter scenario where the system **cannot proceed** without further user input.

Each tool invocation in the query should still be meaningful and reflect a real use case, but it should intentionally omit key information to ensure user clarification is necessary.

Examples:
- If a weather query tool is available, a query could be (missing the location parameter):
  "What's the weather forecast for tomorrow?"
- If a file analysis tool is available, a query could be (missing the file parameter):
  "Analyze this file and summarize the key insights." → (Missing: which file?)
- If a stock information tool is available, a query could be (missing the stock symbol or company name parameter):
  "What’s the current stock price?"

Ensure that:
- The query **requires tool usage**, not general knowledge.
- At least one **required parameter is omitted or vague**.
- Do not mention the missing parameter in the query.
- The missing parameter **must not have appeared in the prior conversation history**. This ensures the system cannot infer it from context and must explicitly ask the user for clarification.
"""
