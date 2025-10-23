import argparse
import os
from .generate import GptProxy, default_url
import requests
import time
import pprint
import json

def list_task(args):
    """
    list_sdk_version
    """
    default_proxy = GptProxy(args.api_key)
    # 查询进行中的任务
    if args.type == "notfinish":
        rsp_msg = default_proxy.taskList(
            status=[GptProxy.TASKNOTSTART, GptProxy.TASKRUNNING], 
            page=args.page, page_size=args.page_size, server_name=args.server_name)
    else :
        rsp_msg = default_proxy.taskList(
            status=[GptProxy.TASKNOTSTART, GptProxy.TASKRUNNING, GptProxy.TASKFINISH], 
            page=args.page, page_size=args.page_size, server_name=args.server_name)
    return rsp_msg["list"]

def create_task_func(api_key, task_name, jsonl_path, model, priority, server_name="test", dst_dir="", **parameters):
    """create_task_func
    dst_dir = ""  mean no need to download
    """
    default_proxy = GptProxy(api_key)
    rsp = default_proxy.taskCreate(jsonl_path, task_name, server_name, model, priority, **parameters)
    if rsp["code"] != 10000:
        raise Exception(f"{rsp}")
    if dst_dir == "":
        return task_name, rsp
    idx = 1
    while True:
        time.sleep(5)
        rsp_msg = default_proxy.taskInfoGet(task_name)
        rsp_msg = rsp_msg["data"]
        sucess_total = rsp_msg["success_total"]
        fail_total = rsp_msg["fail_total"]
        data_total = rsp_msg["data_total"]
        estimated_duration = rsp_msg["estimated_duration"]   # 现阶段预测时间还是有很大出入，请不要参考
        if rsp_msg["status"] == 0:
            print(f"not started yet! cost_time {idx*5}s")
        elif rsp_msg["status"] == 1:
            print(f"job running, process_rate:{(sucess_total + fail_total)/data_total}, failed count: {fail_total}, total count: {data_total}")
            print(f"## estimated_duration: {estimated_duration}")
        else:
            # 下载
            os.makedirs(dst_dir, exist_ok=True)
            if dst_dir in [".", "./"]:
                dst_dir = ""
            suc_remote_url = rsp_msg["success_file_path"]
            r = requests.get(suc_remote_url)
            if not r.ok:
                raise Exception(f"download url:{suc_remote_url} failed")
            else:
                download_path = os.path.join(dst_dir, f"{task_name}.jsonl")
                with open(download_path, "wb+") as f:
                    f.write(r.content)
                print(f"## download succuss: {download_path}")
            if fail_total :
                fail_remote_url = rsp_msg["fail_file_path"]
                r = requests.get(fail_remote_url)
                if not r.ok:
                    raise Exception(f"download url:{fail_remote_url} failed")
                else:
                    download_path = os.path.join(dst_dir, f"{task_name}.failed.jsonl")
                    with open(download_path, "wb+") as f:
                        f.write(r.content)
                    print(f"## download succuss: {download_path}")
            break
    return task_name, rsp

def create_task(args):
    params = json.loads(args.parameters)
    if args.model == "gpt-4o-2024-05-13-ptu":
        global default_url
        default_url = "http://api.schedule.mtc.sensetime.com:80"
    return create_task_func(args.api_key, args.task_name, args.jsonl_path, args.model, args.priority, args.server_name, args.dst_dir, **params)
    
