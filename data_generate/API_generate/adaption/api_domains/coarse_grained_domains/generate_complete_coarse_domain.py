import re
import json
import random
from data_generate.agent.model.gpt import ChatGPTFunction
from data_generate.tools.api_domains.domain_prompts import COARSE_COMPLETE_GENERATE,DOMAIN_LIST,COARSE_COMPLETE_GENERATE_RESPONSE_FORMAT

llm = ChatGPTFunction(name='gpt4o-ptu-client')
def generate_complete_coarse_domains(input_file_path,coarse_init_file_path,coarse_sample_file_path,coarse_complete_file_path):
    domain_dict = {}
    for domain in DOMAIN_LIST:
        domain_dict[domain] = []
    with open(input_file_path, "r") as input_file:
        for input_line in input_file:
            tool_define_domains_json = json.loads(input_line)
            tool_define_domains_sort = json.loads(tool_define_domains_json["tool_define_domains"])["sort"]
            simple_tool_define_domains_json = {}
            simple_tool_define_domains_json["name"], simple_tool_define_domains_json["description"] = \
                tool_define_domains_json["name"], tool_define_domains_json["description"]
            for domain in DOMAIN_LIST:
                if (domain == tool_define_domains_sort) or (domain in tool_define_domains_sort):
                    domain_dict[domain].append(simple_tool_define_domains_json)
    domain_coarse_basic_dict_total = {}
    with open(coarse_init_file_path,"r") as coarse_input_file:
        for coarse_input_line in coarse_input_file:
            coarse_basic = json.loads(coarse_input_line)
            domain = coarse_basic["Domain"]
            domain_coarse_basic_dict = {}
            for category in coarse_basic["coarse_domains"]["category"]:
                for sub_category_name, reason in category.items():
                    if sub_category_name != "APIs" and sub_category_name != "examples":
                        domain_coarse_basic_dict[sub_category_name] = reason
            domain_coarse_basic_dict_total[domain] = domain_coarse_basic_dict
    basic_coarse_length = 0
    for key,value in domain_coarse_basic_dict_total.items():
        print(key)
        print(value)
        basic_coarse_length += len(value)
    print(f"basic_coarse_length:{basic_coarse_length}")
    print(f"**"*30)
    skip_domain_list = ["Health", "Economics", "Environment", "Education", "Gaming", "Devices", "Politics",
                   "Travel", "Psychology", "History", "Cybersecurity", "Lifestyle", "Logistics", "Events", "Automation",
                   "Food", "Construction", "Energy", "Animal Welfare", "Medical", "Nutrition", "Others"]
    for domain, coarse_basic_domain in domain_coarse_basic_dict_total.items():
        recursion_max_nums,classification_perfect_flag = 500,False
        coarse_basic_domain_len = len(coarse_basic_domain)
        if domain in skip_domain_list:
            continue
        while recursion_max_nums>0 and (not classification_perfect_flag) and (coarse_basic_domain_len<=25):
            print(f"=="*20)
            parameter = {"coarse_basic_domain":coarse_basic_domain,\
                         "domain":domain}
            example_ten = random.sample(domain_dict[domain],30)
            for example_id,example in enumerate(example_ten):
                parameter[f"EXAMPLE_{example_id + 1}"] = example
            request = [{"role": "user", "content": COARSE_COMPLETE_GENERATE.format(**parameter) + COARSE_COMPLETE_GENERATE_RESPONSE_FORMAT}]
            print(f"request:\t{request}")
            response = llm.chat(request)
            coarse_domains_check = response[0]["content"]
            if '```json' in coarse_domains_check:
                json_pattern = re.compile(r'```json(.*?)```', re.DOTALL)
                matches = json_pattern.findall(coarse_domains_check)
                json_contents = matches[0].strip()
            else:
                json_contents = coarse_domains_check
            coarse_domains_check = json.loads(json_contents)
            print(f"coarse_domains_check:\t{coarse_domains_check}")
            classification_perfect_flag = (coarse_domains_check["classification perfect"].strip().lower() == 'yes')
            recursion_max_nums -= 30
            new_category_list = []
            coarse_basic_domain = {}
            if not classification_perfect_flag:
                new_category_list = coarse_domains_check['revised category']
                for new_category in new_category_list:
                    for new_category_name, new_category_define in new_category.items():
                        coarse_basic_domain[new_category_name] = new_category_define
            coarse_basic_domain_len = len(coarse_basic_domain)
            print(f"domain:\t:{domain}")
            print(f"current_recursion_max_nums:\t{recursion_max_nums}")
            print(f"current_coarse_basic_domain:\t{coarse_basic_domain}")
            print(f"current_coarse_basic_domain_len:\t{len(coarse_basic_domain)}")
            print(f"coarse_domains_check:{classification_perfect_flag}")
            print(f"==" * 20)
            with open(coarse_sample_file_path,"a+") as f_target:
                check_domain = {"domain":domain,
                                "classification_perfect_flag": classification_perfect_flag,
                                "coarse_domain": json.dumps(coarse_basic_domain, ensure_ascii=False),
                                "coarse_domains_thought":coarse_domains_check,
                                # "add_category_list":add_category_list if add_category_list else None
                                }
                f_target.write(json.dumps(check_domain,ensure_ascii=False)+"\n")
        print(f"Important Message:\tDomain:{domain} \ncoarse_result:{coarse_basic_domain}\n length:{len(coarse_basic_domain)}")
        with open(coarse_complete_file_path,"a+") as final_target:
            final_target.write(json.dumps({
                "domain": domain,
                "coarse_domain":coarse_basic_domain,
                "len_coarse_domain":len(coarse_basic_domain)
            },ensure_ascii=False)+"\n")

if __name__ == '__main__':
    input_file_path = r"../domains/merged_tool_defines_domains.jsonl"
    coarse_init_file_path = r"./files/tool_defines_coarse_domain_initial.jsonl"
    coarse_sample_file_path = r"./files/tool_defines_coarse_domain_iter_sample.jsonl"
    coarse_complete_file_path = r"../../sample_data/tool_defines_coarse_domain_complete.jsonl"
    generate_complete_coarse_domains(input_file_path,
                                     coarse_init_file_path,
                                     coarse_sample_file_path,
                                     coarse_complete_file_path)