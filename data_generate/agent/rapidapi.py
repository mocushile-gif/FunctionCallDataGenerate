import json
import os, yaml
import requests
from typing import Union
from pydantic import BaseModel,Field, model_validator
from requests.exceptions import Timeout
from data_generate.agent.model import *
import logging
from datetime import datetime
logger = logging.getLogger(__name__)

class RapidAPI(BaseModel):
    cache_folder: str=None
    metadata_path: str=None
    toolbench_url: str="http://8.130.32.149:8080/rapidapi"
    toolbench_key: str="LKKU9xQ4YHawCQBLl2iUgCaWxYJJnsKU1Kr525Z2oSLVl1M378"
    use_cache: bool=False
    only_virtual_rapidapi_response: bool=False
    llm: Union[DOUBAOFunction, ChatGPTFunction,QWen25Function] = Field(default=None)
    llm_name: str = 'gpt4o-ptu-client'

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
        elif 'deepseek' in self.llm_name:
            self.llm = Deepseek25Function(args={'temperature': 0.7})
        elif 'qwq' in self.llm_name:
            self.llm = QwQFunction(args={'temperature': 0.7})
        else:
            raise NameError('not support')
        
        if not self.metadata_path or not self.cache_folder:
            import data_generate
            project_dir = os.path.dirname(data_generate.__file__)
            self.metadata_path=f'{project_dir}/tools/xlam_rapidapi_tools_metadata.json'
            self.cache_folder=f'{project_dir}/tools/tool_response_cache'
        if not os.path.exists(self.metadata_path):
            raise Exception(f'Metadata path does not exist: {self.metadata_path}')
        if not os.path.exists(self.cache_folder):
            raise Exception(f'Cache folder path does not exist: {self.cache_folder}')
        return self
    

    def request_rapidapi(self, category, tool_name, api_name, tool_input):
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
            'toolbench_key': self.toolbench_key
        }
        data = {
            "category": category,
            "tool_name": tool_name,
            "api_name": api_name,
            "tool_input": tool_input,
            "strip": "",
            "toolbench_key": self.toolbench_key
        }

        # 保存原始代理配置
        original_http_proxy = os.environ.get("http_proxy")
        original_https_proxy = os.environ.get("https_proxy")
        original_no_proxy = os.environ.get("NO_PROXY")

        def restore_original_proxy():
            if original_http_proxy:
                os.environ["http_proxy"] = original_http_proxy
            if original_https_proxy:
                os.environ["https_proxy"] = original_https_proxy
            if original_no_proxy:
                os.environ["NO_PROXY"] = original_no_proxy

        try:
            # Step 1: 禁用代理尝试
            os.environ.pop("http_proxy", None)
            os.environ.pop("https_proxy", None)
            os.environ.pop("NO_PROXY", None)

            response=requests.post(
                self.toolbench_url, headers=headers, data=json.dumps(data), timeout=20
            )
            restore_original_proxy()

        except Timeout:
            print("Timeout occurred without proxy. Retrying with proxy...")

            # Step 2: 启用代理并重试
            restore_original_proxy()
            response=requests.post(
                self.toolbench_url, headers=headers, data=json.dumps(data), timeout=60
            )
        return response

    def get_rapidapi_or_virtual_response(self, name, arguments):
        api_name=name
        try:
            if os.path.exists(self.metadata_path):
                with open(self.metadata_path,'r',encoding='utf-8') as f:
                    metadata=json.load(f)
                    if api_name not in metadata:
                        raise KeyError(f"can't find api {api_name} in metadata")
                    category=metadata[api_name]["category"]
                    tool_name=metadata[api_name]["tool_name"]
            else:
                raise Exception("no api metadata available")
        except Exception as e:
            raise Exception(f"Loading api_doc error: {e}")
                
        tool_input=arguments
        if not type(tool_input) is dict:
            try:
                if tool_input == "":
                    tool_input = {}
                else:
                    tool_input = json.loads(tool_input)
            except Exception as e:
                logger.warning(f"Can not parse tool input into json: {tool_input}")
                response_dict = {"error": f"Tool input parse error...\nTool input: {tool_input}", "response": ""}
                return response_dict

        if not os.path.exists(self.cache_folder):
            os.mkdir(self.cache_folder)
        # load from cache
            
        cache = {}
        try:
            if os.path.exists(os.path.join(self.cache_folder, api_name+".json")):
                tools_cache_record = json.load(open(os.path.join(self.cache_folder, api_name+".json"), "r"))
                cache.update(tools_cache_record)
                if str(tool_input) in cache and self.use_cache:
                    logger.info("using cached real response")
                    response_dict = cache[str(tool_input)]
                    return response_dict
        except Exception as e:
            logger.error(f"Loading cache error: {e}")
            
        """
        Call the real api before generating fake response
        """
        if not self.only_virtual_rapidapi_response:
            real_response=self.request_rapidapi(category,tool_name,api_name,tool_input)
            # Check if the request was successful
            if real_response.status_code == 200:
                real_response = real_response.json()
                if self.check_result(real_response):
                    logger.info("rapid api returning real_response")
                    # 若cache中数量小于10，则存下来
                    if len(list(cache.items()))<10:
                        self.save_cache(cache, tool_input, real_response, api_name)
                    return real_response
                else:
                    logger.info(f"ERROR with api: {real_response}")
            else:
                logger.info(f"ERROR with api: {real_response.json()}")
        # """
        # Fake response function here. Use the cached history response for in-context examples.
        # result = fake_response_function(api_doc, api_name, api_parameters, *kwargs)
        # """

        # parse api_doc
        api_doc = {
            'tool_description': "",
            'api_info': "",
        }
        try:
            if metadata:
                if api_name not in metadata:
                    raise KeyError("cant match api name")
                api_doc = {
                    'tool_description': metadata[api_name]['tool_description'],
                    'api_define': metadata[api_name]['api_define']
                }
            else:
                raise Exception("no api metadata available")
        except Exception as e:
            logger.error(f"Loading api metadata error: {e}")

        # get several examples from cache
        example_num = 3
        # get top example_num examples
        api_examples = list(cache.items())[:example_num]
        while len(str(api_examples)) > 4096 and example_num > 1:
            example_num -= 1
            api_examples = list(cache.items())[:example_num]
        api_examples = [{"input":example[0],"response":example[1]} for example in api_examples]
            
        if self.only_virtual_rapidapi_response:
            logger.info("\nTry to generate virtual response:")
        else:
            logger.info("\nERROR with real api. Try to generate virtual response:")
        logger.debug(f"api example: {api_examples}  \napi_doc: {api_doc} \napi_input: {tool_input}")
            
        result = self.generate_fake_tool_response(api_examples,tool_input,api_doc)
        logger.debug(f"\nGenerated fake result: {result}")

        # 若不存在cache，则存下来虚拟的回复
        if len(list(cache.items()))==0:
            self.save_cache(cache, tool_input, result, api_name)
        if not isinstance(result, dict):
            return json.loads(result)
        else:
            return result
        
    @staticmethod
    def is_valid_json(result):
        # check json format
        try:
            result = json.loads(result.replace("'",'\\"'),strict=False)
            return True
        except Exception:
            logger.info(f"Can not parse result into json: {result}.")
            return False

    @staticmethod
    def check_result(processes_value: dict):
        logger.info(processes_value)
        if 'error' not in processes_value or processes_value['error']:
            return False
        if 'response' not in processes_value:
            return False
        response = str(processes_value['response'])
        if any([key.lower() in response.lower() for key in ['please upgrade your plan','does not exist','internal error','API doesn\'t exists','Not Found','Cannot GET','Service Unavailable']]):
            return False
        elif response=='[]':
            return False
        # response = str(processes_value['response'])
        # if 'rate limit' in response.lower() or 'time out' in response.lower() or 'timed out' in response.lower() or 'does not exist' in response.lower() or '404' in response.lower() or '504' in response.lower() or 'internal error' in response.lower() or 'API doesn\'t exists' in response.lower() or "API doesn\'t exists" in response.lower() or response == '{\'message\': "API doesn\'t exists"}' or 'Service Not Found' in response:
        #     return False
        # elif 'authoriz' in response.lower() or 'authenticat' in response.lower() or 'unauthorized' in response.lower() or 'blocked user' in response.lower() or 'unsubscribe' in response.lower() or 'blocked' in response.lower() or '401' in response.lower() or '403' in response.lower() or 'credential' in response.lower() or 'unauthenticated' in response.lower() or 'disabled for your subscription' in response.lower() or 'ACCESS_DENIED' in response:
            # return False
        # elif 'parameter' in response.lower() or 'parse' in response.lower() or 'is not defined' in response.lower():
        #     return False
        # elif len(response) == 0:
            # return False
        # elif "status_code=50" in response or "status_code=429" in response:
            # return False
        return True

    def save_cache(self, cache, tool_input, result, api_name):
        # save cache
        try:
            if isinstance(result, dict):
                cache[str(tool_input)] = result
            elif isinstance(result, str):
                try:
                    result_dict = json.loads(result)
                    cache[str(tool_input)] = result_dict
                except Exception as e:
                    logger.info(f"Load result failed: {e}")
                    return

            if not os.path.exists(self.cache_folder):
                os.mkdir(self.cache_folder)
            json.dump(cache, open(os.path.join(self.cache_folder,api_name+".json"), "w"), indent=4)
        except Exception as e:
            logger.info(f"Save cache failed: {e}")

    
    def generate_fake_tool_response(self,api_examples, tool_input, api_doc):
        '''
        api_example: list of tuple, [(input, output), ...]
        tool_input: dict, input of the tool
        api_doc: dict, api document
        '''

        today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')[:10]

        prompt = '''
    The current time is {today}.

    Imagine you are an API Server operating within a specialized tool, which contains a collection of distinct APIs. Your role is to deeply understand the function of each API based on their descriptions in the API documentation.
    As you receive specific inputs for the API, analyze these inputs to determine their intended purpose. Your task is to craft a JSON formatted response that aligns with the expected output of the API, guided by a provided example.\n

    Your responses must adhere to a specific JSON structure, which is as follows:\n
    {{
        "error": "",
        "response": "<Your_Response>"
    }}\n
    The error field should remain empty, indicating no errors in processing. The response field should contain the content you formulate based on the API's functionality and the input provided. Ensure that your responses are meaningful, directly addressing the API's intended functionality. If the provided examples are mostly error messages or lack substantial content, use your judgment to create relevant and accurate responses. The key is to maintain the JSON format's integrity while ensuring that your response is an accurate reflection of the API's intended output within the tool.\n
    Please note that your answer should not contain anything other than a json format object, which should be parsable directly to json.
    Note that:
    - your response should be around 100 to 200 words, containing rich information given the api input parameters. Keep Your answer short and simple.
    - your response must be effective and have practical content.
    - if the api response example if null or ineffective, ignore the example and give your independent response.

    Tool description: {tool_description}

    API Documentation: {api_define}

    An Example: {api_example}

    API Input: {tool_input}
    '''
        template={"tool_description":str(api_doc['tool_description']),
                "api_define":str(api_doc['api_define']),
                "api_example":str(api_examples),
                "tool_input":str(tool_input),
                "today":str(today)}
        messages = [{"role": "user", "content": prompt.format(**template)}]

        max_retries = 3 
        flag = False
        for attempt in range(max_retries):
            response,error_code = self.llm.chat(
                messages
            )
            result=response['content']
            if error_code==200:
                if "```json" in result:
                    result = result.replace("```json", "").replace("```", "").strip()
                if self.is_valid_json(result):
                    flag = True
                    break
                logger.info(f"Invalid JSON response on attempt {attempt + 1}. Retrying...")
            else:
                logger.info(f"ERROR on attempt {attempt + 1}. {result}.Retrying...")

        if flag:
            return result
        else:
            fake_error = {
                "error": "Failed to fetch response.",
                "response": "",
            }
            return json.dumps(fake_error)

