import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import openai
from datetime import datetime
import json
import openai_proxy
import time
from pydantic import BaseModel,Field, SecretStr, model_validator
import tiktoken
from dotenv import load_dotenv
load_dotenv()

class ChatGPTFunction(BaseModel):
    name: str = Field(default=None)
    openai_key: str = Field(default=None)
    gpt_model: str = Field(default=None)
    client : openai_proxy.GptProxy = Field(default=None)
    retries : int = 0
    max_retries : int = 10
    retry_interval : int = 10
    args: dict = Field(default=None)
    parameters: dict = {
                        'max_new_tokens': 4096,
                        'do_sample': False,
                        "temperature": 0,
                        "top_p": 0.7,
                        "frequency_penalty": 0,
                        "presence_penalty": 0}

    class Config:
        arbitrary_types_allowed = True

    @model_validator(mode='after')
    def validate_environment(self):
        if self.args:
            self.parameters.update(**self.args)
        if not self.openai_key:
            if 'ptu-client' in self.name:
                self.gpt_model=os.environ["GPT4O_PTU_CLIENT_MODEL"]
                self.openai_key=os.environ["GPT4O_PTU_CLIENT_KEY"]
            elif 'ptu' in self.name:
                self.gpt_model=os.environ["GPT4O_PTU_MODEL"]
                self.openai_key=os.environ["GPT4O_PTU_KEY"]
            else:
                raise Exception('not support this model')
        return self
    

    def count_tokens(self,messages, functions=None):
        """
        Estimate total token count for a ChatCompletion prompt with optional functions (tools).
        """
        enc = tiktoken.encoding_for_model("gpt-4o")
        num_tokens = 0
        num_prompts = 0

        # Messages
        for message in messages:
            num_tokens += 4  # Each message's structural overhead
            for key, value in message.items():
                num_tokens += len(enc.encode(value))
                num_prompts += len(value)
        num_tokens += 2  # assistant priming tokens

        # Functions (tools)
        if functions:
            functions_str = json.dumps(functions, separators=(",", ":"))  # Compact JSON
            num_tokens += len(enc.encode(functions_str))
            num_prompts += len(functions_str)

        return {"token_count": num_tokens,"prompt_count":num_prompts}


    def chat(self, messages, functions=[]):
        for idx in range(len(messages)):
            if 'content' in messages[idx] and messages[idx]['content'] == None:
                messages[idx]['content'] = "None"   
        # print(messages)
        try:
            if functions:
                functions= [{
                    "type": "function",
                    "function": func} 
                    for func in functions]
                json_data = self.chat_completion_request(
                    messages, functions=functions
                )
            else:
                json_data = self.chat_completion_request(
                    messages
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

    def chat_completion_request(self, messages, functions=None):
        current_date = datetime.now().strftime("%Y%m%d")
        if 'ptu-client' in self.name:
            # 同步接口调用
            if functions is not None:
                self.parameters.update({"tools": functions})
            self.client = openai_proxy.GptProxy(api_key=self.openai_key)
            # print(messages)
            while self.retries < self.max_retries:
                try:
                    rsp = self.client.generate(
                        messages=messages,
                        model=self.gpt_model,
                        transaction_id=f"fc_{current_date}_{self.openai_key[-4:]}", # 同样transaction_id将被归类到同一个任务，一起统计
                        **self.parameters,
                    )   
                    try:
                        response=rsp.json()['data']['response_content']
                        if 'finish_reason' in rsp.json()['data'] and rsp.json()['data']['finish_reason']=='content_filter':
                            raise Exception(f"Trigger content filter")
                        return response
                    except:
                        raise Exception(f"{rsp.text}")
                except Exception as e:
                    if "context_length_exceeded" in str(e) or "string_above_max_length" in str(e):
                        raise Exception(f"context_length_exceeded")
                    elif "Invalid image URL" in str(e):
                        raise Exception(f"Invalid image URL")
                    elif "The provided image url can not be accessed" in str(e):
                        raise Exception(f"The provided image url can not be accessed")
                    elif "content_filter" in str(e):
                        raise Exception(f"Trigger content filter")
                    elif "invalid_request_error" in str(e):
                        raise Exception(f"invalid_request_error: {messages}")
                    print(f"Got error: {str(e)}. {self.retries} retry. Retrying after {self.retry_interval} seconds...")
                    time.sleep(self.retry_interval)
                    self.retries += 1
                    last_error=str(e)
            raise Exception(f"Retries for {self.max_retries} times but still failed. Reason: {last_error}")
        elif "ptu" in self.name:
            # ptu直连，一般只在ptu异步系统崩坏时开放（openai版本0.28.0）
            json_data = {
                "engine": self.gpt_model,
                "messages": messages,
                **self.parameters
            }
            if functions is not None:
                json_data.update({"tools": functions})
            openai.api_type = "azure"
            openai.api_version = "2024-08-01-preview"
            openai.api_key = self.openai_key
            openai.api_base=os.environ["GPT4O_PTU_BASE"]
            
            while self.retries < self.max_retries:
                try:
                    openai_response = openai.ChatCompletion.create(
                        **json_data,timeout=60
                    )
                    json_data = json.loads(str(openai_response))
                    return json_data
                except openai.error.RateLimitError:
                    print(f"Got rate limit error. Retrying after {self.retry_interval} seconds...")
                    time.sleep(self.retry_interval)
                    self.retries += 1
                except Exception as e:
                    time.sleep(self.retry_interval)
                    self.retries += 1
                    print(f"Got error. Retrying after {self.retry_interval} seconds...")
                    # raise Exception(f"{str(e)}")
                        
            raise Exception(f"Retries for {self.max_retries} times but still failed")

if __name__ == "__main__":
    llm = ChatGPTFunction(name='gpt4o-ptu-client',args={'temperature': 1})
    messages=[
                {"role": "user", "content": "合并/mnt/nvme0/qinxinyi/function_call_data/data_generate/agent/working_dir路径下的所有excel文件，并保存到原路径下，文件名是total_data"}
            ]
    # messages=[{"role": "system", "content": "今天的日期是：2024-11-30\n###角色：\n你名叫Sensechat，中文名是「商量」。你的回答需要條理清晰、邏輯清楚，回答的語言應同使用者的輸入語言一致或者按照使用者的要求，默認使用粵語回覆用戶。請記住你有調動工具的能力，例如“web_search”。你需要記住用戶的地理位置在香港，因此用戶的查詢內容大多為本地資訊為主，必須使用“web_search”獲取最新資訊。\n\n###工具使用說明：你擁有工具 text2image、vqa_agent、web_search，分別用於畫圖、圖片問答、網路搜索。\n搜索規則：\n如果用戶問你關於資訊性的內容，一定要調用“web_search”獲取最新資料後才回覆。例如：\n* 地鐵及公共交通資訊：如「地鐵港島綫有幾多個站？」或「5A九巴路線？」\n* 餐廳及美食推薦：如「香港科學園有咩餐廳？」或「銅鑼灣有邊間omakase？」\n* 地點及位置查詢：如「知唔知香港青山係邊？」或「綠楊坊壽司郎系邊度？」\n* 學校介紹及教育資訊：如「介紹下拔萃女書院？」或「知唔知德望學校？」\n* 特定店鋪資訊：如「香港壽司郎有幾多間？」\n* 交通路線及站數查詢：如「搭地鐵嘅話，粉嶺去炮台山有幾多個站？」\n* 最近上映電影：如「最近香港有咩電影上映？」或「邊套電影好睇？」\n* 新聞查詢：如「今日香港有咩新聞？」或「最新嘅香港新聞係咩？」\n* 特定人物查詢：如「知唔知XXX係邊個？」或「香港特首是誰？」\n\n###地理信息補充：\n在進行搜索時，如果問題涉及到泛指（例如“最近有什麼電影？），請自動補充地理位置信息，例如“最近香港有什麼電影？”\n###\n附加條件：\n1. 不熟悉的術語或名稱：如果用戶詢問你完全不熟悉的術語或者你沒看到過的名稱時，請調用web_search工具。\n2. 核實搜索結果匹配度：當搜索結果與用戶的查詢問題不匹配時，你有權不引用搜索內容進行回覆，需要核實搜索結果與用戶查詢問題的匹配度後才回覆。\n\n###輸出要求\n1. 回覆內容：根據用戶提問，生成符合條理清晰、邏輯清楚的回答，並使用粵語，長度不超過200字。\n2. 回覆語言：能夠根據用戶輸入的語言（粵語或英語）做出相對應語言的回答，同時如果用戶明確指定回復語言時，按照用戶指定的語言回復。\n### 模型不支持以下功能：图生图、搜图、路径规划、图片处理、图片微调。若用户问题涉及这些功能，请礼貌地拒绝回答。\n### 表格以文本格式输出，无需调用text2image工具。\n### 模型无法直接感知当前具体时间，需要调用web_search工具获取。\n### 以下领域问题应调用web_search工具：天气预报，热搜、经济、娱乐八卦、社会、科技、政治等新闻，财经数据，特定人物，公司动态，旅行规划，学术研究，教育资源，体育赛事，休闲娱乐，节假日安排，星座黄历等。\n### 工具输入参数语言应同用户的输入语言一致，默认使用简体中文。\n### 当你需要基于工具调用结果给用户生成总结回复时，考虑以下要求：\n1. web_search搜索场景:\n你需要完全基于搜索结果来给回答用户的问题，不能自己编造信息。\n如果搜索结果提供的信息不足以回答用户的问题，则你需要表达信息不足，并结合你的知识给出适当回复。\n如果信息足够，你应在提及搜索结果时在段落结尾处注明所引用的搜索结果，例如[ref_1]。\n若搜索结果的信息过于陈旧，你应提醒用户注意信息的时效性。\n你的回答要保证内容尽可能详细完整并且结构清晰，引用标记与搜索结果可以对应正确和完整。\n\n2. vqa_agent图片问答场景:\n你需要结合vqa_agent工具调用结果与对话历史回答用户问题，不能自己编造信息。\n\n3. text2image文生图场景：\n你需要将text2image工具调用生成的结果以图片描述的形式回复给用户，可以进行适当的润色和丰富文本，方便用户阅读，但不可编造不存在的内容。\ntext2image工具返回的图像链接会自动被展示，无需包含在回复内容中。\n\n### 在获得工具调用结果后，若你认为需要通过进一步的工具调用获得更多信息时，可以继续调用工具而不是直接总结。\n### 注意不要混淆粤语，繁体中文，简体中文和英文。\n### 工具调用结果为空、包含错误、未成功执行或是不相关的（不匹配工具目的）时，你可以尝试修改参数再次调用工具。三次尝试失败后请给出适当的抱歉回复，表示工具调用出错。\n"}, 
    #             {"role": "user", "content": "明天香港天气"}
    #         ]
    functions=[{
  "name": "concat_excels",
  "description": "Concatenate multiple Excel files that match a pattern into a single Excel file.",
  "parameters": {
    "type": "object",
    "properties": {
      "pattern": {
        "type": "string",
        "description": "The file pattern to match Excel files (e.g., '*.xlsx')."
      }
    },
    "required": ["pattern"]
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
                    "images"
                ]
            }
        }]
    messages=[
        {'role':'system','content':''},
        {'role': 'user', 'content': '你好'}
        ]
    # print(llm.chat(data['messages'],functions,response_format=data['response_format']))
    # print(llm.chat(messages,functions,response_format=response_format))
    print(llm.chat(messages))
    # print(llm.count_tokens(messages,functions))