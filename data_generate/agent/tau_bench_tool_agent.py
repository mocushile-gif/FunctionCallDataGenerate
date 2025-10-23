import sys
import os
from pydantic import BaseModel,Field, SecretStr, model_validator
import json
from typing import List, Dict, Any, Optional, Union
from langchain_core.utils import get_from_dict_or_env, convert_to_secret_str
from colorama import Fore, Style
import time
import base64
from mimetypes import guess_type
import re
import inspect
import threading
import traceback
import pandas as pd
from dotenv import load_dotenv
from data_generate.agent.model import *
from dotenv import load_dotenv
import importlib
import logging
load_dotenv()

lock = threading.Lock()
load_dotenv()
pd.set_option('display.max_rows', None)  # Display all rows
pd.set_option('display.max_columns', None)  # Display all columns
pd.set_option('display.max_colwidth', None)

import logging
logger = logging.getLogger(__name__)

class ToolAgent(BaseModel):
    description: str= ("tool_agent")
    file_system_path: str = os.environ['TAU_BENCH_DATA_PATH']
    llm: Union[DOUBAOFunction, ChatGPTFunction,QWen25Function] = Field(default=None)
    llm_name: str = 'gpt4o-ptu-client'
    tools: Dict= Field(default=None)
    tool_modules: Dict= {}

    class Config:
        arbitrary_types_allowed = True

    @model_validator(mode='after')
    def validate_environment(self):
        if 'gpt' in self.llm_name:
            self.llm = ChatGPTFunction(name='gpt4o-ptu-client')
        elif 'doubao' in self.llm_name:
            self.llm = DOUBAOFunction()
        elif 'qwen' in self.llm_name:
            self.llm = QWen25Function(args={'temperature': 0.7})
        elif 'qwq' in self.llm_name:
            self.llm = QwQFunction(args={'temperature': 0.7})
        elif 'deepseek' in self.llm_name:
            self.llm = Deepseek25Function(args={'temperature': 0.7})
        else:
            raise NameError('not support')
        
        for tool in self.tools.keys():
            module=importlib.import_module(f'data_generate.tools.{tool}')
            self.tool_modules[tool.split('.')[-1]]=module
        return self

    def _run(self,assistant_message: Dict[str, Any]) -> List[Dict[str, Any]]:
        tool_calls = assistant_message.get("tool_calls", [])
        results = []

        for call in tool_calls:
            tool_data = call.get("function", {})
            tool_name = tool_data.get("name")
            arguments = tool_data.get("arguments", "{}")
            
            try:
                arguments = json.loads(arguments) if type(arguments) is str else arguments
            except:
                results.append({"role": "tool", "content": {'status':'failed','message':"Cannot decode the arguments, please check and regenerate."},"tool_call_id":call['id']})

            if tool_name in self.tool_modules:
                try:
                    # 获取函数签名
                    func = getattr(self.tool_modules[tool_name], tool_name)
                    # 检查函数是否具有 'tool_agent' 参数
                    func_signature = inspect.signature(func)
                    if 'tool_agent' in func_signature.parameters:
                        #把data传给函数，self.data会随之改变
                        new_arguments = {**arguments, "tool_agent": self}
                        result=func(**new_arguments)
                    else:
                        new_arguments = arguments
                        result=func(**new_arguments)
                    
                    if len(str(result))>8192:
                        result=str(result)[:8192]+'...truncated.'
                        results.append({"role": "tool","content": str(result),"tool_call_id":call['id']})
                    else:
                        results.append({"role": "tool","content": result,"tool_call_id":call['id']})
                except Exception as e:
                    logger.warning(f'{Fore.RED}TOOL {tool_name} ERROR at Tool {tool_name}: {str(e)[:4096]}{Style.RESET_ALL}')
                    logger.warning(f'{Fore.RED}TOOL {tool_name} Tool call: {call}{Style.RESET_ALL}')
                    logger.warning(traceback.format_exc())
                    results.append({"role": "tool", "content": {'status':'failed','message':f'Tool "{tool_name}" Error: '+str(e)[:4096]},"tool_call_id":call['id']})

            else:
                results.append({"role": "tool","content": {'status':'failed','message':f"Unsupported tool: {tool_name}."},"tool_call_id":call['id']})
        
        for result in results:
            if len(str(result['content']))>8192:
                result['content']=str(result)[:8192]+'...truncated.'
        for i,result in enumerate(results):
            logger.info(f'{Fore.MAGENTA}TOOL RESPONSE {i}:{Style.RESET_ALL} {Fore.WHITE}{result}{Style.RESET_ALL}')
        return results

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] [%(levelname)s] [Thread:%(threadName)s - %(thread)d]\n%(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger = logging.getLogger(__name__)
    from data_generate.utils import load_tool_defines
    tools=load_tool_defines(f'{os.environ["PROJECT_DIR"]}/tools/defines/tau_bench',recursive=True)

    # # code_intepreter
    tool_agent = ToolAgent(
            file_system_path=f'{os.environ["PROJECT_DIR"]}/working_dir/tau_bench',
            tools=tools
        )
    assistant_messages={"role": "assistant", "tool_calls": [{"function": {"arguments": 
                    {"order_id": "#W1504875",
                    "item_ids": ["9421195098"],
                    "new_item_ids": ["9799386954"],
                    "payment_method_id": "paypal_6262583"}, "name": "exchange_delivered_order_items"}, "id": "call_rpLCy1u3yvMG8LbAypAToGcu", "type": "function"}]}
    assistant_messages={"role": "assistant", "tool_calls": [{
            "function": {
              "arguments": "{\"reservation_id\":\"MDCLVA\"}",
              "name": "get_reservation_details"
            },
            "id": "call_HpnsUVr01FHdHv0sjv83BNfk",
            "type": "function"
          }]}
    rsp=tool_agent._run(assistant_messages)