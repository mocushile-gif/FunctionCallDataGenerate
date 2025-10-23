tool_dependency_prompt = '''
You will be given a few API functions (called *candidate functions*) and one *source function*. Your task is to identify which candidate functions are **dependent on** the source function.

We define a function **F** as dependent on the source function **S** if any of the following holds:
1. The output of **S** determines whether **F** should be called.
   - Example: `file_exists("a.txt")` → `read_file("a.txt")`

2. The output of **S** is exactly the input to **F**.
   - Example: `get_radius(obj)` → `calculate_area(radius)`

3. The output of **S** is part of the input to **F**.
   - Example: `get_content("file.txt")` → `post(content, id, tags)`

🔁 Cross-domain dependencies are valid. For instance, a weather-checking API might determine if a travel-booking API should be used.

⚠️ The **source function should not appear** in the list of dependent functions.

❗ If no candidate function depends on the source function, return an empty list.

---

source function:
{source_function}

candidate functions:
{candidate_functions}

example outputs of the source function:
{source_function_output}

---

Please return your result **strictly** in the following JSON format (and nothing else):

```json
{{
    "reason": "Explain briefly why the listed functions depend on the source function.",
    "dependent_functions": ["func_a", "func_b"]
}}
```
'''