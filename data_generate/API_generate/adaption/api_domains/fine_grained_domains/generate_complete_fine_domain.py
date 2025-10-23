import re
import json
import random
from tqdm import tqdm
from data_generate.agent.model.gpt import ChatGPTFunction
from data_generate.tools.api_domains.domain_prompts import FINE_GENERATE_PROMPT,FINE_GENERATE_PROMPT_RESPONSE_FORMAT

llm = ChatGPTFunction(name='gpt4o-ptu-client')
def generate_general_fine_domains(input_file_path,classify_file_path,fine_domains_file_path,fine_domains_file_path_complete):
    filter_classify_dict = {}
    with (open(classify_file_path, "r") as input_classify_file):
        classify_json = json.loads(input_classify_file.read())
        for domain_name, coarse_domain_dict_count in classify_json.items():
            if domain_name not in filter_classify_dict:
                filter_classify_dict[domain_name] = {}
            for coarse_domain_name, (coarse_domain_define, coarse_domain_count) in coarse_domain_dict_count.items():
                if (coarse_domain_count >= 3) and (coarse_domain_name.lower() != "others"):
                    if coarse_domain_name not in filter_classify_dict[domain_name]:
                        filter_classify_dict[domain_name][coarse_domain_name] = {
                            "coarse_domain_define": coarse_domain_define}
                    else:
                        filter_classify_dict[domain_name][coarse_domain_name][
                            "coarse_domain_define"] = coarse_domain_define

    print(f"filter_classify_dict:{filter_classify_dict}")
    print(f"len_filter_classify_dict:{len(filter_classify_dict)}")

    # sample做映射
    with open(input_file_path, "r") as sample_files:
        for sample_line in sample_files:
            sample_line_json = json.loads(sample_line)
            domain_name, coarse_domain_name = "", ""
            for name_dict in sample_line_json["tool_define_domains"]:
                if "domain" in name_dict:
                    domain_name = name_dict["domain"]
                if "coarse_domain" in name_dict:
                    coarse_domain_name = name_dict["coarse_domain"]
            if (domain_name in filter_classify_dict) and (
                    coarse_domain_name in filter_classify_dict[domain_name]):  # 没有被filter掉
                if "sample" not in filter_classify_dict[domain_name][coarse_domain_name]:
                    filter_classify_dict[domain_name][coarse_domain_name]["sample"] = [sample_line_json]
                else:
                    filter_classify_dict[domain_name][coarse_domain_name]["sample"].append(sample_line_json)
    skip_domain_name_list = ["Travel", "Lifestyle", "Medical", "Commerce", "Food"]
    for domain_name, coarse_domain in tqdm(filter_classify_dict.items()):
        if domain_name in skip_domain_name_list:
            continue
        for coarse_domain_name, coarse_domain_info in coarse_domain.items():
            sample_list, coarse_domain_define = [], ""
            for coarse_domain_info_key, coarse_domain_value in coarse_domain_info.items():
                if coarse_domain_info_key == "sample":
                    sample_list = coarse_domain_value
                if coarse_domain_info_key == "coarse_domain_define":
                    coarse_domain_define = coarse_domain_value
            # print(f"len sample_list:{len(sample_list)}")
            # print(f"sample_list:{sample_list}")
            # print(f"coarse_domain_define:{coarse_domain_define}")
            current_sample_nums = len(sample_list)
            recursion_max_nums = 150
            classification_perfect_flag = False
            tiny_basic_domain_len = 0
            tiny_basic_domain = {}
            max_tiny_basic_domain = {}
            while (current_sample_nums > 0) and (recursion_max_nums > 0) and (not classification_perfect_flag) and (
                    tiny_basic_domain_len <= 15):
                print(f"==" * 20)
                parameter = {"domain": domain_name,
                             "coarse_domain": coarse_domain_name,
                             "coarse_domain_define": coarse_domain_define,
                             "tiny_basic_domain": tiny_basic_domain}
                recursion_max_nums -= 20
                random_choice_num = 20 if current_sample_nums >= 20 else current_sample_nums
                current_sample_nums -= random_choice_num
                content = FINE_GENERATE_PROMPT.format(**parameter)
                sample_twenty = random.sample(sample_list, random_choice_num)
                for sample_ in sample_twenty:
                    sample_prompt = {"name": sample_["name"], "description": sample_["description"]}
                    sample_prompt = f"""\t{sample_prompt}\n"""
                    content += sample_prompt
                response_format = f"""
###请经过思考后判断对于{coarse_domain_name} 的现有分类是否完善，请务必按照以下JSON格式回复:"""
                response_format += FINE_GENERATE_PROMPT_RESPONSE_FORMAT
                request = [{"role": "user", "content": content + response_format}]
                print(f"request:\t{request}")
                max_retries = 5  # 最大重试次数
                retries = 0
                while retries < max_retries:
                    try:
                        response = llm.chat(request)
                        tiny_domains_check = response[0]["content"]
                        if '```json' in tiny_domains_check:
                            json_pattern = re.compile(r'```json(.*?)```', re.DOTALL)
                            matches = json_pattern.findall(tiny_domains_check)
                            json_contents = matches[0].strip()
                        else:
                            json_contents = tiny_domains_check
                        tiny_domains_check = json.loads(json_contents)
                        break
                    except Exception as e:
                        print(f"Error: {e}. Please try again.")
                        retries += 1
                if retries == 5:  # 直接进入下一次循环
                    continue
                print(f"tiny_domains_check:\t{tiny_domains_check}")
                classification_perfect_flag = (tiny_domains_check["classification perfect"].strip().lower() == 'yes')
                tiny_basic_domain = {}
                if not classification_perfect_flag:
                    new_category_list = tiny_domains_check['revised category']
                    for new_category in new_category_list:
                        for new_category_name, new_category_define in new_category.items():
                            tiny_basic_domain[new_category_name] = new_category_define
                if len(tiny_basic_domain) > len(max_tiny_basic_domain):
                    max_tiny_basic_domain = tiny_basic_domain
                tiny_basic_domain_len = len(tiny_basic_domain)
                print(f"domain:\t:{domain_name}")
                print(f"coarse_domain\t:{coarse_domain_name}")
                print(f"current_recursion_max_nums:\t{recursion_max_nums}")
                print(f"current_tiny_basic_domain:\t{tiny_basic_domain}")
                print(f"current_tiny_basic_domain_len:\t{len(tiny_basic_domain)}")
                print(f"tiny_domains_check:{classification_perfect_flag}")
                print(f"==" * 20)
                with open(fine_domains_file_path, "a+") as f_target:
                    check_domain = {"domain": domain_name,
                                    "coarse_domain": coarse_domain_name,
                                    "coarse_domain_define": coarse_domain_define,
                                    "tiny_domain": tiny_basic_domain,
                                    "classification_perfect_flag": classification_perfect_flag,
                                    "tiny_domains_thought": tiny_domains_check,
                                    }
                    f_target.write(json.dumps(check_domain, ensure_ascii=False) + "\n")
            print(
                f"Important Message:\tDomain:{domain_name} coarse_domain:{coarse_domain_name} \n tiny_result:{max_tiny_basic_domain}\n length:{len(max_tiny_basic_domain)}")
            with open(fine_domains_file_path_complete, "a+") as final_target:
                final_target.write(json.dumps({
                    "domain": domain_name,
                    "coarse_domain": coarse_domain_name,
                    "coarse_domain_define": coarse_domain_define,
                    "tiny_domain": max_tiny_basic_domain,
                    "len_coarse_domain": len(max_tiny_basic_domain)
                }, ensure_ascii=False) + "\n")

