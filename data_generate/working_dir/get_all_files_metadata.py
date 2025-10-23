import json
from datetime import datetime, timedelta
import sys
import os
import shutil
import random
from colorama import Fore, Style
from data_generate.utils.get_file_info import get_file_info


file_infos={}
project_dir=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
file_system_path=f'{project_dir}/working_dir/file_system_new'
for root, dirs, files in os.walk(file_system_path):
    for name in files:
        relative_path = os.path.relpath(os.path.join(root, name), file_system_path)
        file_info = get_file_info(relative_path, 3, file_system_path)['response']
        file_infos[relative_path]=file_info

with open(f'{project_dir}/working_dir/all_files_metadata.json','w',encoding='utf-8') as out_f:
    json.dump(file_infos,out_f,ensure_ascii=False,indent=4)

