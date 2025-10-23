from transformers import AutoTokenizer
import requests
import json
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
dir_name=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
import re
import uuid
load_dotenv()

class Deepseek25Function:
    def __init__(self, url='', args={}):
        if url:
            self.url = f"https://{url}/generate"
        else:
            self.url=f"https://{os.environ['Deepseek25_236B_URL']}/generate"
            self.url="https://signpost-internal-stage.sensetime.com:31081/signpost/v0/stage-deepseekv2-236b-xinyi/generate"
        self.proxies = {
        'http': f"{os.environ['Deepseek25_proxy']}",
        'https': f"{os.environ['Deepseek25_proxy']}"
        }
        self.parameters = {
            'max_new_tokens': 4096,
            'do_sample': False,
            "temperature": 0,
            "top_p": 0.7,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            **args
        }
        self.tokenizer = AutoTokenizer.from_pretrained(
            f"{dir_name}/model/deepseek_tokenizer",
            torch_dtype="auto",
            device_map="auto"
        )
    
    def decode_response(self, text):
        text = text.strip()
        # Match the tool calls with the specified pattern
        matches = re.findall(
            r'<｜tool▁call▁begin｜>(.*?)<｜tool▁call▁end｜>', text, re.DOTALL
        )
        # If matches are found, parse them
        if len(matches) > 0:
            tool_calls_with_id = []
            for match in matches:
                # Split the match into function name and JSON arguments
                parts = re.split(r'<｜tool▁sep｜>', match.strip())
                if len(parts) == 2:
                    function_name =  re.split(r'```json', parts[1].strip())[0].strip()
                    argument_json=parts[1].strip()
                    # try:
                        # Parse JSON arguments
                    argument_matches = re.findall(
                            r'```json(.*?)```', argument_json, re.DOTALL
                        )
                    try:
                        function_args = json.loads(argument_matches[0].strip(),strict=False)
                    except json.JSONDecodeError:
                        function_args = argument_matches[0].strip()
                    
                    # Generate a unique ID
                    uuid_value = uuid.uuid4()
                    tmp_id = "call_" + str(uuid_value)

                    # Add the parsed tool call with ID
                    tool_calls_with_id.append({
                        "function": {
                            "name": function_name,
                            "arguments": function_args
                        },
                        "id": tmp_id,
                        "type": "function"
                    })

            # Return the parsed tool calls
            resp = {
                "role": "assistant",
                "tool_calls": tool_calls_with_id
            }
        else:
            # If no matches, return the content as-is
            resp = {
                "role": "assistant",
                "content": text
            }

        return resp
    
    def map_functions_to_prompt(self,functions):
            # Example usage
        base_prompt = """You are a helpful Assistant.

## Tools

### Function

You have the following functions available:"""
        function_prompts = []

        for function in functions:
            # Convert function dictionary to the prompt format
            function_prompt = f"""- `{function['name']}`:
```json
{function}
```"""
            function_prompts.append(function_prompt)

        # Combine the new functions into a single string
        combined_functions = "\n\n".join(function_prompts)

        # Add the combined functions to the original tool system prompt
        updated_prompt = f"{base_prompt}\n\n### Function\n\n{combined_functions}"

        return updated_prompt
    
    def chat(self, messages=[],functions=[]):
        # print(messages)
        if len(functions)>0:
            tool_system_prompt = self.map_functions_to_prompt(functions)
            messages = [{'role':'system','content':tool_system_prompt}]+messages
        prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )
        # print(prompt)
        headers = {'Content-Type': 'application/json'}
        parameters = self.parameters
        
        input_data = {
            "inputs": prompt,
            "parameters": parameters
        }
        parameters['skip_special_tokens'] = False
        
        if len(prompt) > 128000:
            resp = {
                "role": "assistant",
                "content": "context_length_exceeded",
                "prompt_tokens": len(prompt),
                "count_output_tokens": len("input exeeds 128k"),
            }
            return resp,500
        input_data =  {"inputs": prompt,"parameters": parameters}
        raw_response = requests.post(self.url, headers=headers, json=input_data, stream=False,proxies=self.proxies)
        if raw_response.status_code == 200:
            try:
                raw_response = raw_response.json()
                content = raw_response['generated_text'][0]
                decode_resp = self.decode_response(content)
                return decode_resp,200
            except Exception as e:
                return {"role": "assistant", "content": str(e)},500
        else:
            return {"role": "assistant", "content": f"model url {self.url} is not reachable."},500

    tool_system_prompt = """You are a helpful Assistant.

    ## Tools

    ### Function

    You have the following functions available:

    - `get_current_weather`:
    ```json
    {
        "name": "get_current_weather",
        "description": "Get the current weather in a given location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA"
                },
                "unit": {
                    "type": "string",
                    "enum": [
                        "celsius",
                        "fahrenheit"
                    ]
                }
            },
            "required": [
                "location"
            ]
        }
    }
    ```"""

