

MULTIPLE_OR_DEPENDENT_MODE = """
The generated user query must require invoking **all tools listed in the provided sequence** in order to be resolved correctly.

For example, given the list:
[
    "func_A",
    "func_B",
    "func_C"
]
the query must implicitly involve **exactly three tool calls**, one for each of the listed tools. These tool calls may fall into one of two categories:

- **Dependent (chained)**: The output of one tool (e.g., `func_A`) is used as input for the next (e.g., `func_B`), forming a logical execution sequence.
- **Independent (parallel)**: Each tool performs a distinct, non-overlapping task, and there are no dependencies between them.

**Examples:**
- If both a weather query tool and a route planning tool are available, a valid query could be:  
  → "I'm planning a trip to Shanghai tomorrow. Please check the weather there and suggest the best travel route."  
  (Two independent tool calls — one for weather, one for routing.)

- If a `group_and_aggregate_data` tool, a `create_bar_chart` tool and a `check_file_exists` tool are available, a valid query could be:  
  → "Group the data by date, create a bar chart from the result, and finally check whether the image file exists."
  (This involves dependent operations — first aggregate the data, then visualize it, and lastly verify the chart file.)

**Requirements:**
- The query must require **exactly one call per tool** listed in the tool sequence.
- All tools must be **necessary** to fully resolve the query.
- Each tool call must be **complete** with all required parameters — either specified directly or derived through dependency.
"""


PARALLEL_MODE = """
The generated query must involve calling **the same tool multiple times**, exactly matching the number of times it appears in the provided list.  
Each call should be **independent and parallel**, with no dependency between them. All calls must be clearly structured and include the necessary parameters for successful execution.

For example:
[
    "func_A",
    "func_A"
]
indicates that the generated query should invoke `func_A` twice — each with distinct inputs.

**Examples:**
- If a weather query tool is available, a valid query would be:  
  → "What is the weather like in Beijing and Shanghai tomorrow?"  
  (The tool is called twice: once for Beijing, once for Shanghai.)

- If a flight booking tool is available, a valid query would be:  
  → "Check flights from New York to London and from London to Paris for next Monday."  
  (Two independent flight route checks using the same tool.)

**Requirements:**
- The query must involve **multiple calls to the same tool**.
- The query must include **all required parameters** needed for the tool to execute successfully.
"""



SINGLE_MODE = """The generated query should be resolved using **only a single tool call**.  

For example:
[
    "func_A"
]
indicates that the generated query should invoke `func_A` exactly once, with no additional tool calls involved.

**Example:**
- If a weather query tool is available, a valid query would be:  
  → "Tell me the weather in Shanghai today."

**Requirements:**
- The query should map to exactly **one tool**.
- All **required parameters must be explicitly provided**.
- The query must be executable **without any need for follow-up questions or clarification**.
"""


MISS_FUNC_MODE = """The generated query must **not require any tool invocation** to be answered.  
Even if tools are available, the query should either be:

- **Answerable using general knowledge**, in which case it should be answered directly without calling any tool.
- **Unanswerable with the available tools**, in which case it should be **politely rejected** — the query may resemble the tool's purpose but requires a different or more advanced tool that is not provided.

**Examples:**

- If a basic calculator tool is available, a query like:  
  → "Solve the quadratic equation with a = 1, b = 2, and c = 3."  
  should be rejected, as it exceeds the calculator's capabilities.

- If a real-time weather tool is provided, a query like:  
  → "What was the temperature in New York exactly one year ago today at noon?"  
  should also be rejected, as it requires historical data not accessible via the tool.

- If a tool is available for calculating standard deviation from data, a query like:  
  → "What is the formula for standard deviation?"  
  should be answered directly with general knowledge — **no need to call the tool**.
"""

MISS_PARAM_MODE = """The generated query should involve a tool call but must **lack one or more critical parameters** required for successful execution. The system should **not proceed** without obtaining further input from the user.

Each tool invocation in the query should remain meaningful and aligned with a real use case, but it must **intentionally omit** key information, prompting the system to request clarification.

For example:
[
    "func_A",
    "__miss params__"
]
indicates that the generated query intends to call `func_A`, but one or more of its required parameters are missing.

**Examples:**
- If a meeting scheduling tool is available, a query like:  
  → "Schedule a meeting for me."  
  is missing the required **time** parameter.

- If a stock lookup tool is available, a query like:  
  → "What’s the current stock price?"  
  is missing the **stock symbol or company name** parameter.

**Requirements:**
- The query must **require tool usage** (i.e., it cannot be answered using general knowledge alone).
- At least one **required parameter must be missing or unspecified**.
- The missing parameter should **not be mentioned explicitly in the query**.
- The missing parameter must **not be inferable from prior conversation context**.
- Most importantly, the missing information must **only be obtained through user clarification**.
- The missing information should not be file/database path, table/column names, as they can be obtained via other tool calls.
"""

