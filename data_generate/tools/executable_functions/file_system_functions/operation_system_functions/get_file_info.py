import pandas as pd
import os
import json
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
load_dotenv()
pd.set_option('display.max_rows', None)  # Display all rows
pd.set_option('display.max_columns', None)  # Display all columns
pd.set_option('display.max_colwidth', None)
import logging
from PIL import Image
from PyPDF2 import PdfReader
os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
logger = logging.getLogger(__name__)

def read_pdf(pdf_path: str, preview_rows: int):
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
        try:
            # Extract text from first few pages for preview
            preview_pages = min(3, num_pages)  # Preview first 3 pages
            for page_num in range(preview_pages):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                if page_text:
                    # Split text into lines and filter empty lines
                    page_lines = [line.strip() for line in page_text.split('\n') if line.strip()]
                    lines.extend(page_lines)
        except Exception as e:
            lines = [f"Error extracting text: {str(e)}"]

        result ={"response":
        {
            "file_path": pdf_path,
            "total_pages": num_pages,
            "num_lines": len(lines),
            "preview": lines[:preview_rows] if lines else []
            }
        }
        
        return result

def read_image(file_path: str):
    file_size = os.path.getsize(file_path)
    file_ext = os.path.splitext(file_path)[1].lower()
    file_name = os.path.basename(file_path)
    file_dir = os.path.dirname(file_path)
    
    # Initialize result
    result = {
        "response": {
            "file_path": file_path,
            "size_bytes": file_size,
            "size_mb": round(file_size / (1024 * 1024), 2),
        }
    }
    
    # Open the image
    with Image.open(file_path) as img:
        # Basic image information
        result["response"]["image_info"] = {
            "format": img.format,
            "mode": img.mode,
            "size": img.size,
            "width": img.width,
            "height": img.height,
            "aspect_ratio": round(img.width / img.height, 3),
            "total_pixels": img.width * img.height,
            "megapixels": round((img.width * img.height) / 1000000, 2)
        }
        
        # Color information
        if img.mode in ['RGB', 'RGBA']:
            result["response"]["color_info"] = {
                "color_mode": img.mode,
                "channels": len(img.mode),
                "has_alpha": 'A' in img.mode
            }
        elif img.mode == 'L':
            result["response"]["color_info"] = {
                "color_mode": "Grayscale",
                "channels": 1,
                "has_alpha": False
            }
        else:
            result["response"]["color_info"] = {
                "color_mode": img.mode,
                "channels": "Unknown",
                "has_alpha": "Unknown"
            }
        return result

def get_file_info(file_path: str, preview_rows: int = 5):
    """
    获取文件的基本信息，包括列名、行数、列数等，支持 Excel, CSV, JSON, JSONL, TXT 格式。

    参数:
    - file_path (str): 文件路径
    - preview_rows (int, 可选): 预览的行数，默认 5 行

    返回:
    - dict: 文件信息，包括文件路径、行数、列数、列名（如果适用）
    """    
    work_dir=os.getcwd()
    logger.info('Current working dir：'+work_dir)

    # 获取文件扩展名
    file_extension = os.path.splitext(file_path)[-1].lower()

    if file_extension =='.pdf':
        return read_pdf(file_path, preview_rows)
    elif file_extension in (".jpg",'.jpeg','.png','.gif','.bmp'):
        return read_image(file_path)
    # 处理不同文件类型
    try:
        if file_extension in (".xlsx", ".xls"):
            xls = pd.ExcelFile(file_path)
            sheets_info = {}

            for sheet_name in xls.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name, header=[0, 1] if pd.read_excel(file_path, sheet_name=sheet_name, nrows=0).columns.nlevels > 1 else 0)
                lines = df.values.tolist()

                # 处理多级列名（MultiIndex）
                if isinstance(df.columns, pd.MultiIndex):
                    # 将多级列名转换成字符串，比如 ('A', 'X') -> 'A | X'
                    column_names = [' | '.join([str(level) for level in col]).strip() for col in df.columns.values]
                else:
                    column_names = df.columns.tolist()

                sheets_info[sheet_name] = {
                    "sheet_name": sheet_name,
                    "num_rows": len(df),
                    "num_columns": len(df.columns),
                    "column_names": df.columns.tolist(),
                    "preview": df.head(preview_rows).to_dict(orient="records")
                }

            return {
                "response": {
                    "file_path": file_path,
                    "sheet_names": xls.sheet_names,
                    "sheets": sheets_info
                }
            }
            
        elif file_extension == ".csv":
            encodings_to_try = ['utf-8', 'ISO-8859-1', 'GBK','gb2312']
            for encoding in encodings_to_try:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
        elif file_extension == ".parquet":
            df = pd.read_parquet(file_path)
        elif file_extension == ".json":
            df = pd.read_json(file_path)
        elif file_extension == ".jsonl":
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = [json.loads(line.strip()) for line in f]
            df = pd.DataFrame(lines)
        elif file_extension == ".txt":
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            return {
                "response": {
                    "file_path": file_path,
                    "num_lines": len(lines),
                    "preview": lines[:preview_rows]  # 预览前 `preview_rows` 行
                }
            }
        return {
            "response": {
                "file_path": file_path,
                "num_rows": len(df),
                "num_columns": len(df.columns),
                "column_names": df.columns.tolist(),
                "preview": df.head(preview_rows).to_dict(orient="records")  # 预览前 `preview_rows` 行
            }
        }

    except:
        # 格式或读取失败时退而求其次
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            return {
                "response": {
                    "file_path": file_path,
                    "num_lines": len(lines),
                    "preview": lines[:preview_rows]
                }
            }
        except PermissionError:
            return {
                "response": {
                    "file_path": file_path,
                    "info": "No permission for this file.",
                }
            }
        except (pd.errors.ParserError, pd.errors.EmptyDataError,UnicodeDecodeError,json.JSONDecodeError,ValueError) as inner_e:
            return {
                "response": {
                    "file_path": file_path,
                    "info": "Unsupported file type, no info.",
                }
            }
        except Exception as e:
            logger.error('Current working dir：'+work_dir)
            raise



# Example Usage
if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    # test_files = [
    #     # ("./csv_data/netflix_movies_and_tv_shows.csv", 3),
    #     ("/mnt/afs2/qinxinyi/function_call_data/data_generate/working_dir/file_system_new/excel_data/Global Superstore Orders 2016.xlsx",10),
    #     # ("/mnt/afs2/qinxinyi/function_call_data/data_generate/working_dir/file_system_new/yellow_tripdata_2023-02.parquet", 3),
    #     # ("./image_data/dog.jpg",10)
    #     # ("./csv_data/Chocolate Sales.csv", 10),
    #     # ("./json_data/Books.json", 5),
    #     # ("./json_data/mental_health_counseling_conversations.jsonl", 2),
    #     # ("./txt_data/Friends TV Show Script.txt", 7)
    #     # ("./csv_data/2017 Kaggle Machine Learning & Data Science Survey/multipleChoiceResponses.csv",1),
    #     # ("/mnt/afs2/qinxinyi/function_call_data/data_generate/working_dir/shangtang/学生成绩表_多表.xlsx",10)
    # ]

    # for file_path, preview_rows in test_files:
    #     print(f"\n📄 File: {file_path} (Preview {preview_rows} rows)")
    #     result = get_file_info(file_path, preview_rows)
    #     print("File Information:", json.dumps(result, indent=2, ensure_ascii=False,default=str))

    arguments={"file_path":"./pdf_data/order.pdf"}
    print(get_file_info(**arguments))
    # print(read_pdf("./pdf_data/order.pdf"))