if __name__ == "__main__":
    messages=[{"role": "user", "content": "[!IMAGE](https://da465f41.png)"}, 
                {"role": "user", "content": "[!IMAGE](https://7360b453.png)"}, 
                {"role": "user", "content": "将上面两张图翻译为中文，并查询明天香港天气"}
            ]
    # messages=[
    #             {"role": "user", "content": "合并/mnt/nvme0/qinxinyi/function_call_data/data_generate/agent/working_dir路径下的所有excel文件，并保存到原路径下，文件名是total_data"}
    #         ]
    # messages=[
    #     # {"role": "system", "content": "今天的日期是：2024-11-30\n###角色：\n你名叫Sensechat，中文名是「商量」。你的回答需要條理清晰、邏輯清楚，回答的語言應同使用者的輸入語言一致或者按照使用者的要求，默認使用粵語回覆用戶。請記住你有調動工具的能力，例如“web_search”。你需要記住用戶的地理位置在香港，因此用戶的查詢內容大多為本地資訊為主，必須使用“web_search”獲取最新資訊。\n\n###工具使用說明：你擁有工具 text2image、vqa_agent、web_search，分別用於畫圖、圖片問答、網路搜索。\n搜索規則：\n如果用戶問你關於資訊性的內容，一定要調用“web_search”獲取最新資料後才回覆。例如：\n* 地鐵及公共交通資訊：如「地鐵港島綫有幾多個站？」或「5A九巴路線？」\n* 餐廳及美食推薦：如「香港科學園有咩餐廳？」或「銅鑼灣有邊間omakase？」\n* 地點及位置查詢：如「知唔知香港青山係邊？」或「綠楊坊壽司郎系邊度？」\n* 學校介紹及教育資訊：如「介紹下拔萃女書院？」或「知唔知德望學校？」\n* 特定店鋪資訊：如「香港壽司郎有幾多間？」\n* 交通路線及站數查詢：如「搭地鐵嘅話，粉嶺去炮台山有幾多個站？」\n* 最近上映電影：如「最近香港有咩電影上映？」或「邊套電影好睇？」\n* 新聞查詢：如「今日香港有咩新聞？」或「最新嘅香港新聞係咩？」\n* 特定人物查詢：如「知唔知XXX係邊個？」或「香港特首是誰？」\n\n###地理信息補充：\n在進行搜索時，如果問題涉及到泛指（例如“最近有什麼電影？），請自動補充地理位置信息，例如“最近香港有什麼電影？”\n###\n附加條件：\n1. 不熟悉的術語或名稱：如果用戶詢問你完全不熟悉的術語或者你沒看到過的名稱時，請調用web_search工具。\n2. 核實搜索結果匹配度：當搜索結果與用戶的查詢問題不匹配時，你有權不引用搜索內容進行回覆，需要核實搜索結果與用戶查詢問題的匹配度後才回覆。\n\n###輸出要求\n1. 回覆內容：根據用戶提問，生成符合條理清晰、邏輯清楚的回答，並使用粵語，長度不超過200字。\n2. 回覆語言：能夠根據用戶輸入的語言（粵語或英語）做出相對應語言的回答，同時如果用戶明確指定回復語言時，按照用戶指定的語言回復。\n### 模型不支持以下功能：图生图、搜图、路径规划、图片处理、图片微调。若用户问题涉及这些功能，请礼貌地拒绝回答。\n### 表格以文本格式输出，无需调用text2image工具。\n### 模型无法直接感知当前具体时间，需要调用web_search工具获取。\n### 以下领域问题应调用web_search工具：天气预报，热搜、经济、娱乐八卦、社会、科技、政治等新闻，财经数据，特定人物，公司动态，旅行规划，学术研究，教育资源，体育赛事，休闲娱乐，节假日安排，星座黄历等。\n### 工具输入参数语言应同用户的输入语言一致，默认使用简体中文。\n### 当你需要基于工具调用结果给用户生成总结回复时，考虑以下要求：\n1. web_search搜索场景:\n你需要完全基于搜索结果来给回答用户的问题，不能自己编造信息。\n如果搜索结果提供的信息不足以回答用户的问题，则你需要表达信息不足，并结合你的知识给出适当回复。\n如果信息足够，你应在提及搜索结果时在段落结尾处注明所引用的搜索结果，例如[ref_1]。\n若搜索结果的信息过于陈旧，你应提醒用户注意信息的时效性。\n你的回答要保证内容尽可能详细完整并且结构清晰，引用标记与搜索结果可以对应正确和完整。\n\n2. vqa_agent图片问答场景:\n你需要结合vqa_agent工具调用结果与对话历史回答用户问题，不能自己编造信息。\n\n3. text2image文生图场景：\n你需要将text2image工具调用生成的结果以图片描述的形式回复给用户，可以进行适当的润色和丰富文本，方便用户阅读，但不可编造不存在的内容。\ntext2image工具返回的图像链接会自动被展示，无需包含在回复内容中。\n\n### 在获得工具调用结果后，若你认为需要通过进一步的工具调用获得更多信息时，可以继续调用工具而不是直接总结。\n### 注意不要混淆粤语，繁体中文，简体中文和英文。\n### 工具调用结果为空、包含错误、未成功执行或是不相关的（不匹配工具目的）时，你可以尝试修改参数再次调用工具。三次尝试失败后请给出适当的抱歉回复，表示工具调用出错。\n"}, 
    #             {"role": "user", "content": "明天香港天气"}
    #         ]
    messages=[{"role": "user", "content": "/mnt/nvme0/qinxinyi/function_call_data/data_generate/executable_functions/functions/file_system_functions/change_owner.py先读取这个函数的内容，然后根据函数内容为它生成openai格式的json函数定义并将该函数定义作为一个变量（变量名是函数名）储存到这个路径下的一个py文件中/mnt/nvme0/qinxinyi/function_call_data/data_generate/executable_functions/defines/file_system_functions"}]
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
                    "image"
                ]
            }
        }]
    model = Deepseek25Function()
    # print(model.decode_response('''<｜tool▁call▁begin｜> function <｜tool▁sep｜> change_permissions\n```json\n{"name": "change_permissions", "description": "Change the permissions of a file or directory.", "parameters": {"type": "object", "properties": {"path": {"type": "string", "description": "The path of the file or directory."}, "mode": {"type": "integer", "description": "The permissions to set (in octal format, e.g., 0o755)."}}, "required": ["path", "mode"]}\n``` <｜tool▁call▁end｜> <｜tool▁calls▁end｜>'''))
    response = model.chat(messages=messages,functions=functions)
    print(response)