import os
import json
import re
import pandas as pd
from jupyter_client import KernelManager
from dotenv import load_dotenv
load_dotenv()

import logging
logger = logging.getLogger(__name__)
# 工具方法
def clean_traceback(tb: str):
    arr = []
    for line in tb:
        line = re.sub(r"\x1b\[.*?m", "", line)
        arr.append(line)
    return "\n".join(arr)

def exec_block(client, code):
    msg_id = client.execute(code)
    outputs = []
    while True:
        msg = client.get_iopub_msg(timeout=180)
        if "parent_header" not in msg or "msg_id" not in msg["parent_header"]:
            continue

        if msg["parent_header"]["msg_id"] == msg_id:
            msg_type = msg["msg_type"]

            if msg_type in ["execute_result", "stream", "display_data", "error"]:
                outputs.append(msg)
            elif msg_type == "status" and msg["content"]["execution_state"] == "idle":
                break
    return outputs

def get_jupyter_result(kc, code: str):
    print_output = ""
    execution_output = ""
    for msg in exec_block(kc, code):
        msg_type = msg.get("msg_type", "")
        if msg_type == "stream":
            content = msg.get("content", {}).get("text", "")
            if "ipykernel" in content:
                continue
            print_output += content

        elif msg_type in ["display_data", "execute_result"]:
            data = msg.get("content", {}).get("data", {})
            text_content = data.get("text/plain", "")
            image_content = data.get("image/png", None)
            if image_content:
                execution_output="<<ImageDisplayed>>"
            elif text_content:
                execution_output = text_content

        elif msg_type == "error":
            traceback = clean_traceback(msg.get("content", {}).get("traceback", []))
            return traceback, 500

    # 最后统一组织返回
    combined_output = ""
    if print_output:
        combined_output += print_output
    if execution_output:
        if combined_output:
            combined_output += "\n"  # print 和执行结果之间加换行
        combined_output += execution_output

    return combined_output, 200

import concurrent.futures

# 会话类
class CodeInterpreterSession:
    def __init__(self,work_dir=None):
        self.work_dir=work_dir if work_dir else os.environ['FILE_SYSTEM_PATH']
        logger.info(f"[Init] code_interpreter 工作路径：{self.work_dir}")
        self._start_kernel()
        self.code_block_count = 0
        
    def _start_kernel(self):
        self.km = KernelManager()
        self.km.start_kernel(cwd=self.work_dir)
        self.kc = self.km.client()
        self.kc.start_channels()
        self.kc.wait_for_ready()
        self.code_block_count = 0
        
        # 初始化，设置字体
        self._run("""
from matplotlib import rcParams
rcParams['font.sans-serif'] = ['Noto Sans CJK JP']  # 中文字体
rcParams['axes.unicode_minus'] = False  # 防止负号显示为方块""")


    def _run(self, code: str, timeout_sec=30, retry_count=1):
        def exec_wrapper():
            return get_jupyter_result(self.kc, code)

        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(exec_wrapper)
                res, status_code = future.result(timeout=timeout_sec)

        except concurrent.futures.TimeoutError:
            logger.info(f"[Timeout] Execution timed out after {timeout_sec} seconds. Restarting kernel and retrying...")
            if retry_count <= 0:
                raise TimeoutError(f"[Timeout] Execution timed out after {timeout_sec} seconds.")
            self._restart_kernel()
            return f"[Timeout] Execution timed out. Restarting kernel...\n\n" + self._run(code, timeout_sec, retry_count - 1)

        except Exception as e:
            logger.error("[Error] Execution exception:", e)
            raise

        self.code_block_count += 1
        if status_code != 200:
            raise Exception(f"Code execution failed: {res}")

        return f"Out[{self.code_block_count}]:\n{res}"

    def _restart_kernel(self):
        self._close()
        self._start_kernel()
        self.code_block_count = 0

    def is_kernel_alive(self):
        return self.km.is_alive()

    def _close(self):
        self.kc.shutdown()
        self.km.shutdown_kernel()
        logger.info('code session shutdowned.')

# 兼容原来的单步接口
def code_intepreter(code):
    session = CodeInterpreterSession()
    result = session._run(code)
    session._close()
    return result


if __name__ == '__main__':
# from code_intepreter_session import CodeInterpreterSession
    import logging

    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] [%(levelname)s] [Thread:%(threadName)s - %(thread)d]\n%(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger = logging.getLogger(__name__)

    # 新建一个会话
    session = CodeInterpreterSession()
    print(session.work_dir)
    # 多步执行
    print(session._run("""
    a = 10
    b = 20
    c=30
    b
    """))

    print(session._run("""
    import pandas as pd
    df=pd.read_csv('./csv_data/Chocolate Sales.csv')
    df.head()
    """))

    print(session._run("""
    df.columns
"""))

    # 结束会话
    session._close()
