import os
from dotenv import load_dotenv
import pandas as pd  # 用于读取 Excel 和 CSV 文件
import json  # 用于解析 JSON 和 JSONL 文件
from typing import Dict, Any, Optional, List
import base64
from PIL import Image
import requests
from PyPDF2 import PdfReader
load_dotenv()

def read_pdf(pdf_path: str,start=0, end=None):
    """
    Read PDF file and extract text content and metadata.

    Parameters:
    - pdf_path (str): Path to the input PDF file.

    Returns:
    - dict: Processing result information including extracted text and metadata.
    """
    
    with open(pdf_path, 'rb') as file:
        pdf_reader = PdfReader(file)
        num_pages = len(pdf_reader.pages)

        # Extract text for preview
        lines = []
        # Extract text from first few pages for preview
        preview_pages = min(3, num_pages)  # Preview first 3 pages
        for page_num in range(preview_pages):
            page = pdf_reader.pages[page_num]
            page_text = page.extract_text()
            if page_text:
                # Split text into lines and filter empty lines
                page_lines = [line.strip() for line in page_text.split('\n') if line.strip()]
                lines.extend(page_lines)

        if lines:
            return "".join(lines[start:end])
        else:
            return []

def describe_image(image_path, max_tokens=300, 
                   detail_level="auto", language="en", include_metadata=True):
    """
    Generate a detailed description of an image using Zhipu AI GLM-4V vision models.
    
    Args:
        image_path (str): Path to the input image file
        max_tokens (int): Maximum number of tokens for the description
        detail_level (str): Detail level - "low", "high", "auto"
        language (str): Language for the description
        include_metadata (bool): Whether to include image metadata
    
    Returns:
        dict: Result information including success status and description
    """
    
    
    try:
        # Validate input file
        if not os.path.exists(image_path):
            return {
                "success": False,
                "error": f"Image file not found: {image_path}"
            }
        
        # Get image metadata
        metadata = {}
        if include_metadata:
            try:
                with Image.open(image_path) as img:
                    metadata = {
                        "format": img.format,
                        "mode": img.mode,
                        "size": f"{img.width}x{img.height}",
                        "width": img.width,
                        "height": img.height
                    }
                    
                    # Get file size
                    file_size = os.path.getsize(image_path)
                    metadata["file_size_bytes"] = file_size
                    metadata["file_size_mb"] = round(file_size / (1024 * 1024), 2)
                    
            except Exception as e:
                metadata["error"] = f"Failed to get metadata: {str(e)}"
        
        # Try different description methods
        description_result = _try_zhipu_vision(image_path, max_tokens, detail_level, language)
        
        # Combine results
        result = {
            "image_path": image_path,
            "description": description_result.get("description", ""),
        }
        
        if include_metadata:
            result["metadata"] = metadata
        
        if description_result.get("tags"):
            result["tags"] = description_result["tags"]
        
        if description_result.get("objects"):
            result["objects"] = description_result["objects"]
        
        return {"response":result}
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error describing image: {str(e)}"
        }

def _try_zhipu_vision(image_path, max_tokens, detail_level, language):
    """
    Use Zhipu GLM-4V API to describe an image, with prompt dynamically adjusted by detail_level and max_tokens.
    
    Parameters:
    - image_path (str): Path to the image file
    - max_tokens (int): Max response tokens AND used in prompt as soft constraint
    - detail_level (str): One of "low", "high", "auto"
    - language (str): Output language (e.g., "zh", "en", "ja")
    
    Returns:
    - dict: {success: bool, content or error}
    """
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        return {"success": False, "error": "ZHIPU_API_KEY not found in environment variables"}

    try:
        with open(image_path, "rb") as f:
            image_base64 = base64.b64encode(f.read()).decode("utf-8")
    except Exception as e:
        return {"success": False, "error": f"Failed to read image: {e}"}

    def build_prompt(detail_level, language, max_tokens):
        token_limit_note = f"（不超过 {max_tokens} 个 token）" if language == "zh" else f"(no more than {max_tokens} tokens)"
        if language == "zh":
            if detail_level == "low":
                return f"请简要描述这张图片的内容。{token_limit_note}"
            elif detail_level == "high":
                return f"请尽可能详细地描述这张图片的内容，包括主要物体、颜色、背景、情绪和任何可见细节。{token_limit_note}"
            else:  # auto
                return f"请描述这张图片的内容，包括主要对象、颜色、构图和显著特征。{token_limit_note}"
        else:
            if detail_level == "low":
                return f"Briefly describe this image. {token_limit_note}"
            elif detail_level == "high":
                return f"Describe this image in as much detail as possible, including objects, colors, background, emotion, and notable features. {token_limit_note}"
            else:
                return f"Please describe this image, focusing on main subjects, color, layout, and key features. {token_limit_note}"

    prompt_text = build_prompt(detail_level, language, max_tokens)

    payload = {
        "model": "glm-4v-flash",
        "max_tokens": max_tokens,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}},
                    {"type": "text", "text": prompt_text}
                ]
            }
        ]
    }

    response = requests.post(
        "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        },
        data=json.dumps(payload)
    )
    result = response.json()
    return {"success": True, "description": result["choices"][0]["message"]["content"]}


