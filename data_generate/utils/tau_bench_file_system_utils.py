import json
from datetime import datetime, timedelta
import sys
import os
import shutil
import random
from colorama import Fore, Style
from data_generate.utils.get_tau_bench_file_info import get_tau_bench_file_info
import logging
logger = logging.getLogger(__name__)

class TauBenchFileSystem():
    def __init__(self,debug=False):
        self.debug=debug

    def get_file_info(self,file_path,work_dir):
        file_infos=get_tau_bench_file_info(file_path,10,work_dir)['response']
        file_infos_list=[]
        for file_info in file_infos:
            file_info=str(file_info)
            if len(file_info)>4096:
                file_infos_list.append(file_info[:4096]+'...truncated.')
            else:
                file_infos_list.append(file_info)
        return file_infos_list

    def get_file_system_info_list(self,file_system_path):
        file_system_info_list=[]
        # 遍历文件系统目录及其所有子目录
        for root, dirs, files in os.walk(file_system_path):
            for name in files:
                relative_path = os.path.relpath(os.path.join(root, name), file_system_path)
                file_infos = self.get_file_info(relative_path, file_system_path)
                for file_info in file_infos:
                    file_system_info_list.append({
                        "role": "user",
                        "content": file_info
                    })
        return file_system_info_list

if __name__ == "__main__":
    system=TauBenchFileSystem()
    # print(system.extract_random_files(f'{os.environ["PROJECT_DIR"]}/agent/working_dir/shangtang_file_system',f'{os.environ["PROJECT_DIR"]}/agent/working_dir/shangtang_file_system',5))
    print(system.get_file_system_info_list(f'{os.environ["PROJECT_DIR"]}/working_dir/tau_bench')[1])
