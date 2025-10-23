FILE_TOOL_ENVIRONMENT="""
{file_system_info}

### Files information：
{file_info}

### Notes:
1.You can only query or issue commands based on the provided directory.
2.DO NOT provide absolute file paths directly. Instead, describe the paths using natural language.
3.Use implicit language to query, e.g., refer to files or directories in a general way.
4.If no file info you need to get, directly return the query.
5.**DO NOT assume any column name or data. Your query must be based on the following file information.**
"""