def create_task_func_mem(api_key, task_name, inputs, model, server_name="test", priority=800, **parameters):
    """ 
    Create a new task.

    Args:
        api_key (str): The API key for authentication.
        task_name (str): The name of the task（unique）.
        inputs (List[List[Dict]]): A list of messages to be sent to the chatbot, list of gpt messages.
        model (str): The model to use for processing the task.
        server_name (str): value for task classification.
        priority (int): The priority level of the task, default is 800.
        parameters (dict): 支持OpenAI completions接口中部分参数: "max_tokens", "frequency_penalty", "presence_penalty", "temperature", "top_p", "n", "seed", "stop"

    Returns:
        outputs(List[Dict or None]): list of return messages, in format:
            [{
                'task_id': 109, 
                'task_data_id': 30196, 
                'total_duration': 3,
                # 请求内容 str
                "request_content": [{"role":"user","content":"你叫什么名字."}],
                # 模型返回内容 str   格式完全和模型返回值一样
                "response_content": {"choices":[{"finish_reason":"stop","index":0,"message":{"content":"我是OpenAI的人工智能助手，我并没有个人名字，只是被称作聊天机器人。","role":"assistant"}}],"created":1718078394,"id":"chatcmpl-9YmxmcTgvhgBLK8p3cvbo7yu2N71t","model":"gpt-4","usage":{"completion_tokens":35,"prompt_tokens":16,"total_tokens":51}}
            }]
        outputs_failed(List[Dict]): only output fails, in format:
            [{
                "request_content":[{\"role\":\"user\",\"content\":\"你叫什么名字.\"},
                "response_content":{"id\":\"chatcmpl-9WhTOkBWfWfOchw4xd3tU5Ris46bU!",!"object!":!"chat.completion!",!"created!":1717580634,!"model!"."gpt-4\",!"choices!":["index!":0,\"message!":"role\":\"assistant!",\"content\":!"我是一个人工智能助手你可以称呼我为“Assistant”或者就叫我人工智能也可以。我没有真实的名字，因为我不是一个真实的人，而是由OpenAl创造的一个程序，旨在帮助和回答问题。有什么我可以帮助你的吗?\"},\"logprobs\":null,\"finish reason\":\"'stop\"}],\"usage\":A"prompt tokens!":16,\"completion tokens!":95,\"total tokens!":111},\"system fingerprint!":"fp _811936bd4f\"},
                "request_fail message":"错误信息",
            }]
    """
    default_proxy = GptProxy(api_key)
    messages_list = inputs

    rsp = default_proxy.taskCreateMem(messages_list, task_name, server_name, model, priority, **parameters)
    if rsp["code"] != 10000:
        raise Exception(f"{rsp}")
    idx = 1
    results_success = []
    results_failed = []
    while True:
        time.sleep(5)
        rsp_msg = default_proxy.taskInfoGet(task_name)
        rsp_msg = rsp_msg["data"]
        sucess_total = rsp_msg["success_total"]
        fail_total = rsp_msg["fail_total"]
        data_total = rsp_msg["data_total"]
        estimated_duration = rsp_msg["estimated_duration"]   # 现阶段预测时间还是有很大出入，请不要参考
        if rsp_msg["status"] == 0:
            print(f"not started yet! cost_time {idx*5}s")
        elif rsp_msg["status"] == 1:
            print(f"job running, process_rate:{(sucess_total + fail_total)/data_total}, failed count: {fail_total}, total count: {data_total}")
            print(f"## estimated_duration: {estimated_duration}")
        else:
            # 下载
            if fail_total > 0:
                fail_remote_url = rsp_msg["fail_file_path"]
                r = requests.get(fail_remote_url)
                if r.ok:
                    for line in r.content.decode("utf-8").splitlines():
                        tmp_results = json.loads(line)
                        results_failed.append(tmp_results)
            # get remote file 
            if sucess_total > 0:
                suc_remote_url = rsp_msg["success_file_path"]
                r = requests.get(suc_remote_url)
                if r.ok:
                    for line in r.content.decode("utf-8").splitlines():
                        tmp_results = json.loads(line)
                        results_success.append(tmp_results)
            break
    # reoder
    results = [None] * len(messages_list)
    for result in results_success:
        results[int(result["index"])] = result
    return results, results_failed

def detail_task(args):
    default_proxy = GptProxy(args.api_key)
    rsp_msg = default_proxy.taskInfoGet(args.task_name)
    rsp_msg = rsp_msg["data"]
    print(rsp_msg)
    sucess_total = rsp_msg["success_total"]
    fail_total = rsp_msg["fail_total"]
    data_total = rsp_msg["data_total"]
    estimated_duration = rsp_msg["estimated_duration"]   # 现阶段预测时间还是有很大出入，请不要参考
    if rsp_msg["status"] == 0:
        print(f"not started yet!")
    elif rsp_msg["status"] >= 1:
        print(f"job running, process_rate:{(sucess_total + fail_total)/data_total}, failed count: {fail_total}")
        print(f"## estimated_duration: {estimated_duration}")
        if rsp_msg["status"] == 2:
            print(f"job finished, sucess_total/data_total: {sucess_total}/{data_total}")
        if (rsp_msg["status"] + args.addtion_option >= 3) :
            # 下载
            os.makedirs(args.dst_dir, exist_ok=True)
            if args.dst_dir in [".", "./"]:
                args.dst_dir = ""
            suc_remote_url = rsp_msg["success_file_path"]
            r = requests.get(suc_remote_url)
            if not r.ok:
                raise Exception(f"download url:{suc_remote_url} failed")
            else:
                download_path = os.path.join(args.dst_dir, f"{args.task_name}.jsonl")
                with open(download_path, "wb+") as f:
                    f.write(r.content)
                print(f"## download succuss: {download_path}")
            if fail_total :
                fail_remote_url = rsp_msg["fail_file_path"]
                r = requests.get(fail_remote_url)
                if not r.ok:
                    raise Exception(f"download url:{fail_remote_url} failed")
                else:
                    download_path = os.path.join(args.dst_dir, f"{args.task_name}.failed.jsonl")
                    with open(download_path, "wb+") as f:
                        f.write(r.content)
                    print(f"## download succuss: {download_path}")
    return sucess_total, fail_total, data_total, estimated_duration

