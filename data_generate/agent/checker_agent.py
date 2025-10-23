# -*- coding: utf-8 -*-
# To do
import json
from pydantic import BaseModel,Field, SecretStr, model_validator
from typing import List, Dict, Any, Optional
from colorama import Fore, Style
from typing import Union
import re
from data_generate.prompt.checker_prompt import *
from data_generate.agent.model import *
import os
from collections import defaultdict
import logging
logger = logging.getLogger(__name__)

class CheckerAgent(BaseModel):
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
        elif 'qwq' in self.llm_name:
            self.llm = QwQFunction(args={'temperature': 0.7})
        elif 'deepseek' in self.llm_name:
            self.llm = Deepseek25Function(args={'temperature': 0.7})
        else:
            raise NameError('not support')
        return self

    def _tool_call_check(self, message: Dict[str, Any], dummy_dialogs: List,tools: List):
        try:
            tool_calls_id = []
            # tool_calls= []
            for tool_call in message["tool_calls"]:
                # tool_calls.append(tool_call["function"])
                tool_calls_id.append(tool_call['id'])
            # 规则检查(若无法通过规则则直接返回错误)
            try:
                advices=self._tool_call_rule_checker(message,tools,dummy_dialogs)
            except Exception as e:
                raise Exception(f'rule checker error: {e}, assistant_message: {message}')
            
            if any(advices):
                advice_message=[]
                for i,id in enumerate(tool_calls_id):
                    advice_content=advices[i] if advices[i] else None
                    advice_message+=[{'role':'tool','tool_call_id':id,'content':advice_content}]
                logger.info(f'{Fore.RED}CHECKER RESPONSE(NOT PASS):{Style.RESET_ALL} {Fore.WHITE}{advice_message}{Style.RESET_ALL}')
                return advice_message,200,False

            # llm检查(通过规则后再通过llm检查)
            TOOL_CALL_CHECK_TEMPLET = {'context_history': dummy_dialogs, 'tool_name_and_parameter': [call['function'] for call in message['tool_calls']]}

            check_message = [
                {'role': 'system', 'content': TOOL_CALL_CHECK_SYSTEM_PROMPT + CHECKER_TOOL_CALL_RESPONSE_FORMAT_PROMPT},
                {'role': 'user', 'content': TOOL_CALL_CHECK_USER_PROMPT.format(**TOOL_CALL_CHECK_TEMPLET)}]
            # print(check_message)
            gpt_output,error_code = self.llm.chat(check_message,tools)
            # print(gpt_output)
            if error_code==200:
                if '<advice>' in gpt_output['content']:
                    matches = re.findall(r'<advice>\s*(.*?)\s*</advice>', gpt_output['content'], re.DOTALL)
                    # Parse each match as a JSON object
                    try:
                        advices = [json.loads(match) for match in matches]
                        # advices = [{tool:text} for advice in advices for tool,text in advice.items() if text!='无']
                        advices = [{tool: text} for advice in advices for tool, text in advice.items() \
                                   if text != 'None']
                    except:
                        advices = [str(match) for match in matches] if matches else []
                else:
                    advices = []

                if not advices:
                    # logger.debug(f'{Fore.GREEN}CHECKER PROMPT:{Style.RESET_ALL} {Fore.WHITE}{check_message}{Style.RESET_ALL}')
                    logger.info(f'{Fore.GREEN}CHECKER RESPONSE(PASS):{Style.RESET_ALL} {Fore.WHITE}None{Style.RESET_ALL}')
                    return None,200,True
                else:
                    # print(f'{Fore.GREEN}CHECKER PROMPT:{Style.RESET_ALL} {Fore.WHITE}{check_message}{Style.RESET_ALL}')
                    advice_message=[]
                    for i,id in enumerate(tool_calls_id):
                        try:
                            if advices[i]:
                                advice_content={'advice':advices[i]}
                            else:
                                advice_content = {'advice': 'None'}
                        except:
                            # advice_content={'advice':'无'}
                            advice_content = {'advice': 'None'}
                        advice_message+=[{'role':'tool','tool_call_id':id,'content':TOOL_CALL_ADVICE_PROMPT.format(**advice_content)}]
                    logger.info(f'{Fore.RED}CHECKER RESPONSE(NOT PASS):{Style.RESET_ALL} {Fore.WHITE}{advice_message}{Style.RESET_ALL}')
                    return advice_message,200,False
            else:
                return gpt_output['content'],500,False
        except Exception as e:
            import traceback
            logger.error(f'{Fore.RED}CHECKER ERROR:{Style.RESET_ALL} {Fore.WHITE}{str(e)}{Style.RESET_ALL}')
            traceback.print_exc()
            return str(e),500,False


    # 工具调用的规则检测
    def _tool_call_rule_checker(self, message, tools, history_dialogs):
        valid_types = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict,
            "null": type(None)
        }
        tool_call_history=defaultdict(int)
        for history_message in history_dialogs:
            if 'tool_calls' in history_message:
                for tool_call in history_message['tool_calls']:
                    tool_call=(tool_call['function']['name'],tool_call['function']['arguments'])
                    tool_call_history[tool_call]+=1

        def has_duplicates(dict_list):
            dict_list=[function_call['function'] for function_call in dict_list]
            seen = set()  # 用于记录已见过的字典
            for d in dict_list:
                # 将字典转换为 JSON 字符串，确保字典嵌套结构也能被正确比较
                dict_str = json.dumps(d, sort_keys=True)  # `sort_keys=True` 保证顺序一致性
                if dict_str in seen:
                    return True  # 如果发现重复的字典
                seen.add(dict_str)
            return False  # 没有重复

        all_tools={}
        for tool in tools:
            tool_name=tool['name']
            arguments={key:value['type'] if 'type' in value else [item['type'] for item in value['oneOf']] for key,value in tool["parameters"]["properties"].items()}
            all_tools[tool_name]={'arguments':arguments,'required':tool["parameters"]["required"] if "required" in tool["parameters"] else []}
        tool_calls=message['tool_calls']
        advices=[]
        for tool_call in tool_calls:
            advice=[]
            if tool_call['function']['name'] not in all_tools:
                advice.append(f'''Tool "{tool_call['function']['name']}" is not in the available tool list. Available tools: {list(all_tools.keys())}''')
            else:
                tool_call_tuple=(tool_call['function']['name'],tool_call['function']['arguments'])
                if tool_call_history.get(tool_call_tuple,0)>=3:
                    advice.append(f'You have called the "{tool_call["function"]["name"]}" tool with the same arguments `{tool_call["function"]["arguments"]}` more than 3 times.')
                if type(tool_call['function']['arguments']) is str:
                    arguments=json.loads(tool_call['function']['arguments'])
                else:
                    arguments=tool_call['function']['arguments']
                for argument_name,value in arguments.items():
                    if argument_name not in all_tools[tool_call['function']['name']]["arguments"]:
                        advice.append(f'''Parameter "{argument_name}" is not in the parameter list of the "{tool_call['function']['name']}" tool. Available parameter(s) for tool: {list(all_tools[tool_call["function"]["name"]]["arguments"].keys())}''')
                    else:
                        argument_type=all_tools[tool_call['function']['name']]["arguments"][argument_name]
                        if type(argument_type) is list:
                            if all([not isinstance(value, valid_types.get(type)) for type in argument_type]):
                                advice.append(f'unmatch data type for argument "{argument_name}": "{value}", required type: "{argument_type}"')
                        else:
                            if not isinstance(value, valid_types.get(argument_type)):
                                advice.append(f'unmatch data type for argument "{argument_name}": "{value}", required type: "{argument_type}"')
                for require_argument in all_tools[tool_call['function']['name']]["required"]:
                    if require_argument not in arguments:
                        advice.append(f'''Tool "{tool_call['function']['name']}" lack of required argument: {require_argument}''')
            advice=[f'{num+1}. {item}' for num,item in enumerate(advice)]
            advice='\n'.join(advice)
            advices.append(advice)
        if has_duplicates(tool_calls):
            advices[0]='Duplicate tool calls in parallel calls.\n'+advices[0]
        return advices
    
    @staticmethod
    def extract(dummy_dialogs):
        # 提取最后的工具回复和用户问题
        last_user_index = -1
        last_assistant_index = -1
        cnt=0
        for i in range(len(dummy_dialogs) - 1, -1, -1):
            # print(new_messages[i])
            if 'content' in dummy_dialogs[i]:
                if dummy_dialogs[i]['role'] == 'user' and (not type(dummy_dialogs[i]['content']) is list):
                    cnt+=1
                    last_user_index = i
                elif dummy_dialogs[i]['role'] == 'user' and type(dummy_dialogs[i]['content']) is list:
                    last_user_index = i
                elif dummy_dialogs[i]['role'] == 'assistant':
                    last_assistant_index = i
                if cnt==1 and not (type(dummy_dialogs[i-1]['content']) is list):
                    break
        if dummy_dialogs[-1]['role']=='tool':
            history=dummy_dialogs[:last_user_index]
            user_messages = dummy_dialogs[last_user_index:last_assistant_index]
            assistant_tool_messages = dummy_dialogs[last_assistant_index:]
            return history,user_messages,assistant_tool_messages
        else:
            history=dummy_dialogs[:last_user_index]
            user_messages = dummy_dialogs[last_user_index:]
            return history,user_messages,None
        

    def _llm_check(self, message: Dict[str, Any], dummy_dialogs: List,tools: List):
        # 把对话拆分为历史、当前用户问题、模型调用工具及工具回复、当前模型回复
        try:
            history,user_messages,assistant_tool_messages=self.extract(dummy_dialogs)
            LLM_CHECK_TEMPLET = {'context_history': json.dumps(history,ensure_ascii=False),
                                'user_messages':json.dumps(user_messages,ensure_ascii=False),
                                'assistant_tool_messages':json.dumps(assistant_tool_messages,ensure_ascii=False),
                                'assistant_response':json.dumps(message,ensure_ascii=False)}
            # LLM_CHECK_REQUEST = LLM_CHECK_PROMPT.format(**LLM_CHECK_TEMPLET)+CHECKER_LLM_RESPONSE_FORMAT_PROMPT
            # check_message = [{'role': 'user', 'content': LLM_CHECK_REQUEST}]
            check_message = [
                {'role': 'system', 'content': LLM_CHECK_SYSTEM_PROMPT + CHECKER_LLM_RESPONSE_FORMAT_PROMPT},
                {'role': 'user', 'content': LLM_CHECK_USER_PROMPT.format(**LLM_CHECK_TEMPLET)}]
            gpt_output, error_code = self.llm.chat(check_message, tools)
            # print(gpt_output)
            if error_code==200:
                if '<advice>' in gpt_output['content']:
                    matches = re.findall(r'<advice>\s*(.*?)\s*</advice>', gpt_output['content'], re.DOTALL)
                    # Parse each match as a JSON object
                    try:
                        advices = [json.loads(match, strict=False) for match in matches]
                        # advices = [{number:text} for advice in advices for number,text in advice.items() if text!='无']
                        advices = [{number: text} for advice in advices for number, text in advice.items() \
                                   if text != 'None']
                    except:
                        advices = [str(match) for match in matches] if matches else []
                else:
                    advices = []
                if not advices:
                    # logger.debug(f'{Fore.GREEN}CHECKER PROMPT:{Style.RESET_ALL} {Fore.WHITE}{check_message}{Style.RESET_ALL}')
                    logger.info(f'{Fore.GREEN}CHECKER RESPONSE(PASS):{Style.RESET_ALL} {Fore.WHITE}None{Style.RESET_ALL}')
                    return None,200,True
                else:
                    if type(advices[0]) is dict:
                        advices=[f'{number}: {text}'for advice in advices for number,text in advice.items()]
                        advice_format={'advice':'\n'.join(advices)}
                    else:
                        advice_format={'advice':'\n'.join(advices)}
                    advice_message={'role':'user','content':LLM_ADVICE_PROMPT.format(**advice_format)}
                    # logger.debug(f'{Fore.RED}CHECKER PROMPT:{Style.RESET_ALL} {Fore.WHITE}{check_message}{Style.RESET_ALL}')
                    logger.info(f'{Fore.RED}CHECKER RESPONSE(NOT PASS):{Style.RESET_ALL} {Fore.WHITE}{advice_message}{Style.RESET_ALL}')
                    return [advice_message],200,False
            else:
                return gpt_output,500,False
        except Exception as e:
            return str(e),500,False
    
