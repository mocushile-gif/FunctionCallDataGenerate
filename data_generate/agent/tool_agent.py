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
from requests.exceptions import Timeout
# from data_generate.tools.executable_functions.shangtang_functions import *
from data_generate.tools.executable_functions.file_system_functions.code_intepreter import CodeInterpreterSession
from data_generate.tools.executable_functions import REGISTERED_TOOLS
# from data_generate.tools.executable_functions.database_functions import *
# from data_generate.tools.executable_functions.python_functions import *
from data_generate.prompt.virtual_tool_prompt import VIRTUAL_TOOL_RESPONSE_PROMPT
from data_generate.agent.rapidapi import RapidAPI
from data_generate.agent.model import *
import os
from contextlib import contextmanager
import importlib
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
load_dotenv()
pd.set_option('display.max_rows', None)  # Display all rows
pd.set_option('display.max_columns', None)  # Display all columns
pd.set_option('display.max_colwidth', None)

import logging
logger = logging.getLogger(__name__)

from contextlib import contextmanager

@contextmanager
def temp_disable_proxy(obj):
    obj.close_proxy()
    try:
        yield
    finally:
        obj.restore_original_proxy()

@contextmanager
def use_working_directory(path, retries=3, wait_seconds=5):
    default_dir = os.environ['FILE_SYSTEM_PATH']
    changed = False
    try:
        if path is None or not os.path.isdir(path):
            logger.error(f"{Fore.RED}[ToolAgent] Invalid working directory: {path}, using default.{Style.RESET_ALL}")
            # 如果 path 无效，就不切换目录，直接 yield
        else:
            attempt = 0
            while attempt < retries:
                try:
                    logger.info(f"{Fore.GREEN}[ToolAgent] Change directory to {path} successfully.{Style.RESET_ALL}")
                    os.chdir(path)
                    changed=True
                    break
                except Exception as e:
                    attempt += 1
                    if attempt > retries:
                        logger.error(f"{Fore.RED}[ToolAgent] Failed to change directory to {path} after {retries} attempts. Using default.{Style.RESET_ALL}")
                        break
                    time.sleep(wait_seconds)
        yield
    finally:
        if changed:
            os.chdir(default_dir)

