import requests
import json
import io
import os

default_url = "http://api.schedule.mtc.sensetime.com"

def msgsToJsonlReader(msgs: list):
    res_str = ""
    for msg in msgs:
        res_str += json.dumps(msg, ensure_ascii=False) + "\n"
    bytes_str = bytes(res_str, encoding="utf-8")
    return io.BufferedReader(io.BytesIO(bytes_str), len(bytes_str))

def check_parameters(obj):
    choices_set = set([
        "stop", "user", 
        "tool_choice", "tools", "function_call", "functions", 
        "response_format", "azure_extensions", "enhancements",
        "max_tokens", "frequency_penalty", "logit_bias", 
        "presence_penalty", "temperature", "top_p", "n", "seed", 
        "top_logprobs"])
    for key in obj.keys():
        if key not in choices_set:
            raise Exception(f'parameter {key} must in {choices_set}')
    return

class GptProxy:
    TASKNOTSTART = 0
    TASKRUNNING = 1
    TASKFINISH = 2
    def __init__(self, api_key = None, base_url = None):
        if not base_url:
            global default_url
            base_url = default_url
            # print(f"set url: {base_url}")
        self.url_base = f"{base_url}"
        if api_key == None:
            g_api_key = os.environ.get("API_KEY", "")
            if g_api_key == "":
                raise Exception("API_KEY env not set!!")
            self.headers = {"api-key": g_api_key}
        else:
            self.headers = {"api-key": api_key}

    def _get(self, url, params = {}):
        return requests.get(url, headers= self.headers, params=params)

    def _post_json(self, url, json_data={}, params={}):
        headers = self.headers
        headers['Content-Type'] = 'application/json'
        data = json.dumps(json_data, ensure_ascii=False).encode('utf8')
        return requests.post(url, headers=headers, params=params, data=data)
    
    def _post_file(self, url, files, params={}):
        return requests.post(url, headers=self.headers, params=params, files=files)

    def generate(self, 
                 *,
                 messages, 
                 model,
                 transaction_id,
                 **kwargs
                 ):
        url = f"{self.url_base}/gateway/chatTask/callResult"
        data = {
            "server_name": "test",
            "model": model,
            "messages": messages,
            "transaction_id":transaction_id,
            **kwargs,
        }
        rsp = self._post_json(url=url, json_data=data)
        return rsp
    
    def taskList(self, status = [], is_async=1, server_name = "", page = 1, page_size = 100):
        url = f"{self.url_base}/gateway/chatTask/getList"
        params = {"page": page, "page_size": page_size}
        if server_name != "":
            params["server_name"] = server_name
        params["is_async"] = is_async
        res_obj = {'list': [], 'total': 0}
        for sta in status:
            params["status"] = sta
            rsp = self._get(url, params)
            _obj = rsp.json()['data']
            # print(_obj)
            res_obj['list'].extend(_obj['list'])
            res_obj["total"] += len(_obj['list'])
        return res_obj

    def taskCreate(self, file_path, transaction_id, server_name, model, priority=800, **kwargs):
        """
        priority越高越先执行，默认800.用户设置的范围是0~1000
            默认的，不要修改优先级.
            如果是大任务且不紧急，请将优先级修改为0.
            如果是评测类小任务希望快速获得结果，请将优先级设置为1000
        """
        check_parameters(kwargs)
        url = f"{self.url_base}/gateway/chatTask/import"
        files = {
            "transaction_id": (None, transaction_id), 
            "server_name": (None, server_name),
            "model": (None, model),
            "priority": (None, str(priority)),
            'messages_file': (os.path.basename(file_path), open(file_path, 'rb'), "text/plain"),
        } 
        for k, v in kwargs.items():
            files[k] = (None, json.dumps(v))
        rsp = self._post_file(url, files, )
        return json.loads(rsp.text)
    
    def taskCreateMem(self, msg_list, transaction_id, server_name, model, priority=800, **kwargs):
        check_parameters(kwargs)
        url = f"{self.url_base}/gateway/chatTask/import"
        files = {
            "transaction_id": (None, transaction_id), 
            "server_name": (None, server_name),
            "model": (None, model),
            "priority": (None, str(priority)),
            'messages_file': ("tmp_inputs.jsonl", msgsToJsonlReader(msg_list), "text/plain"),
        } 
        for k, v in kwargs.items():
            files[k] = (None, json.dumps(v))
        rsp = self._post_file(url, files, )
        return json.loads(rsp.text)
    
    def taskInfoGet(self, transaction_id):
        url = f"{self.url_base}/gateway/chatTask/getInfo"
        params = {"transaction_id": transaction_id}
        try_count = 0
        while True:
            rsp = self._get(url, params)
            if rsp.ok:
                break
            try_count += 1
            if try_count > 3:
                raise Exception("taskInfoGet failed, try 3 times")
        # print(rsp.text)
        return rsp.json()