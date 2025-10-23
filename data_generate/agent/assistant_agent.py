# -*- coding: utf-8 -*-
from pydantic import BaseModel,Field, model_validator
from typing import List, Dict, Any, Optional
from datetime import datetime
from colorama import Fore, Style
from typing import Union
from data_generate.agent.model import *
import logging
logger = logging.getLogger(__name__)

class AssistantAgent(BaseModel):
    llm: Union[DOUBAOFunction, ChatGPTFunction,QWen25Function,QwQFunction] = Field(default=None)
    llm_name: str = 'gpt4o-ptu-client'
    llm_type: str = 'chat'

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
            self.llm_type='reasoning'
        else:
            raise NameError('not support')
        return self
    
    def _generate(self,messages: Dict[str, Any],tools:List=[],n: int=1) -> List[Dict[str, Any]]:
        if self.llm_type=='chat':
            outputs=[]
            for i in range(n):
                output, error_code = self.llm.chat(messages,tools)
                logger.info(f'{Fore.YELLOW}ASSISTANT RESPONSE:{Style.RESET_ALL} {Fore.WHITE}{output}{Style.RESET_ALL}')
                
                if error_code==200:
                    outputs.append(output)
                else:
                    return output,error_code
            return outputs,200

        elif self.llm_type=='reasoning':
            outputs=[]
            reasonings=[]
            for i in range(n):
                output, reasoning, error_code = self.llm.chat(messages,tools,include_reasoning=True)
                logger.debug(f'{Fore.YELLOW}ASSISTANT THINKING:{Style.RESET_ALL} {Fore.WHITE}{reasoning}{Style.RESET_ALL}')
                logger.info(f'{Fore.YELLOW}ASSISTANT RESPONSE:{Style.RESET_ALL} {Fore.WHITE}{output}{Style.RESET_ALL}')
                if error_code==200:
                    outputs.append(output)
                    reasonings.append(reasoning)
                else:
                    return output,reasoning,error_code
            return outputs,reasonings,200


