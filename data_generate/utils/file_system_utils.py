import json
from datetime import datetime, timedelta
import sys
import os
import shutil
import random
from colorama import Fore, Style
from data_generate.utils.display_directory_tree import display_directory_tree
from data_generate.utils.get_file_info import get_file_info
import logging
logger = logging.getLogger(__name__)

class FileSystem():
    def get_file_system_info(self,file_system_path,work_dir):
        file_system_info=display_directory_tree(file_system_path,depth=5,work_dir=work_dir)
        return file_system_info

    def get_file_info(self,file_path,work_dir):
        file_info=str(get_file_info(file_path,10,work_dir)['response'])
        file_info=str(file_info['response']) if 'response' in file_info and type(file_info) is dict else str(file_info)
        if len(file_info)>4096:
            file_info=file_info[:4096]+'...truncated.'
        return file_info

    def get_file_system_info_list(self,file_system_path):
        file_system_info_list=[]
        file_system_info=self.get_file_system_info('./',file_system_path)
        file_system_info_list.append({"role":"user","content":f"""File System Environment Information:
    The default file working path is: './'
    ###Directory Structure:
    {file_system_info}
    """})
        logger.info(f'{Fore.MAGENTA}Selected Files:{Style.RESET_ALL} {Fore.WHITE}{file_system_info}{Style.RESET_ALL}')
        # 遍历文件系统目录及其所有子目录
        for root, dirs, files in os.walk(file_system_path):
            for name in files:
                relative_path = os.path.relpath(os.path.join(root, name), file_system_path)
                try:
                    file_info = self.get_file_info(relative_path, file_system_path)
                    file_system_info_list.append({
                        "role": "user",
                        "content": file_info
                    })
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    logger.error(f'{Fore.RED}Failed to get file info{Style.RESET_ALL} {Fore.WHITE}{str(e)}{Style.RESET_ALL}')
                    continue
        return file_system_info_list

    def extract_random_files(self, file_system_path, temp_file_system_path, num_files=None, ratio=None):
        """
        从 file_system_path 中随机挑选部分文件，复制到 temp_file_system_path。
        
        :param temp_file_system_path: 临时目标文件夹
        :param num_files: 指定挑选多少个文件
        :param ratio: 按比例挑选，比如0.1就是10%
        """
        all_files = []
        # 遍历整个目录树，收集所有文件
        for root, dirs, files in os.walk(file_system_path):
            for file in files:
                full_path = os.path.join(root, file)
                all_files.append(full_path)

        if not all_files:
            raise ValueError("No files found to copy.")

        # 决定选多少个
        if ratio is not None:
            num_files = max(1, int(len(all_files) * ratio))
        elif num_files is None:
            raise ValueError("You must specify either num_files or ratio.")

        num_files = min(num_files, len(all_files))  # 不超过总文件数
        selected_files = random.sample(all_files, num_files)

        # 清空 temp_file_system_path
        if os.path.exists(temp_file_system_path):
            shutil.rmtree(temp_file_system_path)
        os.makedirs(temp_file_system_path, exist_ok=True)

        # 复制选中的文件，保留相对目录结构
        final_files=[]
        for src_path in selected_files:
            rel_path = os.path.relpath(src_path, file_system_path)
            dest_path = os.path.join(temp_file_system_path, rel_path)
            final_files.append(rel_path)

            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.copy2(src_path, dest_path)  # copy2保留文件属性

        return final_files  # 返回实际复制的文件清单

if __name__ == "__main__":
    import logging
    logger = logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] [%(levelname)s] [Thread:%(threadName)s - %(thread)d]\n%(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger = logging.getLogger(__name__)

    system=FileSystem()
    # print(system.extract_random_files(f'{os.environ["PROJECT_DIR"]}/agent/working_dir/shangtang_file_system',f'{os.environ["PROJECT_DIR"]}/agent/working_dir/shangtang_file_system',5))
    print(system.get_file_system_info_list(f'{os.environ["PROJECT_DIR"]}/working_dir/file_system_new/pdf_data')[1])
    # print(system.get_file_system_info_list(f'{os.environ["HOME_DIR"]}/function_call_data_temp/function_call_file_system_var_140615300822784/tmpwdt8cp3b'))
