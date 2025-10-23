
import json
import re
import os
import json
from collections import defaultdict
import random
import threading
import tempfile
from data_generate.utils.log_setting import set_main_logger
import logging
import copy
import shutil
from colorama import Fore, Style
import subprocess
import concurrent
import traceback
from tqdm import tqdm
import re
from concurrent.futures import ThreadPoolExecutor
from data_generate.agent.model.gpt import ChatGPTFunction
from data_generate.agent.model.qwq import QwQFunction
from fsp_generate.code.label_task.extract_lookup_task_answer_prompt import extract_lookup_task_answer_prompt
lock = threading.Lock()

def normalize_text(text: str) -> str:
    if not isinstance(text, str):
        text = json.dumps(text, ensure_ascii=False)
    else:
        try:
            text = json.dumps(json.loads(text), ensure_ascii=False)
        except:
            pass
    try:
        decoded = bytes(text, 'utf-8').decode('unicode_escape')
        # 将解码后的文本重新编码为utf-8来确保中文字符正确
        text = decoded.encode('latin-1').decode('utf-8')
    except:
        pass
    text = re.sub(r'\\n', ' ', text)
    text = re.sub(r'\\t', ' ', text)
    text = re.sub(r'\\+', '', text)
    text = re.sub(r'[^\w\s]', '', text)
    text = ' '.join(text.split()).lower()
    return text

def mask_to_regex(answer: str) -> str:
    # 1. 保留 <mask> 临时占位符
    placeholder = "___MASK___".lower()
    # 2. 标准化：去掉符号，转小写
    answer = normalize_text(answer)
    # 3. 将占位符替换为正则通配符
    pattern = re.escape(answer).replace(re.escape(placeholder), r".+?")
    return pattern

def match_answer(answer, task_messages):
    normalized_task_messages = ','.join([normalize_text(message) for message in task_messages])

    if '___MASK___' in answer:
        pattern = mask_to_regex(answer)
        # 使用 re.IGNORECASE 进行忽略大小写匹配
        print(pattern)
        if not re.search(pattern, normalized_task_messages, flags=re.IGNORECASE):
            return False
    else:
        normalized_answer = normalize_text(answer)
        if normalized_answer not in normalized_task_messages:
            return False

    return True

task_messages=[
        "Generate a high-complexity random password, split its characters into chunks of 3, and then validate if a given 9x9 Sudoku board is correctly formatted.",
        [
            {
                "function": {
                    "arguments": "{\"complexity\":\"high\"}",
                    "name": "generate_random_password"
                },
                "id": "call_ttqkeHVJXAF1Q7zxOR7Q8Ooq",
                "type": "function"
            }
        ],
        "\"3Ex`/#)'@['%\"",
        [
            {
                "function": {
                    "arguments": "{\"chunk_size\":3,\"lst\":[\"3\",\"E\",\"x\",\"`\",\"/\",\"#\",\")\",\"'\",\"@\",\"[\",\"'\",\"%\"]}",
                    "name": "split_list"
                },
                "id": "call_PGPbK5QPahO6N3eBGZeULOMY",
                "type": "function"
            }
        ],
        "[[\"3\", \"E\", \"x\"], [\"`\", \"/\", \"#\"], [\")\", \"'\", \"@\"], [\"[\", \"'\", \"%\"]]",
        [
            {
                "function": {
                    "arguments": "{\"board\":[[\"5\",\"3\",\".\",\".\",\"7\",\".\",\".\",\".\",\".\"],[\"6\",\".\",\".\",\"1\",\"9\",\"5\",\".\",\".\",\".\"],[\".\",\"9\",\"8\",\".\",\".\",\".\",\".\",\"6\",\".\"],[\"8\",\".\",\".\",\".\",\"6\",\".\",\".\",\".\",\"3\"],[\"4\",\".\",\".\",\"8\",\".\",\"3\",\".\",\".\",\"1\"],[\"7\",\".\",\".\",\".\",\"2\",\".\",\".\",\".\",\"6\"],[\".\",\"6\",\".\",\".\",\".\",\".\",\"2\",\"8\",\".\"],[\".\",\".\",\".\",\"4\",\"1\",\"9\",\".\",\".\",\"5\"],[\".\",\".\",\".\",\".\",\"8\",\".\",\".\",\"7\",\"9\"]]}",
                    "name": "is_valid_sudoku"
                },
                "id": "call_iOljWyaNBaniULL17ojt52AC",
                "type": "function"
            }
        ],
        "true"
    ]
answer="{\"complexity\":\"high\"}",
print(match_answer(answer, task_messages))
# print("Pie chart saved to ___MASK___ successfully.")
