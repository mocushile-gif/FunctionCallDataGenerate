extract_lookup_task_answer_prompt = '''
You will be given the conversation history of a task.

Your objective is to extract the **shortest necessary fields** from the final **tool-based answer**, in order to **determine whether the task has been successfully completed**. These fields must:

1. **Verbatim Only**:  
   Extract exact sub-strings from the tool’s output.  
   ⛔ Do not rephrase, summarize, or infer.

2. **Minimal but Sufficient**:  
   Extract only the **smallest self-contained units** (e.g. key-value pair, phrase, line) that confirm task outcome.  
   These must be sufficient to judge whether the task succeeded, failed, or returned a meaningful output.

3. **Preserve Formatting**:  
   ✅ Preserve all original punctuation, spacing, and newlines.  
   ⛔ Do not clean or alter the text.

4. **Long Lists**:  
   If the tool returns many items, extract only the **first 1–2 representative items**, as long as they prove the operation succeeded.

5. **Real-time or Random Outputs**:  
   For tasks involving real-time or random content (current_weather, web_search, convert_currency, random_jokes, draw_cards, random_data), do **not** extract actual data values.  
   ✅ Only extract **success/failure signals** from tool result or key paramater in tool call, such as:
   - `"status": "success"`
   - `"error": false`
   - `"Drawing 5 card(s) from the deck"`
   - `"name": "Chicago"`
   - "from": "USD", "to": "CAD", "amount": 500
   - "base_currency": "USD", "target_currency": "EUR,GBP"
   - "type": "guoji"

6. **Multiple Sub-strings Allowed for Long Outputs**:  
   If the tool response is long and contains both useful and irrelevant content,  
   ✅ You may extract **multiple short sub-strings** from **different parts** of the response,  
   as long as each is necessary and contributes to verifying the task result.  
   ⛔ Do not extract large blocks of text unless the whole block is minimal and required.

---

**Examples:**

1. Task: *Compare two files*  
   Tool output: `["Compared: ./file1.txt, ./file2.txt\\nStatus: identical"]`  
   → `"shortest_necessary_answer_string": ["Status: identical"]`

2. Task: *Extract user IDs*  
   Tool output: `["user_001", "user_002", "user_003", "user_004"]`  
   → `"shortest_necessary_answer_string": ["\"user_001\"", "\"user_002\""]`

3. Task: *Check Chicago weather*  
   Tool output: `"coord": [...], "weather": [...], "name": "Chicago", "cod": 200`  
   → `"shortest_necessary_answer_string": ["\"name\": \"Chicago\""]`

4. Task: *Draw 5 cards from a deck*  
   Tool output: `"Drawing 5 card(s) from the deck: ['Ace of Hearts', ...]"`  
   → `"shortest_necessary_answer_string": ["Drawing 5 card(s) from the deck"]`

5. Task: *Extract from complex output*  
   Tool output: `"Tool executed successfully. \nExtracted entities: [\"gene1\", \"gene2\", \"gene3\"]\nSome irrelevant logs..."`  
   → `"shortest_necessary_answer_string": ["Tool executed successfully.", "\"gene1\"", "\"gene2\""]`

---

**The task:**
{task}

**The Conversation history:**
{task_messages}

---

**Output Format (strict JSON only):**

```json
{{
  "reason": "Explain how the extracted strings minimally and sufficiently fulfill the task's requirements.",
  "shortest_necessary_answer_string": []
}}
```
'''
