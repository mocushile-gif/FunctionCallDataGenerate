import subprocess
import os
from dotenv import load_dotenv
load_dotenv()

def is_path_safe(command, base_dir):
    """
    检查命令中是否使用了越界路径（不允许指向 base_dir 之外）
    """
    tokens = command.split()
    for token in tokens:
        if token.startswith("./") or token.startswith(".\\"):
            # 解析绝对路径
            abs_path = os.path.abspath(os.path.join(base_dir, token))
            if not abs_path.startswith(base_dir):
                return False
        elif token.startswith("../") or token.startswith("/") or token in ['..', '/']:
            return False
    return True

def execute_linux_system_command(command):
    """
    在当前目录中安全执行 Linux 命令
    """

    try:
        cwd = os.getcwd()
        
        # 禁止危险字符（命令注入类）
        forbidden_keywords = ['&&', '|', ';', '`', '$(', '>', '<']
        if any(k in command for k in forbidden_keywords):
            return 'Failed', "Command contains unsafe shell operators."

        # 检查路径是否越界
        if not is_path_safe(command, cwd):
            return 'Failed', "Command contains unsafe paths (escaping current directory)."

        # 执行命令
        result = subprocess.run(
            command,
            shell=True,
            text=True,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        if result.returncode != 0:
            return 'Failed', f"Command failed with error:\n{result.stderr.strip()}"
        elif result.stderr.strip():
            return 'Failed', f"Standard error: {result.stderr.strip()}"

        return 'Success', result.stdout.strip()

    except FileNotFoundError as e:
        return 'Failed', f"Command not found: {command}. Error: {str(e)}"
    except Exception as e:
        return 'Failed', f"An unexpected error occurred: {str(e)}"

if __name__ == '__main__':
    # Example usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    print(execute_linux_system_command('du -h ./image_data'))
