INIT_QUESTION_SYSTEM_PROMPT = """
Current system time: {current_time}

You are playing the role of a **user** in a dialogue with an assistant. Your task is to generate a **plausible, well-formed query** that a real user might ask given the current context.

Your persona: {language_style}  
**Language to use: {language}**

---

### Query Generation Guidelines

1. **Build on the ongoing conversation.**  
   - You may use relevant details from the dialogue history when forming your query.

2. **Use a natural, directive user tone.**  
   - Avoid overly formal phrasing like *"Can you..."* or *"Please..."*  
   - Prefer casual, direct expressions such as: *"Show me..."*, *"I want to..."*, *"Give me..."*, *"Help me figure out..."*  
   - It's okay to be brief — real users often speak in fragments.

3. **Avoid mentioning API or function names.**  
   - Do **not** include technical phrases like *"Call get_weather_data()"* or *"Use load_table_from_csv()"*  
   - Instead, describe the question naturally, as a user would.

4. **Keep parameters implicit and context-rich.**  
   - Avoid directly naming files, databases, or columns.  
   - Use natural language like: *"the speech on October 17, 2019"* rather than *"DallasOct17_2019.txt"*

5. **Introduce realistic complexity.**  
   - Avoid trivial queries with only default settings.  
   - Modify or override default parameters meaningfully where appropriate.

6. **If referencing fictional or synthetic data:**  
   - Make the dataset sufficiently large (e.g., more than 30 entries).  
   - Ensure structural richness (e.g., mix of text, numbers, timestamps).  
   - Avoid simplistic toy examples or obviously fake content.

7. **The query must be achievable.**  
   - Only generate queries that the given tools can handle. 
   - For example, if tools only support SQLite database, do not generate query related to Excel or CSV files. If tools only handle numeric data, don’t ask about string data.

8. **Maintain consistent language throughout.**  
   - Do not mix languages (e.g., avoid combining English and Chinese in the same query).
"""


INIT_QUESTION_USER_PROMPT = """
### Conversation History:
{history}

---

### Available Tools:
{tools}  
**Reminder: You are playing the role of the user. DO NOT call these tools directly!**

---

### Tool-Call Mode for This Turn:
{fsp_current_turn}

#### Mode Explanation:
{mode}

---

### Final Output Format:
When you're ready, write your query using the following format:

<final_query>The generated query using imperative sentences or first-person phrasing (follow all the instructions above)</final_query>

---

### Important Guidelines:
- Speak naturally — as if you were a real user asking for help.
- DO NOT include explanations or reasoning steps.
- Focus on clearly expressing your goal or request — the assistant will take care of planning and tool invocation.
"""


FILE_TOOL_ENVIRONMENT = """
{file_system_info}

### Files information:
{file_info}

### Notes:
1. You can query or issue commands based on the above files.
2. If your question relates to any of the above files, please refer only to the actual data structure — do not assume any additional columns or content.
3. DO NOT provide absolute file paths directly. Instead, refer to files or directories using natural language descriptions (e.g., "the log file under the logs folder").
"""

CLARIFY_USER_PROMPT = """
### Conversation History:
{history}

Based on the conversation above, please determine the current status of the initial user request by selecting one of the following options:

1. The user's original question or request has been fully and correctly addressed. No further input or action is required from the user. Return **"Finished"**.
2. The request is inherently impossible to fulfill, regardless of additional input. This may be due to technical limitations (e.g., unavailable data, inaccessible APIs), logical contradictions, or constraints such as policy violations or unsupported features. Even with clarification or more information, the task cannot be completed. Return **"Unachievable"**.
3. The request cannot be completed yet because it requires additional clarification, input, or decisions from the user. Once the missing pieces are provided, the task can proceed. Return **"Unsolved"**.

Only return one of the three keywords exactly as specified: "Finished", "Unachievable", or "Unsolved".
"""

FILE_ENVIRONMENT_FOR_CLARITY = """
{file_system_info}

### Files information:
{file_info}
"""

CLARIFY_USER_GENERATE_QUERY_PROMPT = """
### Conversation History:
{history}

---

### Original User Question:
{user_question}  

---

You are the USER in the above conversation. Your task is to **provide only the missing information** based on the conversation and file info above, while using the specified language style.  
Language style: {language_style}

---

### Strict Guidelines:
1. **You are only the USER. Do not act as an assistant, model, or any other role.**
2. Maintain the original tone, wording, and language style of the user's input.
3. Only provide the necessary missing detail(s) — nothing more.
   - **Do not repeat, rephrase, or expand the original question.**
   - **Do not ask new questions or request additional actions.**
   - **Do not offer explanations, suggestions, or any extra content.**
4. **If the query involves the file system, refer strictly to the listed files above. Do not assume, fabricate, or mention files not explicitly provided.**

---

### Important:  
You must adhere to all rules above. Any deviation is unacceptable.

---

### Final Output Format:
When you're ready, write your input in the following format:

<final_input>Your generated user input here</final_input>
"""
