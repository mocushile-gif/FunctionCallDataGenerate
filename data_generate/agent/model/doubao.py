import os
import openai
import os
import sys
from dotenv import load_dotenv
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

# DOUBAO_API_KEY="6ef45f7f-1d82-4d34-80c0-c70180bd59fc"
# DOUBAO_MODEL="ep-20241210112235-7l2qr"
# DOUBAO_URL="https://ark.cn-beijing.volces.com/api/v3"

import openai
from datetime import datetime
import json
import openai_proxy
import os
import sys
from dotenv import load_dotenv
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

class DOUBAOFunction:
    def __init__(self, model='doubao',api_key=''):
        if api_key:
            self.api_key = api_key
        else:
            self.api_key=os.environ.get("DOUBAO_API_KEY")
        self.model_name=model
        self.model=os.environ.get("DOUBAO_MODEL")

    def chat(self, messages, functions=[], **args):
        # print(messages)
        try:
            if functions:
                functions= [{
                    "type": "function",
                    "function": func} 
                    for func in functions]
                json_data = self.chat_completion_request(
                    messages, functions=functions, **args
                )
            else:
                json_data = self.chat_completion_request(
                    messages, **args
                )
            message = json_data["choices"][0]["message"]

            if "tool_calls" in message.keys():
                tool_calls=[]
                for func in message["tool_calls"]:
                    if 'multi_tool_use' in func['function']['name']:
                        tool_uses=json.loads(func['function']['arguments'])['tool_uses']
                        for tool_use in tool_uses:
                            tool_calls.append({'type':'function',
                                         'function':
                                                {'name':tool_use["recipient_name"].split(".")[-1],
                                                'arguments':tool_use["parameters"]}})
                        message['tool_calls']=tool_calls
                    else:
                        func["function"]["name"] = func["function"]["name"].split(".")[-1]
            return message,200
        except Exception as e:
            return {"role": "assistant", "content": str(e)},500

    def chat_completion_request(self, messages, functions=None, function_call=None, stop=None,**args):
        current_date = datetime.now().strftime("%Y%m%d")
        json_data = {
            "model": self.model,
            "messages": messages,
            "temperature": 0,
            "max_tokens": 4096,
            "top_p": 0.7,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            **args
        }
        if stop is not None:
            json_data.update({"stop": stop})
        if functions is not None:
            json_data.update({"tools": functions})
        # print(json_data)
        openai.api_key = self.api_key
        openai.api_base=os.environ["DOUBAO_URL"]
        # print(messages)
        self.retries = 0
        self.max_retries = 30
        self.retry_interval = 15
        while self.retries < self.max_retries:
            try:
                openai_response = openai.ChatCompletion.create(
                    **json_data,timeout=60
                )
                json_data = json.loads(str(openai_response))
                # print(json_data)
                if 'finish_reason' in json_data['choices'][0] and json_data['choices'][0]['finish_reason']=='length':
                    raise Exception(f"context_length_exceeded")
                elif 'finish_reason' in json_data['choices'][0] and json_data['choices'][0]['finish_reason']=='content_filter':
                    raise Exception(f"content_filter")
                return json_data
                
            except openai.error.RateLimitError:
                print(f"Got rate limit error. Retrying after {self.retry_interval} seconds...")
                time.sleep(self.retry_interval)
                self.retries += 1
            except Exception as e:
                if "context_length_exceeded" in str(e):
                    raise Exception(f"context_length_exceeded")
                elif "Invalid image URL" in str(e):
                    raise Exception(f"Invalid image URL")
                elif "The provided image url can not be accessed" in str(e):
                    raise Exception(f"The provided image url can not be accessed")
                elif "content_filter" in str(e):
                    raise Exception(f"Trigger content filter")
                print(f"Got error: {str(e)}. {self.retries} retry. Retrying after {self.retry_interval} seconds...")
                time.sleep(self.retry_interval)
                self.retries += 1
                last_error=str(e)
        raise Exception(f"Retries for {self.max_retries} times but still failed. Reason: {last_error}")

if __name__ == "__main__":
    llm = DOUBAOFunction()
    messages=[{"role": "user", "content": "[!IMAGE](https://da465f41.png)"}, 
                {"role": "user", "content": "[!IMAGE](https://7360b453.png)"}, 
                {"role": "user", "content": "将以上图片翻译为中文"}, 
            ]
    messages=[{"role": "user", "content": "[!IMAGE](https://da465f41.png)"}, 
                {"role": "user", "content": "[!IMAGE](https://7360b453.png)"}, 
                {"role": "user", "content": "将上面两张图翻译为中文，并查询明天香港天气"}
            ]
    messages=[{"role": "user", "content": "/mnt/nvme0/qinxinyi/function_call_data/data_generate/executable_functions/functions/file_system_functions/change_owner.py先读取这个函数的内容，然后根据函数内容为它生成openai格式的json函数定义并将该函数定义作为一个变量（变量名是函数名）储存到这个路径下的一个py文件中/mnt/nvme0/qinxinyi/function_call_data/data_generate/executable_functions/defines/file_system_functions"}]
    # messages=[{"role": "user", "content": "生成一张小猫图片"}]
    functions=[{
  "name": "execute_file_system_command",
  "description": "执行 Linux 系统命令并返回输出或错误信息。",
  "parameters": {
    "type": "object",
    "properties": {
      "command": {
        "type": "string",
        "description": "要执行的 Linux 系统命令。"
      }
    },
    "required": ["command"]
  }
},{
    "name": "hongkong_weather",
    "description": "This function can query weather information about Hong Kong. If a user asks for weather information about Hong Kong, use this function over a web searcher.",
    "parameters": {
        "type": "object",
        "properties": {
            "lang": {
                "description": "The language expected by the user, should match the user's question. Choose from: 'en' - for English, 'tc' - for Traditional Chinese, 'sc' - for Simplified Chinese",
                "type": "string"
            }
        },
        "required": ["lang"]
    }},
    {
            "name": "vqa_agent",
            "description": "This function serves as a Visual Question Answering agent. It can understand image-based visual questions and provide answers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "A repfrased question based on the original question and conversation histories that the agent should use to answer the question about the images provided."
                    },
                    "images": {
                    "type": "array",
                    "description": "A list of image URLs from conversation histories this question refers to.",
                    "items": {
                        "type": "string"
                    }
                }
                },
                "required": [
                    "prompt",
                    "image"
                ]
            }
        },
        {
            "name": "text2image",
            "description": "This function generates a visual representation of a given textual description. "
        "It is capable of creating images in various styles based on the provided prompts.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "A detailed textual description used to generate the image. "
        "The prompt should be clear and descriptive, potentially including details about the "
        "desired style (photorealism style if not specified), color scheme, and content of the image. "
        "If the user requested modifications to a previous image, the prompt should be refactored "
        "to integrate the user suggestions based on the previous one."
                    }
                },
                "required": [
                    "prompt"
                ]
            }
        }]
    print(llm.chat(messages,functions))