class ToolAgent(BaseModel):
    description: str= ("tool_agent")
    code_session: Optional[CodeInterpreterSession] = Field(default=None)
    file_system_path: str = Field(default=None)
    llm: Union[DOUBAOFunction, ChatGPTFunction,QWen25Function] = Field(default=None)
    llm_name: str = 'gpt4o-ptu-client'
    rapidapi_metadata: Dict = Field(default=None)
    only_virtual_rapidapi_response: bool=False
    tools: Dict= Field(default=None)
    tool_modules: Dict= {}
    rapidapi: RapidAPI = Field(default=None)
    output_limit: int=4096
    original_http_proxy: str = os.environ.get("http_proxy")
    original_https_proxy: str = os.environ.get("https_proxy")
    original_no_proxy: str = os.environ.get("NO_PROXY")

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
            if 'code_intepreter' in tool:
                self.code_session = CodeInterpreterSession(self.file_system_path) #把file_system工作路径传过去
            elif tool in REGISTERED_TOOLS:
                self.tool_modules[tool.split('.')[-1]]=REGISTERED_TOOLS.get(tool)
        logger.info(f'{Fore.MAGENTA}TOOL AGENT SELF EXECUTABLE TOOLS:{Style.RESET_ALL} {Fore.WHITE}{list(self.tool_modules.keys())}{Style.RESET_ALL}')
        
        if any(['rapidapi' in tool for tool in self.tools.keys()]):
            logger.info(f'{Fore.MAGENTA}Use Rapid-API System{Style.RESET_ALL}')
            import data_generate
            project_dir = os.path.dirname(data_generate.__file__)
            rapidapi_metadata_path=f'{project_dir}/tools/xlam_rapidapi_tools_metadata.json'
            if os.path.exists(rapidapi_metadata_path):
                with open(rapidapi_metadata_path,'r',encoding='utf-8') as f:
                    self.rapidapi_metadata=list(json.load(f).keys())
            else:
                raise Exception('cannot find rapidapi metadata!')
            cache_folder=f'{project_dir}/tools/tool_response_cache'
            self.rapidapi=RapidAPI(llm_name=self.llm_name,
                                    use_cache=False,
                                    only_virtual_rapidapi_response=self.only_virtual_rapidapi_response,
                                    metadata_path=rapidapi_metadata_path,
                                    cache_folder=cache_folder)

        return self

    def restore_original_proxy(self):
        if self.original_http_proxy:
            os.environ["http_proxy"] = self.original_http_proxy
        if self.original_https_proxy:
            os.environ["https_proxy"] = self.original_https_proxy
        if self.original_no_proxy:
            os.environ["NO_PROXY"] = self.original_no_proxy

    def close_proxy(self):
        os.environ.pop("http_proxy", None)
        os.environ.pop("https_proxy", None)
        os.environ.pop("NO_PROXY", None)

    def _run(self,assistant_message: Dict[str, Any]) -> List[Dict[str, Any]]:
        with use_working_directory(self.file_system_path):
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
                # 内置工具
                if tool_name == 'code_intepreter': #jupyter code执行工具
                    code = arguments.get("code")
                    try:
                        result=self.code_session._run(code)
                        results.append({"role": "tool","content": str(result),"tool_call_id":call['id']})
                    except Exception as e:
                        results.append({"role": "tool", "content": {'status':'failed','message':f'Tool "{tool_name}" Error: '+str(e)[:4096]},"tool_call_id":call['id']})

                elif tool_name in self.tool_modules:
                    try:
                        # 获取函数签名
                        func = self.tool_modules[tool_name]
                        # 检查函数是否具有 'working_dir' 参数
                        func_signature = inspect.signature(func)
                        if 'args'  in func_signature.parameters or 'kwargs' in  func_signature.parameters:
                                new_arguments = {**arguments}
                        else:
                            new_arguments = arguments
                        # 开代理试一次，关代理试一次
                        try:
                            with temp_disable_proxy(self):
                                result = func(**new_arguments)
                        except Timeout:
                            # 使用原始代理配置重试
                            print("Timeout occurred without proxy. Retrying with proxy...")
                            result = func(**new_arguments)  

                        if len(str(result))>self.output_limit:
                            result=str(result)[:self.output_limit]+'...truncated.'
                            results.append({"role": "tool","content": str(result),"tool_call_id":call['id']})
                        else:
                            results.append({"role": "tool","content": json.dumps(result,ensure_ascii=False,default=str),"tool_call_id":call['id']})
                    except Exception as e:
                        logger.warning(f'{Fore.RED}TOOL {tool_name} ERROR at Tool {tool_name}: {str(e)[:self.output_limit]}{Style.RESET_ALL}')
                        logger.warning(f'{Fore.RED}TOOL {tool_name} Tool call: {call}{Style.RESET_ALL}')
                        logger.warning(traceback.format_exc())
                        if 'Input/output' in str(e):
                            raise Exception(str(e))
                        results.append({"role": "tool", "content": {'status':'failed','message':f'Tool "{tool_name}" Error: '+str(e)[:self.output_limit]},"tool_call_id":call['id']})
                elif tool_name in self.rapidapi_metadata: # rapidapi工具
                        result=self.rapidapi.get_rapidapi_or_virtual_response(tool_name,arguments)
                        results.append({"role": "tool","content": json.dumps(result,ensure_ascii=False,default=str),"tool_call_id":call['id']})
                # else: # open工具
                    # tools_dict={tool['name']:tool for tool in self.tools.values()}
                    # if tool_name in tools_dict:
                    #     result,error_code=self.generate_virtual_tool_answer(arguments,tools_dict[tool_name])
                    #     if error_code==200:
                    #         results.append({"role": "tool","content": json.dumps(result,ensure_ascii=False,default=str),"tool_call_id":call['id']})
                    #     else:
                    #         results.append({"role": "tool","content": {'status':'failed','message':f"Generating virtual response ERROR: {str(result)}."},"tool_call_id":call['id']})
                else:
                    results.append({"role": "tool","content": {'status':'failed','message':f"Unsupported tool: {tool_name}."},"tool_call_id":call['id']})
            
            for i,result in enumerate(results):
                if len(str(result['content']))>self.output_limit:
                    result['content']=str(result['content'])[:self.output_limit]+'...truncated.'
                    logger.info(f'{Fore.MAGENTA}TOOL RESPONSE {i}:{Style.RESET_ALL} {Fore.WHITE}{result} {Fore.RED}(truncated to {self.output_limit}){Style.RESET_ALL}')
                else:
                    logger.info(f'{Fore.MAGENTA}TOOL RESPONSE {i}:{Style.RESET_ALL} {Fore.WHITE}{result}{Style.RESET_ALL}')
            return results

    def generate_virtual_tool_answer(self,arguments,tool_define):
        if "response" not in tool_define:
            raise ValueError(f"ERROR! Generating virtual response for tool {tool_define['name']}: 'response' not in tool define.")
        TOOL_TEMPLET = {
                "tool_define":{"name":tool_define['name'],
                               "description":tool_define['description'],
                               "parameters":tool_define['parameters']},
                "response":tool_define['response'],
                "usage_examples":tool_define['usage_examples'] if 'usage_examples' in tool_define else None,
                "request":arguments}
        virtual_tool_response_prompt=VIRTUAL_TOOL_RESPONSE_PROMPT.format(**TOOL_TEMPLET)
        messages=[{'role':'user','content':virtual_tool_response_prompt}]
        output, error_code = self.llm.chat(messages)
        if error_code==200:
            if '```json' in output['content']:
                match = re.findall(r'```json\s*(.*?)\s*```', output['content'], re.DOTALL)[0]
            else:
                match =output['content']
            # Parse each match as a JSON object
            try:
                parsed_matches = json.loads(match.replace("'",'\\"'),strict=False)
                return parsed_matches,200
            except:
                return output['content'],200
        return output['content'],error_code