if __name__ == '__main__':
    import logging

    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] [%(levelname)s] [Thread:%(threadName)s - %(thread)d]\n%(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger = logging.getLogger(__name__)

    assistant_agent = AssistantAgent(llm_name='qwq')
    FILE_TOOL_PROMPT = """
Operating System-related Tools Notes:

1.Default Working Root Path: The default working root path is set to './'.
2.Unknown File Path: If the file path is not known in advance, always begin by using the <display_directory_tree> tool to retrieve a comprehensive list of directory contents and file paths.
3.Unknown File Information: If specific file information (e.g., column names) is unclear before performing queries or operations, start by utilizing the <read_file_contents> tool to examine the relevant file details.
"""
    # messages=[
        # {'role':'system','content': FILE_TOOL_PROMPT},
        # {'role': 'user', 'content':'Can you find all files in the txt_data directory that contain the word \"life\" and let me know which files they are?'}]
    messages=[{'role': 'user', 'content':'你好'}]
    # messages=[{'role': 'user', 'content': [{'type': 'text', 'text': 'User uploaded an image here："https://3d7c0045.png"'}]}, {'role': 'user', 'content': '描述图片的内容'}]
    # messages=[{"role": "system", "content": "今天的日期是：2024-11-14\n###角色：\n你名叫Sensechat，中文名是「商量」。你的回答需要條理清晰、邏輯清楚，回答的語言應同使用者的輸入語言一致或者按照使用者的要求，默認使用粵語回覆用戶。請記住你有調動工具的能力，例如“web_search”。你需要記住用戶的地理位置在香港，因此用戶的查詢內容大多為本地資訊為主，必須使用“web_search”獲取最新資訊。\n\n###工具使用說明：你擁有工具 text2image、vqa_agent、web_search，分別用於畫圖、圖片問答、網路搜索。\n搜索規則：\n如果用戶問你關於資訊性的內容，一定要調用“web_search”獲取最新資料後才回覆。例如：\n* 地鐵及公共交通資訊：如「地鐵港島綫有幾多個站？」或「5A九巴路線？」\n* 餐廳及美食推薦：如「香港科學園有咩餐廳？」或「銅鑼灣有邊間omakase？」\n* 地點及位置查詢：如「知唔知香港青山係邊？」或「綠楊坊壽司郎系邊度？」\n* 學校介紹及教育資訊：如「介紹下拔萃女書院？」或「知唔知德望學校？」\n* 特定店鋪資訊：如「香港壽司郎有幾多間？」\n* 交通路線及站數查詢：如「搭地鐵嘅話，粉嶺去炮台山有幾多個站？」\n* 最近上映電影：如「最近香港有咩電影上映？」或「邊套電影好睇？」\n* 新聞查詢：如「今日香港有咩新聞？」或「最新嘅香港新聞係咩？」\n* 特定人物查詢：如「知唔知XXX係邊個？」或「香港特首是誰？」\n\n###地理信息補充：\n在進行搜索時，如果問題涉及到泛指（例如“最近有什麼電影？），請自動補充地理位置信息，例如“最近香港有什麼電影？”\n###\n附加條件：\n1. 不熟悉的術語或名稱：如果用戶詢問你完全不熟悉的術語或者你沒看到過的名稱時，請調用web_search工具。\n2. 核實搜索結果匹配度：當搜索結果與用戶的查詢問題不匹配時，你有權不引用搜索內容進行回覆，需要核實搜索結果與用戶查詢問題的匹配度後才回覆。\n\n###輸出要求\n1. 回覆內容：根據用戶提問，生成符合條理清晰、邏輯清楚的回答，並使用粵語，長度不超過200字。\n2. 回覆語言：能夠根據用戶輸入的語言（粵語或英語）做出相對應語言的回答，同時如果用戶明確指定回復語言時，按照用戶指定的語言回復。\n### 模型不支持以下功能：图生图、搜图、路径规划、图片处理、图片微调。若用户问题涉及这些功能，请礼貌地拒绝回答。\n### 表格以文本格式输出，无需调用text2image工具。\n### 模型无法直接感知当前具体时间，需要调用web_search工具获取。\n### 以下领域问题应调用web_search工具：天气预报，热搜、经济、娱乐八卦、社会、科技、政治等新闻，财经数据，特定人物，公司动态，旅行规划，学术研究，教育资源，体育赛事，休闲娱乐，节假日安排，星座黄历等。\n### 工具输入参数语言应同用户的输入语言一致，默认使用简体中文。\n### 当你需要基于工具调用结果给用户生成总结回复时，考虑以下要求：\n1. web_search搜索场景:\n你需要完全基于搜索结果来给回答用户的问题，不能自己编造信息。\n如果搜索结果提供的信息不足以回答用户的问题，则你需要表达信息不足，并结合你的知识给出适当回复。\n如果信息足够，你应在提及搜索结果时在段落结尾处注明所引用的搜索结果，例如[ref_1]。\n若搜索结果的信息过于陈旧，你应提醒用户注意信息的时效性。\n你的回答要保证内容尽可能详细完整并且结构清晰，引用标记与搜索结果可以对应正确和完整。\n\n2. vqa_agent图片问答场景:\n你需要结合vqa_agent工具调用结果与对话历史回答用户问题，不能自己编造信息。\n\n3. text2image文生图场景：\n你需要将text2image工具调用生成的结果以图片描述的形式回复给用户，可以进行适当的润色和丰富文本，方便用户阅读，但不可编造不存在的内容。\ntext2image工具返回的图像链接会自动被展示，无需包含在回复内容中。\n\n### 在获得工具调用结果后，若你认为需要通过进一步的工具调用获得更多信息时，可以继续调用工具而不是直接总结。\n### 注意不要混淆粤语，繁体中文，简体中文和英文。\n### 工具调用结果为空、包含错误、未成功执行或是不相关的（不匹配工具目的）时，你可以尝试修改参数再次调用工具。三次尝试失败后请给出适当的抱歉回复，表示工具调用出错。\n"}, {"role": "user", "content": "老公……有點痛……我向你撒嬌哭訴，以上用香港俗語怎麼說"}, {"role": "assistant", "content": "老公……有啲痛……我向你撒嬌哭訴，"}, {"role": "user", "content": "我努力放鬆身體，漸漸的就沒那麼痛了，取而代之的是空虛的感覺，以上用香港俗語怎麼說"}, {"role": "assistant", "content": "我努力放鬆身體，漸漸咁就唔咁痛喇，反而有種空虛嘅感覺，"}, {"role": "user", "content": "我感覺好舒服，開始叫床，以上用香港俗語怎麼說"}, {"role": "assistant", "content": "我覺得好舒服，開始叫床，"}, {"role": "user", "content": "我努力夾住你，舌頭伸出來想讓你親，以上用香港俗語怎麼說"}, {"role": "assistant", "content": "我努力夾住你，條脷伸出嚟想畀你鍚，"}, {"role": "user", "content": "我的閪剛剛開苞，十分緊致，不需要用力就可以夾緊你。以上用香港俗語怎麼說"}, {"role": "assistant", "content": "我個屄啱啱開苞，好緊緻，唔使點用力就可以夾實你。"}, {"role": "user", "content": "我感到你的精液射進我的體內，我們兩個雙雙高潮了。以上用香港俗語怎麼說呢"}, {"role": "assistant", "content": "我感到你嘅精液射入我體內，我哋兩個一齊高潮咗。"}, {"role": "user", "content": "都沒來得及  以上用香港俗語怎麼說"}, {"role": "assistant", "content": "都唔及時"}, {"role": "user", "content": "要不要我現在含下你的波呀，以上用香港俗語怎麼說呢"}]
    # print(assistant_agent._generate(messages))
    from data_generate.utils import load_tool_defines
    tools=load_tool_defines(f'{os.environ["PROJECT_DIR"]}/tools/defines/file_system_functions/',recursive=True)
    # # tools=load_tool_defines('./tools/defines/',True)
    print(assistant_agent._generate(messages,list(tools.values())[:1]))
