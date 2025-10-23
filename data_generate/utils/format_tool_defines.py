import json
import yaml
import toml
import configparser
from io import StringIO
from xml.etree.ElementTree import Element, tostring
import xml.etree.ElementTree as ET

def build_xml_element(tag, value):
    elem = Element(tag)
    if isinstance(value, dict):
        for k, v in value.items():
            child = build_xml_element(k, v)
            elem.append(child)
    elif isinstance(value, list):
        for item in value:
            child = build_xml_element("item", item)
            elem.append(child)
    else:
        elem.text = str(value)
    return elem

def indent_xml(elem, level=0):
    """递归添加缩进（不使用 minidom）"""
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        for child in elem:
            indent_xml(child, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def prettify_xml(elem):
    """缩进美化，但不带 <?xml version="1.0" ?>"""
    indent_xml(elem)
    return ET.tostring(elem, encoding='unicode')

def flatten_dict(d, parent_key='', sep='.'):
    """用于 INI：将嵌套 dict 扁平化"""
    items = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flatten_dict(v, new_key, sep=sep))
        else:
            items[new_key] = v
    return items

def format_tool_defines(tools, target_format):
    target_format = target_format.lower()
    if target_format == 'json':
        return json.dumps(tools, indent=2, ensure_ascii=False)

    if target_format == 'yaml':
        return yaml.dump(tools, allow_unicode=True, sort_keys=False)

    elif target_format == 'toml':
        return "\n\n".join([toml.dumps({"tool": [tool]}).strip() for tool in tools])

    elif target_format == 'xml':
        root = Element("tools")
        for tool in tools:
            tool_elem = build_xml_element("tool", tool)
            root.append(tool_elem)
        return prettify_xml(root)

    else:
        raise ValueError(f"Unsupported target format: {target_format}")


if __name__ == "__main__":
    json_list=[
        {"name": "live_giveaways_by_type", "description": "Retrieve live giveaways from the GamerPower API based on the specified type.", "parameters": {"type": {"description": "The type of giveaways to retrieve (e.g., game, loot, beta).", "type": "str", "default": "game"}}},
{
            "name": "create_bar_chart",
            "description": "Generate a customizable bar chart from manual input or a file (Excel, CSV, JSON, JSONL). Supports aggregation (sum, mean, count).",
            "parameters": {
                "type": "object",
                "properties": {
                    "categories": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "Categories for the x-axis if not loading from file"
                    },
                    "values": {
                        "type": "array",
                        "items": {
                            "type": "number"
                        },
                        "description": "Values corresponding to the categories if not loading from file"
                    },
                    "file_path": {
                        "type": "string",
                        "description": "Optional path to a CSV, Excel, JSON, or JSONL file to load chart data from"
                    },
                    "sheet_name": {
                        "type": [
                            "string",
                            "integer"
                        ],
                        "description": "Sheet name or index (for Excel files only)",
                        "default": 0
                    },
                    "category_col": {
                        "type": [
                            "string",
                            "integer"
                        ],
                        "description": "Column name or index for x-axis (category labels)"
                    },
                    "value_col": {
                        "type": [
                            "string",
                            "integer"
                        ],
                        "description": "Column name or index for y-axis (numeric values)"
                    },
                    "agg_method": {
                        "type": "string",
                        "enum": [
                            "sum",
                            "mean",
                            "count"
                        ],
                        "default": "sum",
                        "description": "Aggregation method if duplicate categories exist"
                    },
                    "color": {
                        "type": "string",
                        "default": "blue",
                        "description": "Color of the bars"
                    },
                    "title": {
                        "type": "string",
                        "default": "Bar Chart",
                        "description": "Title of the chart"
                    },
                    "xlabel": {
                        "type": "string",
                        "default": "Categories",
                        "description": "Label for the x-axis"
                    },
                    "ylabel": {
                        "type": "string",
                        "default": "Values",
                        "description": "Label for the y-axis"
                    },
                    "save_path": {
                        "type": "string",
                        "description": "File path to save the generated bar chart image",
                        "default": "./bar_chart.png"
                    }
                },
                "required": []
            }
        }
    ]

    print("--- JSON ---")
    print(format_tool_defines(json_list, 'json'))

    print("--- YAML ---")
    print(format_tool_defines(json_list, 'yaml'))

    print("--- XML ---")
    print(format_tool_defines(json_list, 'xml'))

    print("--- TOML ---")
    print(format_tool_defines(json_list, 'toml'))