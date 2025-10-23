import re
from typing import List, Dict
from collections import Counter
import os
from dotenv import load_dotenv
load_dotenv()

def extract_patterns_from_text(file_path: str, patterns: List[str], limit: int = None):

    """
    从文本文件中提取正则匹配项，并统计每个模式下每个匹配值出现的次数。

    参数:
    - file_path (str): 文本文件路径。
    - patterns (List[str]): 正则表达式列表。
    - limit (int): 每个模式返回最多多少个不同匹配值（按频率排序）。

    返回:
    - Dict[str, Dict]: 包含每个模式的总匹配次数和每个匹配项的出现次数。
    """

    results = {}

    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    for pattern in patterns:
        matches = re.findall(pattern, text)
        counter = Counter(matches)
        sorted_matches = dict(counter.most_common(limit)) if limit else dict(counter)

        results[pattern] = {
            "total": sum(counter.values()),
            "matches": sorted_matches
        }

    total_all = sum(v["total"] for v in results.values())
    return f"Total {total_all} matches found across all patterns.", results


# Example usage:
if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    file_path = './txt_data/Harry Potter Books/05 Harry Potter and the Order of the Phoenix.txt'
    patterns = [
        "\d{4}",# 匹配日期 "YYYY-MM-DD"
        r"1"# 匹配百分比 例如"50%" 
    ]
    try:
        extracted_data = extract_patterns_from_text(file_path, patterns, limit=10)
        print(extracted_data)
    except Exception as e:
        print(f"Error: {e}")
