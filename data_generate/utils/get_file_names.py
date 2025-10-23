
import os
import shutil
import json
import sys

def get_file_names(folder_path):
    """
    获取指定文件夹下的所有文件名
    :param folder_path: 文件夹路径
    :return: 文件名列表
    """
    try:
        # 获取文件夹下的所有文件名
        file_names = [os.path.join(folder_path,file_name) for file_name in os.listdir(folder_path)]
        return file_names
    except Exception as e:
        print(f"Error reading folder: {e}")
        return []