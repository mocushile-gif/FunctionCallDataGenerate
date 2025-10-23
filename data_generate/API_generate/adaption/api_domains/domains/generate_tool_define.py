import json
from tqdm import tqdm
from data_generate.agent.model.doubao import DOUBAOFunction
from data_generate.tools.api_domains.domain_prompts import GET_TOOL_DEFINE_FROM_TOOLACE

llm = DOUBAOFunction()
def generate_tool_define_from_toolace(toolace_input_file,toolace_output_file):
    with open(toolace_input_file,"r") as input_file:
        for input_line in tqdm(input_file):
            input_line_json = json.loads(input_line)
            if input_line_json[0]["role"]=="system":
                sample_system_prompt = input_line_json[0]["content"]
                request = [{"role":"user","content":GET_TOOL_DEFINE_FROM_TOOLACE + sample_system_prompt}]
                response = llm.chat(request)
                try:
                    tool_define_json = json.loads(response[0]["content"])
                    print(f"tool_define_json:{tool_define_json}")
                    with open(toolace_output_file,"w+") as f_target:
                        f_target.write(json.dumps(tool_define_json,ensure_ascii=False)+"\n")
                except Exception as e:
                    print(f"error:{e}")
                    continue

if __name__ == '__main__':
    #从toolace中提取出API的定义
    toolace_input_file = "./files/toolace_data_transformed.jsonl"
    toolace_output_file = "./files/toolace_tool_define.jsonl"
    generate_tool_define_from_toolace(toolace_input_file,toolace_output_file)