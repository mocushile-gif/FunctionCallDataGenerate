import re
import json
import random
from data_generate.agent.model.gpt import ChatGPTFunction
from data_generate.tools.api_domains.domain_prompts import COARSE_INITIAL_GENERATE,DOMAIN_LIST,COARSE_INITIAL_GENERATE_RESPONSE_FORMAT

llm = ChatGPTFunction(name='gpt4o-ptu-client')

def initial_coarse_domains(input_file_path,output_file_path):
    domain_dict = {}
    for domain in DOMAIN_LIST:
        domain_dict[domain] = []
    with open(input_file_path,"r") as input_file:
        for input_line in input_file:
            tool_define_domains_json = json.loads(input_line)
            tool_define_domains_sort = json.loads(tool_define_domains_json["tool_define_domains"])["sort"]
            simple_tool_define_domains_json = {}
            simple_tool_define_domains_json["name"],simple_tool_define_domains_json["description"] =\
                tool_define_domains_json["name"],tool_define_domains_json["description"]
            for domain in DOMAIN_LIST:
                if (domain == tool_define_domains_sort) or (domain in tool_define_domains_sort):
                    domain_dict[domain].append(simple_tool_define_domains_json)
        for key,value in domain_dict.items():
            parameter = {"domain":key}
            print(f"==" * 20)
            print(f"domain:{key} \t"+str(len(value)))
            if len(value) <= 20:
                #不存在这种情况
                print(f"{key} domain length < 20")
                continue
            example_ten = random.sample(value,20)
            for id,example in enumerate(example_ten):
                parameter[f"EXAMPLE_{id+1}"] = example
            request = [{"role": "user", "content": COARSE_INITIAL_GENERATE.format(**parameter) + COARSE_INITIAL_GENERATE_RESPONSE_FORMAT}]
            response = llm.chat(request)
            coarse_domains = response[0]["content"]
            if '```json' in coarse_domains:
                json_pattern = re.compile(r'```json(.*?)```', re.DOTALL)
                matches = json_pattern.findall(coarse_domains)
                json_contents = matches[0].strip()
            else:
                json_contents = coarse_domains['content']
            coarse_domains = json.loads(json_contents)
            print(f"request:{request}")
            print(f"domain:{key} \tcoarse_domains:{coarse_domains}")
            print(f"=="*20)
            with open(output_file_path,"a+") as f_target:
                f_target.write(json.dumps({
                    "Domain": key,
                    "prompt":request[0]["content"],
                    "coarse_domains":coarse_domains},ensure_ascii=False)+"\n")

if __name__ == '__main__':
    input_file_path = r"../domains/files/merged_tool_defines_domains.jsonl"
    # 细致的粗粒度分类
    # output_file_path = r"../../sample_data/tool_defines_domain_coarse.jsonl"
    output_file_path = r"./files/tool_defines_coarse_domain_initial.jsonl"
    initial_coarse_domains(input_file_path,output_file_path)