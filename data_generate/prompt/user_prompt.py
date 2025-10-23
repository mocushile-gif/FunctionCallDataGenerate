INIT_QUESTION_SYSTEM_PROMPT = """
The current system time: {current_time}

You are playing the role of a user in a dialogue with an assistant. Your task is to generate a **plausible, well-formed query** that a real user might ask in the current context.

Your identity is: {language_style}

**Your language is: {language}**

### Query Generation Guidelines:

1. **Base the new query on the ongoing conversation.**
   - You can expand the previous user intent.
   - Swap out details while preserving structure.
   - Or shift to a completely different topic (pivot).

2. **Ensure the query is meaningfully different from previous ones.**
   - Change tool usage, introduce new structure, modify key variables, or explore different goals.

3. **Use a natural, directive user tone.**
   - Avoid overly formal phrasing like *"Can you..."* or *"Please..."*
   - Use natural and directive user voice like: *"Show me..."*, *"I want to..."*, *"Give me..."*, *"Help me figure out..."*
   - It’s perfectly fine to be brief—users are lazy and often speak in fragments. What matters is the intent is clear.

4. **Avoid explicit mentions of API or function names.**
   - No phrases like *"Call get_weather_data()"* or *"Use load_table_from_csv()"*
   - Just describe what the user wants in natural terms.

5. **Keep parameters implicit and natural.**
   - Don’t reference file/database/column names directly.
   - Instead, use context-rich phrases like *"the speech on October 17, 2019"* rather than *"DallasOct17_2019.txt"*

6. **Increase complexity where appropriate.**
   - Avoid trivial or default-only queries.
   - Add optional flags, variations, edge cases, or constraints that might impact tool behavior.

7. **Make the query self-contained.**
   - It should contain enough detail for the assistant to act, without requiring back-and-forth clarification.

8. **If referencing fictional or synthetic data:**
   - Make it realistic and structurally rich (mix of text, numbers, timestamps, etc.)
   - Avoid toy examples or obviously fake formats.

9. **Ensure the generated query uses a consistent language**. Avoid mixing languages (e.g., do not mix English and Chinese in one query).
"""

INIT_QUESTION_USER_PROMPT = """
### Conversation History:
{history}

### Available Assistant Tools:
{assistant_tools}
**Remenber you are the user. DO NOT call these tools directly!**

### Query Mode:
{mode}
**The final query should be based on the available assistant tools and follow the query mode.**

### Final Output Format:
When you're ready, output your query in the following format:
<final_query>Your generated query here (following all the guidelines above)</final_query>

### Note:
Just express your intent naturally, like a real user would. Don’t write a plan — just say what you want, and let the assistant figure out the rest.
"""

CLARIFY_USER_PROMPT = """
Conversation History: {history}

Based on the conversation above, please determine the current status of the initial user request by selecting one of the following options:

1. The user's original question or request has been fully and correctly addressed. No further input or action is required from the user. Return **"Finished"**.
2. The request is inherently impossible to fulfill, regardless of additional input. This may be due to technical limitations (e.g., unavailable data, inaccessible APIs), logical contradictions, or constraints such as policy violations or unsupported features. Even with clarification or more information, the task cannot be completed. Return **"Unachievable"**.
3. The request cannot be completed yet because it requires additional clarification, input, or decisions from the user. Once the missing pieces are provided, the task can proceed. Return **"Unsolved"**.

Only return one of the three keywords exactly as specified: "Finished", "Unachievable", or "Unsolved".
"""


CLARIFY_USER_GENERATE_QUERY_PROMPT="""
Conversation History: {history}

You are the USER in the above conversation. Provide only the missing details in the specified language style. 
Language style: {language_style}

### Strict Guidelines:
1. **You are only the USER. Do not act as a model, assistant, or any other role.**
2. **Do not repeat, rephrase, expand or answer the original question. Do not raise a new question. Only supplement missing information.**
3. **Do not provide explanations, suggestions, or unneccessary information.** 
4. Maintain the exact tone and language of the original user input.
5. Only provide the required information, nothing more.
6. If involves fictional or synthetic data, make sure the data is:
   - Realistic — it should reflect plausible real-world scenarios.
   - Complex and detailed — avoid toy examples or overly simplistic values.
   - Structurally rich — include diverse data types such as mixed formats (e.g. text, numbers, timestamps), hierarchical relationships, and multi-field records.

### Important:  
Your response must strictly follow these rules. Any deviation is not allowed.

### When you're ready to generate the final user input, respond using the following format:
<final_input>Your generated user input</final_input>
"""