def read_file_contents(file_path, start=0, end=None, column_names=[], sheet_name: str or int =0):
    """
    读取文件内容并返回字符串、JSON、JSONL 或 DataFrame，支持文本和表格文件。
    支持 .txt, .json, .jsonl, .xlsx, .xls, .csv 文件类型，并允许通过 `start` 和 `end` 限制读取范围。

    参数:
    - file_path (str): 文件路径。
    - start (int): 起始行或字符索引（默认 0）。
    - end (int): 结束行或字符索引（默认为 None，表示读取所有内容）。
    - column_names (list): 
    - sheet_name (str): 

    返回:
    - 文本文件返回字符串。
    - JSON / JSONL 返回字典或列表。
    - 表格文件返回 DataFrame。
    - 发生错误时返回错误消息。
    """

    # 获取文件扩展名
    file_extension = os.path.splitext(file_path)[1].lower()

    # 处理文本文件 (.txt, .json, .jsonl)
    if file_extension == '.pdf':
        return read_pdf(file_path,start,end)
    if file_extension in (".jpg",'.jpeg','.png','.gif','.bmp'):
        return describe_image(file_path,max_tokens=200, detail_level="auto", language="en")
    if file_extension in ['.txt', '.json', '.jsonl','md']:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()  # 读取所有行

        # 处理 JSONL 文件
        if file_extension == '.jsonl':
            parsed_lines = [json.loads(line.strip()) for line in lines[start:end]]
            return parsed_lines

        # 处理 JSON 文件
        elif file_extension == '.json':
            parsed_content = json.loads("".join(lines))
            if isinstance(parsed_content, list):
                return parsed_content[start:end]  # 适用于列表 JSON
            elif isinstance(parsed_content, dict):
                keys = list(parsed_content.keys())[start:end]
                return {key: parsed_content[key] for key in keys}
            else:
                return f"Error: Unsupported JSON structure in file '{file_path}'."

        # 处理普通文本文件
        return "".join(lines[start:end])

    # 处理 Excel / CSV 文件 (.xlsx, .xls, .csv)
    elif file_extension in ['.xlsx', '.xls','.csv']:
        if file_extension == '.csv':
            encodings_to_try = ['utf-8', 'ISO-8859-1', 'GBK','gb2312']
            for encoding in encodings_to_try:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue

        else:
            df = pd.read_excel(file_path, sheet_name=sheet_name)

        # 适配 Pandas 的 DataFrame 切片
        pd.set_option('display.max_rows', None)  # Display all rows
        pd.set_option('display.max_columns', None)  # Display all columns


        if column_names:
            for column in column_names:
                if column not in list(df.columns):
                    return f"Error: does not have column '{column}'."
            df = df[column_names]
        return df.iloc[start:end]  # 返回 start 到 end 之间的行数据

    else:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()  # 读取所有行
            return "".join(lines[start:end])
        except:
            return f"Error: Unsupported file type '{file_extension}'."

# Example Usage
if __name__ == '__main__':
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    test_files = [
        # ("./excel_data/BikeBuyers_Data.xlsx", 0, 3),
        # ("./csv_data/Chocolate Sales.csv", 2, 10),
        # ("./json_data/Books.json", 1, 5),
        # ("./json_data/mental_health_counseling_conversations.jsonl", 2, 5),
        # ("./txt_data/Friends TV Show Script.txt", 7, 11),
        # ("./pdf_data/order.pdf", 0, 100),
        ("./image_data/dog.jpg", 0, 100)
    ]

    for file_path, start, end in test_files:
        print(f"\n📄 File: {file_path} (Rows {start} to {end})")
        result = read_file_contents(file_path, start=start, end=end)
        print(result)


    # file_path = f"{os.environ['HOME_DIR']}/function_call_data/data_generate/working_dir/file_system_new/output/nextjs_repository_page.md"
    sheet_name="OrderBreakdown"
    column_name = "Quantity"
    # result = read_file_contents("./excel_data/BikeBuyers_Data.xlsx", 0, 100,["Income"])
    # result = read_file_contents(file_path, 0, 100,[column_name],sheet_name)
    # result = read_file_contents("./csv_data/TED Talks.csv", 50, 100,["title"])
    # result = read_file_contents("./pdf_data/order.pdf", 0, 100)
    print(result)