if __name__ == '__main__':
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] [%(levelname)s] [Thread:%(threadName)s - %(thread)d]\n%(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger = logging.getLogger(__name__)
    checker_agent = CheckerAgent(llm_name='qwen')
    message = {'role': 'assistant', 'tool_calls': [{'function': {
        'arguments': '{"prompt": "a cute kitten playing with a ball of yarn, photorealism style, soft lighting, warm colors"}',
        'name': 'text2image'}, 'id': 'call_lA2PijMhibsMdToaNgR0O8EJ', 'type': 'function'}, {
                                                       'function': {'arguments': '{"query": "上海天气"}',
                                                                    'name': 'web_search'},
                                                       'id': 'call_g14rD9RtGrJhaCvyElg8Dosr', 'type': 'function'}]}
    dummy_dialogs = [
        {'role': 'system', 'content': '今天的日期是：2024-12-31\r\n角色：\r\n你是SenseChat，中文名是「商量」。你的回答需要条理清晰、逻辑清楚，回答的语言应同用户的输入语言一致或者按照用户的要求。\n### 模型不支持除了给定工具以外的其他功能，若用户问题涉及其他功能，请礼貌地拒绝回答。\n### 工具输入参数语言应默认跟随用户的输入语言或用户指定的语言。\n### 在调用工具前，需要确保工具的所有必需参数都是客观存在的，不能编造不存在的参数信息。\n### 注意信息的时效性和匹配性，不要用陈旧或错误的信息回答用户。\n### 注意不要混淆粤语，繁体中文，简体中文和英文。\n### 工具调用结果为空、包含错误、未成功执行或是不相关的（不匹配工具目的）时，你可以尝试修改参数再次调用工具。三次尝试失败后请给出适当的抱歉回复，表示工具调用出错。\n'},
        {'role': 'user', 'content': "在处理这些缺失的归还日期时，我倾向于采用估算归还日期的方法。但是，为了更准确地估算，我需要了解整个数据库中电影的平均租赁期限。您能否帮我计算一下2005年和2006年期间所有电影的平均租赁期限？这将有助于我更精确地填充这些缺失值。"},
                     ]
    message={'role': 'assistant', 'tool_calls': [{'function': {'arguments': '{\"query\":\"你好\", \"limit\": \"5\"}', 'name': 'duckduckgo_websearch'}, 'id': 'call_HmUofPDqIbpkWMBQa5DhqjE9', 'type': 'function'}, 
    {'function': {'arguments': '{\"database_path\": \"airlines\", \"table_name\": \"tickets\", \"group_by\": \"passenger_id\"}', 'name': 'duckduckgo_websearch'}, "id": "call_PCe2XVAY4XNomZ7OGEvFkyga", "type": "function"}]}
    
    from data_generate.utils import load_tool_defines
    # executable_tools=load_tool_defines('./tools/defines/',True)
    executable_tools=load_tool_defines(f'{os.environ["PROJECT_DIR"]}/tools/defines/api_functions')
    tools=list(executable_tools.values())
    if 'tool_calls' in message:
        checker_agent._tool_call_check(message, dummy_dialogs, tools)
    else:
        checker_agent._llm_check(message, dummy_dialogs, tools)
