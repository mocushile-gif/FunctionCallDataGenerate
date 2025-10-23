import nltk
from nltk.tokenize import word_tokenize
from nltk.sentiment import SentimentIntensityAnalyzer
from typing import Dict, List
import os
from dotenv import load_dotenv
import nltk
from nltk.data import find
try:
    find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')
load_dotenv()

def sentiment_analysis_for_text_file(file_path: str):
    """
    读取 TXT 文件内容并执行自然语言处理（如分词、情感分析）。

    参数:
    - file_path (str): TXT 文件的路径。

    返回:
    - Dict[str, any]: 包含处理结果的字典。
    """
    # 初始化返回结果
    results = {}

    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # 情感分析
    sia = SentimentIntensityAnalyzer()
    sentiment_scores = sia.polarity_scores(text)
    results['sentiment'] = sentiment_scores

    return results

# Example usage:
if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    file_path = './txt_data/Donald Trump Rally Speeches/BattleCreekDec19_2019.txt'
    try:
        nlp_results = sentiment_analysis_for_text_file(file_path)
        print(f"Processed Text Results:\n{nlp_results}")
    except Exception as e:
        print(f"Error: {e}")
