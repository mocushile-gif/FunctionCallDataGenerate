tool_category_prompt = '''
You will be given one or more API functions.  
Your task is to determine whether **each function is a lookup function, a modification function, or both**.

Definitions:

- A function is a lookup function if:
    - Its primary goal is to retrieve or extract information without altering any existing state.
    - It may read from files, call APIs, query databases, or perform calculations.
    - Examples: performing calculations, sending a request to an API, reading data from a file, querying a database, extracting metadata, etc.

- A function is a modification function if:
    - It may create, delete, update, or otherwise modify any files, directories, databases, or system state.
    - This includes both direct changes (e.g., writing to a file) and indirect ones (e.g., invoking a command that alters the environment).
    - Examples: generating a file, deleting a file, updating a database record, renaming a directory, changing file permissions or ownership, modifying environment variables, etc.

- A function is a realtime function if:
    - For the same parameters, its result is not fixed or deterministic.
    - Usually involves real-time information or randomness.
    - Examples: querying the current weather, fetching live stock prices, checking current CPU usage, generating random data.

---

**Notes**:
- A function can be in multiple categories at the same time.
- Example: a function that fetches data from the internet and saves it to disk → lookup = true, modification = true, realtime = maybe true depending on the nature of the data.

---

**Examples**:

- `get_weather_info(city)` →  
  ✅ Lookup: true  
  ❌ Modification: false  
  ✅ Realtime: true

- `delete_file(path)` →  
  ❌ Lookup: false  
  ✅ Modification: true  
  ❌ Realtime: false

- `web_search(query, save_to=output_file)` →  
  ✅ Lookup: true  
  ✅ Modification: true  
  ✅ Realtime: true

- `get_current_time()` →  
  ✅ Lookup: true  
  ❌ Modification: false  
  ✅ Realtime: true

---

**Function to classify:**
{function}

---

Please return your result **strictly** in the following JSON format (and nothing else):

```json
{{
  "reason": "Explain why the function is categorized as lookup, modification, or both.",
  "is_lookup_function": true or false,
  "is_modification_function": true or false,
  "is_realtime_function": true or false
}}
```
'''