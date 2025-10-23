tool_file_dependency_prompt = '''
You will be given information about a file, including its **path**, **name**, **structure**, and **sample contents**, as well as a list of API functions. Your task is to determine **which functions are likely to use this file** as input.

A function is considered to **use** the file if:
1. It reads from or operates on this specific file (e.g., via path, file name, or known format).
2. The file's content provides necessary data or parameters for the function.
3. The file acts as a trigger or configuration for the function to run.

Examples:
- A function like `read_file("data.csv")` or `load_config("settings.json")` clearly uses the file.
- A function like `parse_json(file_content)` could use the file if the content matches.
- A function like `upload_to_cloud(file_path, user_id)` may also be using the file.

💡 Use the file's name, path, structure, and sample content to make a reasoned judgment.
⚠️ Only include functions that **directly or indirectly operate on this file**.

---

file info:
{file_info}

candidate functions:
{candidate_functions}

---

Please return your result **strictly** in the following JSON format (and nothing else):

```json
{{
    "reason": "Explain why the selected functions are likely to use this file.",
    "functions_using_file": ["func_a", "func_b"]
}}
```
'''