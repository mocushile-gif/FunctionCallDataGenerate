import re
import json
from tqdm import tqdm
from data_generate.agent.model.gpt import ChatGPTFunction
from data_generate.tools.api_domains.domain_prompts import GENERATE_FUNCTIONS_PROMPT,GENERATE_FUNCTIONS_PROMPT_RESPONSE_FORMAT

llm = ChatGPTFunction(name='gpt4o-ptu-client')
def generate_function(fine_domains_file_path_complete, fine_domains_function_path,skip_idx=0):
    with open(fine_domains_file_path_complete,"r") as input_file:
        for idx,input_line in tqdm(enumerate(input_file)):
            if idx <= skip_idx:
                continue
            input_line_json = json.loads(input_line)
            domain_name = input_line_json["domain"]
            coarse_domain_name = input_line_json["coarse_domain"]
            coarse_domain_define = input_line_json["coarse_domain_define"]
            tiny_domain_dict = {}
            for tiny_domain_name,tiny_domain_define in input_line_json["tiny_domain"].items():
                parameter = {"domain_name": domain_name,
                             "coarse_domain_name": coarse_domain_name,
                             "coarse_domain_define": coarse_domain_define,
                             "tiny_domain_name": tiny_domain_name,
                             "tiny_domain_define": tiny_domain_define}
                request = [{"role": "user", "content": GENERATE_FUNCTIONS_PROMPT.format(**parameter)+GENERATE_FUNCTIONS_PROMPT_RESPONSE_FORMAT}]
                max_retries = 5  # 最大重试次数
                retries = 0
                while retries < max_retries:
                    try:
                        response = llm.chat(request)
                        functionalities = response[0]["content"]
                        if '```json' in functionalities:
                            json_pattern = re.compile(r'```json(.*?)```', re.DOTALL)
                            matches = json_pattern.findall(functionalities)
                            json_contents = matches[0].strip()
                        else:
                            json_contents = functionalities
                        json_contents = json.loads(json_contents)
                        break
                    except Exception as e:
                        print(f"Error: {e}. Please try again.")
                        retries += 1
                functions_list = json_contents["function"]
                # tiny_domain_dict = {tiny_domain_name:{}}
                functions_sample_list = []
                for function_define_example in functions_list:
                    for function_name,define_example in function_define_example.items():
                        function_define = define_example["define"]
                        function_example_list = define_example["example"]
                        functions_sample_dict = {"define":function_define,"example":function_example_list}
                        functions_sample_list.append(functions_sample_dict)
                tiny_domain_dict[tiny_domain_name] = {
                    "thought": json_contents["thought"],
                    "functions":functions_sample_list
                }
                # print(f"tiny_domain_dict:{tiny_domain_dict}")
            input_line_json["tiny_domain_functions"] = tiny_domain_dict
            with open(fine_domains_function_path,"a+") as f_target:
                f_target.write(json.dumps(input_line_json,ensure_ascii=False)+"\n")

def count_functions(fine_domains_function_path):
    with open(fine_domains_function_path,"r") as input_file:
        example_length = 0
        tiny_domains_length = 0
        for input_line in input_file:
            input_line_json = json.loads(input_line)
            tiny_domains = input_line_json["tiny_domain"]
            tiny_domain_functions = input_line_json["tiny_domain_functions"]
            tiny_domains_length += len(tiny_domains.keys())
            for tiny_domain_functions_key,tiny_domain_functions_value in  tiny_domain_functions.items():
                for function in tiny_domain_functions_value["functions"]:
                    example_length += len(function["example"])
                    print(function["example"])
        print(f"example_length:{example_length}")
        print(f"tiny_domains_length:{tiny_domains_length}")

if __name__ == '__main__':
    fine_domains_function_path = r"./files/tool_defines_functions.jsonl"
    fine_domains_file_path_complete = r"./files/tool_defines_fine_domain_complete.jsonl"
    generate_function(fine_domains_file_path_complete, fine_domains_function_path,skip_idx=76)
    count_functions(fine_domains_function_path)