if __name__ == "__main__":
    import logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] [%(levelname)s] [Thread:%(threadName)s - %(thread)d]\n%(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger = logging.getLogger(__name__)
    tool_calls=[{"name": "time_zone_api", "arguments": {"q": "G2J"}}, {"name": "time_zone_api", "arguments": {"q": "48.8567,2.3508"}}]
    tool_calls=[
        # {"name": "analyze_v2", "arguments": {"category": "accessibility","strategy":"desktop","url":"https://example.com"}},
        # {"name": "airport_search", "arguments": {"query": "San Francisco"}},
                 {'arguments': '{"city": "New York"}', 'name': 'get_the_forecast'},
            # {"arguments": "{\"q\":\"API development tutorials\",\"hl\":\"en_us\",\"gl\":\"us\",\"duration\":\"short\",\"device\":\"desktop\",\"num\":\"10\"}", "name": "google_videos"}
    # tool_calls=[{"name": "get_leaderboard_rank", "arguments": {}}]
# {
#                         "name": "qr_code_gen",
#                         "arguments": {
#                             "url": "https://forms.gle/menstrualCycleFeedback2023!survey?trackID=CYC-456#improvements"
#                         }
#                     }
            ]
    for tool_call in tool_calls:
        rapidapi=RapidAPI(llm_name='gpt',use_cache=False)
        # res=rapidapi.check_result({'error': '', 'response': "{'companies_use_same_domain': ['https://www.linkedin.com/company/sensetime-mea'], 'confident_score': '80%', 'data': {'affiliated_companies': [], 'company_id': '9272195', 'company_name': 'SenseTime 商汤科技', 'description': 'SenseTime is a leading AI software company founded in Hong Kong in 2014, focused on creating a better AI-empowered future through innovation. Upholding a vision of advancing the interconnection of physical and digital worlds with AI, driving sustainable productivity growth and seamless interactive experiences, SenseTime is committed to advancing AI research, developing scalable and affordable AI software platforms that benefit businesses, people and society, as well as attract and nurture top talents to shape the future together.\\n\\nWith our roots in the academic world, we invest in original and cutting-edge research that allows us to offer and continuously improve industry-leading, full-stack AI capabilities, covering key fields across perception intelligence, decision intelligence, AI-enabled content generation and AI-enabled content enhancement, as well as key capabilities in AI chips, sensors and computing infrastructure. Our proprietary AI infrastructure, SenseCore, allows us to develop powerful and efficient AI software platforms that are scalable and adaptable for a wide range of applications. Our technologies are trusted by customers and partners in many industry verticals including Smart Business, Smart City, Smart Life and Smart Auto.\\n\\nSenseTime ha"})
        res=rapidapi.get_rapidapi_or_virtual_response(tool_call["name"],tool_call["arguments"])
        logger.info(res)