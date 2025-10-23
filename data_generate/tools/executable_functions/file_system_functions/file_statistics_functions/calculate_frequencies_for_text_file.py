from collections import Counter
from typing import Tuple, Dict, List, Optional
import os
from dotenv import load_dotenv
load_dotenv()

def calculate_frequencies_for_text_file(
    file_path: str, 
    word_list: Optional[List[str]] = None, 
    char_list: Optional[List[str]] = None,
    case_sensitive: bool = False,
    limit: Optional[int] = 10):
    """
    计算文本文件中单词频率和字符频率，可选择过滤特定单词或字符。

    参数:
    - file_path (str): 文本文件路径。
    - limit (int, optional): 限制返回的高频单词或字符数量，默认为 None（不限制）。
    - word_list (List[str], optional): 指定要统计的单词列表，默认为 None（统计所有单词）。
    - char_list (List[str], optional): 指定要统计的字符列表，默认为 None（统计所有字符）。

    返回:
    - Tuple[Dict[str, int], Dict[str, int]]: 包括单词频率和字符频率的字典。
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()

    # 清理文本，转为小写
    if not case_sensitive:
        cleaned_text = ''.join(c.lower() if c.isalnum() or c.isspace() else c for c in text)
    else:
        cleaned_text = text


    # 分割单词
    words = cleaned_text.split()

    # 计算词频
    word_counts = Counter(words)
    if word_list:
        word_counts = {word: word_counts[word] if word in word_counts else 0 for word in word_list}

    # 计算字符频率
    char_counts = Counter(cleaned_text.replace(' ', ''))  # 去掉空格后统计字符
    if char_list:
        char_counts = {char: char_counts[char] if char in char_counts else 0 for char in char_list}
    
    if not char_list and not word_list:
        # 限制高频结果数量
        word_counts = dict(Counter(word_counts).most_common(limit))
        char_counts = dict(Counter(char_counts).most_common(limit))

    result=''
    if word_list or (not char_list and not word_list):
        result+=f"Word frequencies:\n"
        for word, freq in word_counts.items():
            result+=f"{word}: {freq}\n"
    
    if char_list or (not char_list and not word_list):
        result+=f"Character frequencies:\n"
        for char, freq in char_counts.items():
            result+=f"{char}: {freq}\n"
    return result

# 使用示例
if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    file_path = './txt_data/birth_rate_and_life_expectancy_2010.txt'
    limit = 10  # 限制返回的高频结果数量
    word_list = []  # 要统计的单词列表
    # char_list = ['e', 'a', 't']  # 要统计的字符列表

    result = calculate_frequencies_for_text_file(file_path,word_list=word_list)
    print({'result':result})
    # import json
    # with open('/mnt/nvme0/qinxinyi/function_call_data/data_generate/tools/defines/file_system_functions/calculate_frequencies_for_text_file.json','r',encoding='utf-8') as f:
    #     print(json.load(f))