def count_general_fine_domains(fine_domains_file_path_complete):
    domain_list,coarse_domain_list,tiny_domain_len = [],[],0
    with open(fine_domains_file_path_complete,"r") as input_file:
        for input_line in input_file:
            try:
                input_line_json = json.loads(input_line)
                domain_list.append(input_line_json["domain"])
                coarse_domain_list.append(input_line_json["coarse_domain"])
                tiny_domain_len += len(list(input_line_json["tiny_domain"].keys()))
            except Exception as e:
                print(f"error e:{e}")
                print(f"input_line:{input_line}")

    print(len(domain_list))
    print(len(coarse_domain_list))
    print(tiny_domain_len)

if __name__ == '__main__':
    # 粗粒度分类+API数量
    input_file_path = "../coarse_grained_domains/files/merged_tool_defines_coarse_domains_sample.jsonl"
    # 每个API的domain+coarse_domain
    classify_file_path = "../coarse_grained_domains/files/tool_defines_coarse_domain_count.jsonl"
    fine_domains_file_path = r"../fine_grained_domains/files/tool_defines_fine_domain.jsonl"
    fine_domains_file_path_complete = r"../fine_grained_domains/files/tool_defines_fine_domain_complete.jsonl"
    generate_general_fine_domains(input_file_path,classify_file_path,fine_domains_file_path,fine_domains_file_path_complete)
    count_general_fine_domains(fine_domains_file_path_complete)