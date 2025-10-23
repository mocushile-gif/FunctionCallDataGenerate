import re
import json
import threading
from tqdm import tqdm
from data_generate.agent.model.doubao import DOUBAOFunction
from concurrent.futures import ThreadPoolExecutor, as_completed
from data_generate.tools.api_domains.domain_prompts import SORT_SAMPLE_COARSE_DOMAIN,SORT_SAMPLE_DOMAIN_RESPONSE_FORMAT,DOMAIN_LIST

llm = DOUBAOFunction()
write_lock = threading.Lock()
def update_progress_bar(pbar):
    with threading.Lock():  # 保证进度条更新时线程安全
        pbar.update(1)
def sort_sample_coarse_domain(input_file_path,coarse_complete_file_path,sort_coarse_domain_file_path):
    coarse_sub_domain_dict = {}
    with open(coarse_complete_file_path,"r") as coarse_input_file:
        coarse_lines = coarse_input_file.readlines()
        for coarse_line in coarse_lines:
            coarse_json_line = json.loads(coarse_line)
            domain = coarse_json_line["domain"]
            coarse_domain_dict = coarse_json_line["coarse_domain"]
            coarse_sub_domain_dict[domain] = coarse_domain_dict

    with open(input_file_path, "r") as input_file:
        lines = input_file.readlines()
        with tqdm(total=len(lines), desc="Processing lines") as pbar:
            # 使用ThreadPoolExecutor处理每一行
            with ThreadPoolExecutor(max_workers=32) as executor:
                futures = []
                input_file.seek(0)  # 重置文件指针

                # 提交每一行处理任务
                for input_line in lines:
                    futures.append(executor.submit(sort_sample_coarse_domain_line, input_line, pbar,coarse_sub_domain_dict,sort_coarse_domain_file_path))
                # 等待所有任务完成
                for future in as_completed(futures):
                    future.result()


def sort_sample_coarse_domain_line(input_line, pbar, coarse_sub_domain,sort_coarse_domain_file_path):
    try:
        tool_define_domains_json = json.loads(input_line)
        tool_define_domains_sort = json.loads(tool_define_domains_json["tool_define_domains"])["sort"]
        simple_tool_define_domains_json = {}
        simple_tool_define_domains_json["name"], simple_tool_define_domains_json["description"] = \
            tool_define_domains_json["name"], tool_define_domains_json["description"]
        true_domain = ""
        for domain in DOMAIN_LIST:
            if (domain == tool_define_domains_sort) or (domain in tool_define_domains_sort):
                true_domain = domain
        if true_domain:
            sub_domain_dict = coarse_sub_domain[true_domain]
            sub_domain_others = False
            for sub_domain_name, sub_domain_define in sub_domain_dict.items():
                if sub_domain_name.lower() == "others":
                    sub_domain_others = True
            if not sub_domain_others:
                sub_domain_dict["Others"] = ""
            api_tool_define = json.dumps(simple_tool_define_domains_json, ensure_ascii=False)
            request_parameter = {"domain": tool_define_domains_sort, "api_tool_define": api_tool_define,
                                 "sub_domain_dict": sub_domain_dict}
            request = [{"role": "user", "content": SORT_SAMPLE_COARSE_DOMAIN.format(**request_parameter) + SORT_SAMPLE_DOMAIN_RESPONSE_FORMAT}]
            response = llm.chat(request)
            coarse_domains = response[0]["content"]
            if '```json' in coarse_domains:
                json_pattern = re.compile(r'```json(.*?)```', re.DOTALL)
                matches = json_pattern.findall(coarse_domains)
                json_contents = matches[0].strip()
            else:
                json_contents = json.loads(coarse_domains)
            sub_domain_dict = {"thought": json_contents["thought"], "sort": json_contents["sort"]}
            # print(f"sub_domain_dict:{sub_domain_dict}")
            tool_define_domains = json.loads(tool_define_domains_json["tool_define_domains"])
            # print(f"tool_define_domains:{tool_define_domains}")
            tool_define_domains_json_new = {"domain": tool_define_domains, "coarse_domain": sub_domain_dict}
            tool_define_domains_json["tool_define_domains"] = tool_define_domains_json_new
            # print(f"tool_define_domains_json:{tool_define_domains_json}")
            with write_lock:
                with open(sort_coarse_domain_file_path, "a+",
                          encoding="utf-8") as f_target:
                    f_target.write(json.dumps(tool_define_domains_json, ensure_ascii=False) + "\n")
                # 更新进度条
                update_progress_bar(pbar)

                return tool_define_domains
    except Exception as e:
        print(f"Error processing line: {e}")
        with write_lock:
            with open(sort_coarse_domain_file_path, "a+", encoding="utf-8") as f_target:
                tool_define_domains_json["tool_define_domains_error"] = e
                f_target.write(json.dumps(tool_define_domains_json, ensure_ascii=False) + "\n")

            # 更新进度条
            update_progress_bar(pbar)
            return None