def subparser():
    """
    函数功能   使用-h查询

    """
    list_parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter, add_help=False)
    list_parser.add_argument("--type",
                             choices=['notfinish', 'all'], default='notfinish',
                             help="默认展示未跑完的任务，all显示全部任务")
    list_parser.add_argument("--server_name",
                             type=str, default='',
                             help="任务类型字段，用作task分类, default '' means all")
    list_parser.add_argument("--is_async",
                             choices=[0, 1], default=1,
                             help="查询异步还是同步任务：0同步、1异步；默认异步任务")
    list_parser.add_argument("--page",
                             type=int, default=1,
                             help="展示的页面")
    list_parser.add_argument("--page_size",
                             type=int, default=50,
                             help="每页展示的条目数")
    list_parser.set_defaults(func=list_task)

    create_parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter, add_help=False)
    create_parser.add_argument("task_name", type=str, help="任务名，要保证唯一，请以研究员名字首字母开始，比如'lsc_'")
    create_parser.add_argument("jsonl_path", type=str, help="任务目标文件")
    create_parser.add_argument("--model", type=str, default="GPT4o_0513", help="使用模型, 如何设置 gpt-4o-2024-05-13-ptu 将使用ptu后端")
    create_parser.add_argument("--priority", type=int, default=800, help="""priority越高越先执行，默认800.用户设置的范围是0~1000;
    默认的，不要修改优先级.
    如果是大任务且不紧急，请将优先级修改为0.
    如果是评测类小任务希望快速获得结果，请将优先级设置为1000""")
    create_parser.add_argument("--server_name",
                             type=str, default='test',
                             help="任务类型字段，用作task分类, default is 'test'")
    create_parser.add_argument("--parameters", type=str, default="{}", help="""json格式的参数，含义可以参考OpenAI completions接口，支持的参数包括：
"max_tokens", "frequency_penalty", "presence_penalty", "temperature", "top_p", "n", "seed", "stop"
请使用类似 --parametes='{"temperature":0.8}'来传参
""")
    create_parser.add_argument("--dst_dir", type=str, default="", help="下载路径，如果非空则下载")

    create_parser.set_defaults(func=create_task)

    detail_parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter, add_help=False)
    detail_parser.add_argument("task_name", type=str, help="任务完整名字，建立任务时候会返回")
    detail_parser.add_argument("--addtion_option", type=int, default=0, 
                               help="""额外的操作
0. 什么也不做
1. 任务如果完成下载到dst_dir目录
2. 不管任务是否完成，下载已经完成结果到dst_dir目录""")
    detail_parser.add_argument("--dst_dir", type=str, default=".", help="结果下载路径")
    detail_parser.set_defaults(func=detail_task)

    parser_researcher = argparse.ArgumentParser()
    g_api_key = os.environ.get("API_KEY", "")
    if g_api_key == "":
        raise Exception("API_KEY env must be set before use!!!")
    parser_researcher.add_argument("--api_key", type=str, default=g_api_key , help="密钥, 只能通过API_KEY环境变量设置")
    subparsers = parser_researcher.add_subparsers(dest="type", required=True)
    subparsers.add_parser('list', help="task查询", parents=[list_parser])
    subparsers.add_parser('create', help="task新建", parents=[create_parser])
    subparsers.add_parser('detail', help="特定task查询，可以获得结果", parents=[detail_parser])
    return parser_researcher

def main():
    parser_researcher = subparser()
    args = parser_researcher.parse_args()
    pprint.pp(args.func(args))

if __name__ == '__main__':
    main()