if __name__ == "__main__":
    import logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] [%(levelname)s] [Thread:%(threadName)s - %(thread)d]\n%(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger = logging.getLogger(__name__)
    from data_generate.utils import load_tool_defines   
    tools = load_tool_defines(
        directory=f'{os.environ["PROJECT_DIR"]}/tools/defines/file_system_functions/image_functions/',
        recursive=True,
    )
    tool_agent = ToolAgent(
            llm_name='gpt',
            file_system_path=f'{os.environ["PROJECT_DIR"]}/working_dir/image/',
            tools=tools
        )
    assistant_messages={'role': 'assistant', 'tool_calls': [{'function':  {"name": "getnews", "arguments": {"page": 3}}, 'id': 'call_f664e93c-489a-4574-afd3-1e5ad9730d01', 'type': 'function'}]}
    assistant_messages={'role': 'assistant', 'tool_calls': [{'function':  {"name": "duckduckgo_websearch", "arguments": {"query": "查询上海天气"}}, 'id': 'call_f664e93c-489a-4574-afd3-1e5ad9730d01', 'type': 'function'}]}
    # assistant_messages={'role': 'assistant', 'tool_calls': [{'function': {'name': 'code_intepreter', 'arguments': {'code': 'a=3\nprint("hello")'}}, 'id': 'call_f664e93c-489a-4574-afd3-1e5ad9730d01', 'type': 'function'}]}
    # assistant_messages={"role": "assistant", "tool_calls": [{"function": {"arguments": "{\"file_path\":\"./excel_data/AmazingMartEU2.xlsx\",\"preview_rows\":5}", "name": "get_file_info"}, "id": "call_20yPJmpCSPTHYi1MTpy8kt3N", "type": "function"}]}
    # assistant_messages={'role': 'assistant', 'tool_calls': [{'function': {'name': 'query_file_with_sql', 'arguments': {'file_path': './csv_data/TED Talks.csv', 'sql_query': "SELECT * FROM data WHERE title = 'You deserve the right to repair your stuff'", 'table_name': 'data'}}, 'id': 'call_1e047fc4-f884-4ce4-bc56-6c9c28fcbfec', 'type': 'function'}]}
    # assistant_messages={'role': 'assistant', 'tool_calls': [{'function': {'name': 'check_table_null_values', 'arguments': {'database_path': './database/chinook.db', 'table_name': "Album"}}, 'id': 'call_1e047fc4-f884-4ce4-bc56-6c9c28fcbfec', 'type': 'function'}]}
    # assistant_messages={"role": "assistant", "tool_calls": [{"function": {"arguments": {'url': 'https://finance.yahoo.com/quote/TSLA/news', 'extract_content': 'clean_content', 'max_length': 5000, 'save_path': './yahoo_tesla_news.md'}, "name": "fetch_url"}, "id": "call_rpLCy1u3yvMG8LbAypAToGcu", "type": "function"}]}
    assistant_messages={"role": "assistant", "tool_calls": [{'function': {'arguments': '{"image_path": "./image_data/dog.jpg"}', 'name': 'blur_image'}, "id": "call_rpLCy1u3yvMG8LbAypAToGcu", "type": "function"}]}
    # assistant_messages={'role': 'assistant', 'tool_calls': [{'function': {'name': 'create_bar_chart_from_database', 'arguments': {'database_path': './database/delivery_center.sqlite', 'from_clause': 'deliveries', 'x_column': 'delivery_status', 'y_column': 'delivery_distance_meters', 'agg_method': 'mean', 'title': 'Average Delivery Distance by Status', 'xlabel': 'Delivery Status', 'ylabel': 'Average Distance (meters)', 'save_path': './average_distance_by_status.png'}}, 'id': 'call_d564b664-2f96-45dc-86ef-e26add00226b', 'type': 'function'}]}
    # assistant_messages={"role": "assistant", "tool_calls": [{"function": {"name": "code_intepreter", "arguments": {"code": "import pandas as pd\nimport matplotlib.pyplot as plt\nfrom datetime import datetime\n\n# 读取创意素材工作表\nfile_path = './excel_data/达人数据.xlsx'\ndf = pd.read_excel(file_path, sheet_name='创意素材')\n\n# 数据清洗：处理时间列和缺失值\n# 将时间列转换为datetime格式并提取日期，忽略无效值\ndf['时间'] = pd.to_datetime(df['时间'], errors='coerce').dt.date\n# 删除时间或消费为NaN的行\ndf = df.dropna(subset=['时间', '消费'])\n\n# 按日期和计划名称分组，计算每日各活动总消费\naggregated = df.groupby(['时间', '计划名称'])['消费'].sum().reset_index()\n\n# 保存聚合数据到CSV\naggregated.to_csv('daily_campaign_consumption.csv', index=False)\n\n# 计算各活动总消费并获取TOP3\ncampaign_total = aggregated.groupby('计划名称')['消费'].sum().reset_index()\ntop3_campaigns = campaign_total.nlargest(3, '消费')['计划名称'].tolist()\n\n# 过滤出TOP3活动的数据\nfiltered = aggregated[aggregated['计划名称'].isin(top3_campaigns)]\n\n# 绘制折线图\nplt.figure(figsize=(15, 7))\nfor campaign in top3_campaigns:\n    data = filtered[filtered['计划名称'] == campaign]\n    plt.plot(data['时间'], data['消费'], marker='o', label=campaign)\n\nplt.title('Top 3 Campaigns Daily Spending Trend')\nplt.xlabel('Date')\nplt.ylabel('Daily Consumption (¥)')\nplt.xticks(rotation=45)\nplt.legend()\nplt.grid(True)\nplt.tight_layout()\nplt.savefig('top3_campaign_trends.png')\nplt.show()\nprint('Data saved to daily_campaign_consumption.csv and chart saved to top3_campaign_trends.png')"}}, "id": "call_c64bc0fa-27af-4c00-97ad-15ea1599d86a", "type": "function"}]}
    tool_agent._run(assistant_messages)

    # print(tool_agent.code_session._run("print(a)"))

    tool_agent.code_session._close()