def fix_count_coarse_domain(coarse_complete_file_path,sort_coarse_domain_file_path,coarse_domain_count_path,coarse_domain_simple_file_path):
    result_json_lines = []
    classify_range = {}
    with open(coarse_complete_file_path,"r") as coarse_ultimate_file:
        for coarse_ultimate_line in coarse_ultimate_file:
            coarse_ultimate_json = json.loads(coarse_ultimate_line)
            classify_range[coarse_ultimate_json["domain"]] = coarse_ultimate_json["coarse_domain"]

    with open(sort_coarse_domain_file_path,"r") as input_file:
        domain_dict = {}
        coarse_domain_num = 0
        for input_line in input_file:
            input_line_json = json.loads(input_line)
            if "tool_define_domains_error" not in input_line_json:
                domain = input_line_json["tool_define_domains"]["domain"]["sort"]
                match_flag = False
                for domain_label in DOMAIN_LIST:
                    if domain_label.lower()==domain.lower():
                        match_flag =True
                if not match_flag:
                    continue
                coarse_domain = input_line_json["tool_define_domains"]["coarse_domain"]["sort"]
                if isinstance(coarse_domain,list) and len(coarse_domain)>=2:
                    print(f"error coarse_domain:{coarse_domain}")
                    continue
                # 如果 domain 不存在，初始化为空字典
                if domain not in domain_dict:
                    domain_dict[domain] = {}

                try:
                    # 获取 coarse_domain 的当前计数
                    coarse_domain_dict = domain_dict[domain]
                    if coarse_domain not in domain_dict[domain]:
                        coarse_domain_num+=1
                    _,count = coarse_domain_dict.get(coarse_domain, ("",0))
                    count += 1
                    domain_dict[domain][coarse_domain] = (classify_range[domain].get(coarse_domain,""),count)
                    tool_define_domains = [
                        {
                            "domain":domain,
                            "thought":input_line_json["tool_define_domains"]["domain"]["thought"]
                    },
                        {
                            "coarse_domain":coarse_domain,
                            "thought":input_line_json["tool_define_domains"]["coarse_domain"]["thought"],
                            "coarse_domain_define":classify_range[domain].get(coarse_domain,"")

                    }]
                    input_line_json["tool_define_domains"] = tool_define_domains
                    result_json_lines.append(input_line_json)
                except Exception as e:
                    print(f"error e :{e}")
                    print(f"domain:{domain}")
                    print(f"coarse_domain:{coarse_domain}")
        print(f"domain_dict:{domain_dict}")
        print(f"coarse_domain_num:{coarse_domain_num}")
        count_coarse_domain_count = {}
        for domain_dict_key,domain_dict_value in domain_dict.items():
            for coarse_domain_dict_key,(coarse_domain_dict_define,coarse_domain_dict_value) in domain_dict_value.items():
                if coarse_domain_dict_value >=4:
                    count_coarse_domain_count[coarse_domain_dict_key]=coarse_domain_dict_value
        print(f"count_coarse_domain:{count_coarse_domain_count}")
        print(f"len count_coarse_domain:{len(count_coarse_domain_count)}")
        with open(coarse_domain_count_path, 'w', encoding='utf-8') as json_file:
            json.dump(domain_dict, json_file, ensure_ascii=False, indent=4)
        print(len(result_json_lines))
        with open(coarse_domain_simple_file_path,'w+') as f_target:
            for result_json_line in result_json_lines:
                f_target.write(json.dumps(result_json_line,ensure_ascii=False)+"\n")

if __name__ == '__main__':
    input_file_path = r"../domains/files/merged_tool_defines_domains.jsonl"
    coarse_complete_file_path = r"./files/tool_defines_coarse_domain_complete.jsonl"
    sort_coarse_domain_file_path = r"./files/merged_tool_defines_coarse_domains.jsonl"
    sort_sample_coarse_domain(input_file_path,coarse_complete_file_path,sort_coarse_domain_file_path)
    coarse_domain_count_path = r"./files/tool_defines_coarse_domain_count.jsonl"
    coarse_domain_simple_file_path = r"./files/merged_tool_defines_coarse_domains_sample.jsonl"
    fix_count_coarse_domain(coarse_complete_file_path,sort_coarse_domain_file_path,coarse_domain_count_path,coarse_domain_simple_file_path)