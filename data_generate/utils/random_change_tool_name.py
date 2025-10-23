import random

def to_camel_case(s):
    """Converts snake_case to camelCase."""
    if '_' in s:
        parts = s.split('_')
    elif ' ' in s:
        parts = s.split(' ')
    elif '-' in s:
        parts = s.split('-')
    return parts[0] + ''.join(x.capitalize() for x in parts[1:])

def to_pascal_case(s):
    """Converts snake_case to PascalCase."""
    if '_' in s:
        parts = s.split('_')
    elif ' ' in s:
        parts = s.split(' ')
    elif '-' in s:
        parts = s.split('-')
    return ''.join(x.capitalize() for x in parts)

def to_snake_case(s):
    """Ensures snake_case format (lowercase with underscores)."""
    return s.lower().replace("-", "_").replace(" ", "_")

def to_space_case(s):
    """Ensures snake_case format (lowercase with spaces)."""
    return s.lower().replace("-", " ").replace("_", " ")

def to_kebab_case(s):
    """Converts to kebab-case (lowercase with hyphens)."""
    return s.lower().replace(" ", "-").replace("_", "-")

def to_upper_case(s):
    """Converts to UPPER_CASE."""
    return s.upper()

def to_lower_case(s):
    """Converts to lowercase."""
    return s.lower()

def to_capitablize(s):
    return s.capitalize()

def keep_original(s):
    return s


def generate_random_tool_name(category, tool_name, api_name):
    """
    Generates a diverse tool name variation using category, tool_name, and api_name.

    Parameters:
    - category (str): Main category of the tool (e.g., 'eCommerce').
    - tool_name (str): Tool name, sometimes the same as api_name.
    - api_name (str): API function name.

    Returns:
    - str: A randomly generated tool name variation.
    """
    if category=='file_system_functions':
        category=random.choice([
            "file_system_functions", "file_related_tools",
            "filesystem_management", "file_system_tools",
            "file_system_operations","FileSystem","fileSystem"
        ])
        if tool_name=='file_operation_functions':
            tool_name=random.choice(["file_ops", "file_io_tools", "file_tasks", 
            "file_management_tools", "file_actions", "file_handlers"]
            )
        elif tool_name=='file_statistics_functions':
            tool_name=random.choice(["file_metrics", "file_insights", 
            "file_stats_tools", "file_analysis", 
            "file_summary_tools", "file_data_stats"
        ])
        elif tool_name=='operation_system_functions':
            tool_name=random.choice(["os_utilities","system_admin_tools","system_operations",
                    "os_tools","os_functions","system_utils",
                    "sys_control","os_management",
                ])
    elif category=='database_functions':
        category=random.choice([
            "database_functions", "db_operations", "query_utilities",
            "sql_queries", "data_manipulation_functions", "relational_db_functions",
            "query_execution_functions", "data_retrieval_functions"
        ])
    elif category=='python_functions':
        category=random.choice([
            "python_utilities", "py_helpers", "built_in_python_functions",
            "python_toolkit", "python_library_functions", "py_standard_lib",
            "python_core_functions", "python_scripting_helpers"
        ])

    # Naming styles for variety
    naming_styles = [
        to_camel_case,   # camelCase
        to_pascal_case,  # PascalCase
        to_snake_case,   # snake_case
        to_kebab_case,   # kebab-case
        to_space_case,   # space case
        to_upper_case,   # UPPER_CASE
        to_lower_case,    # lowercase
    ]

    case_styles = [
        to_upper_case,   # UPPER_CASE
        to_lower_case,    # lowercase
        to_capitablize,
        keep_original
    ]

    # Randomly format inputs
    if any([sym in category for sym in ['_','-',' ']]):
        formatted_category = random.choice(naming_styles)(category)
    else:
        formatted_category = random.choice(case_styles)(category)
    
    if any([sym in tool_name for sym in ['_','-',' ']]):
        formatted_tool = random.choice(naming_styles)(tool_name)
    else:
        formatted_tool = random.choice(case_styles)(tool_name)
    
    if any([sym in api_name for sym in ['_','-',' ']]):
        formatted_api = random.choice(naming_styles)(api_name)
    else:
        formatted_api = random.choice(case_styles)(api_name)
    
    separator = random.choices([".", "/"],weights=[0.8,0.2])[0]

    # If tool_name and api_name are identical, only combine category & api_name
    if tool_name == api_name:
        possible_structures = [
            f"{formatted_api}",
            f"{formatted_category}{separator}{formatted_api}"
        ]
    else:
        possible_structures = [
            f"{formatted_api}",
            f"{formatted_category}{separator}{formatted_api}",
            f"{formatted_category}{separator}{formatted_tool}{separator}{formatted_api}",
            f"{formatted_tool}{separator}{formatted_api}"
        ]
    
    return random.choice(possible_structures)

# Example Usage
if __name__ == "__main__":
    test_cases = [
        ("file_system_functions","fetch_url","fetch_url"),
        ("file_system_functions","file_statistics_functions","anova_test"),
        ("eCommerce", "aliexpress_datahub", "aliexpress_item_search_2"),
        ("ShoppingAPI", "AliExpress_Search", "AliExpressItemSearch2"),
        ("Marketplace", "product_finder", "product_finder"),  # Identical tool_name and api_name
        ("org.marketplace", "data_provider", "search_service"),
        ("tech.aliexpress", "AliexpressDatahub", "AliexpressItemSearch2")
    ]

    for _ in range(10):  # Generate multiple variations
        category, tool_name, api_name = random.choice(test_cases)
        print(generate_random_tool_name(category, tool_name, api_name))
