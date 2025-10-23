import json
import threading
from tqdm import tqdm
import matplotlib.pyplot as plt
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from data_generate.agent.model.doubao import DOUBAOFunction
from data_generate.tools.api_domains.domain_prompts import SORT_SAMPLE_DOMAIN,SORT_SAMPLE_DOMAIN_RESPONSE_FORMAT,DOMAIN_LIST

write_lock = threading.Lock()
llm = DOUBAOFunction()

def update_progress_bar(pbar):
    with threading.Lock():  # 保证进度条更新时线程安全
        pbar.update(1)

def multi_thread_sort(tool_define_input_file_path,tool_define_output_file_path):
    with open(tool_define_input_file_path, "r") as input_file:
        lines = input_file.readlines()

        # 创建一个线程安全的进度条
        with tqdm(total=len(lines), desc="Processing lines") as pbar:
            # 使用ThreadPoolExecutor处理每一行
            with ThreadPoolExecutor(max_workers=32) as executor:
                futures = []
                input_file.seek(0)  # 重置文件指针

                # 提交每一行处理任务
                for input_line in lines:
                    futures.append(executor.submit(sort_line_domains, input_line, tool_define_output_file_path,pbar))
                # 等待所有任务完成
                for future in as_completed(futures):
                    future.result()
def sort_line_domains(input_line,tool_define_output_file_path,pbar):
    input_line_json = json.loads(input_line)
    try:
        api_tool_define = {"api_tool_define":input_line_json}
        request = [{"role": "user", "content": SORT_SAMPLE_DOMAIN.format(**api_tool_define)+SORT_SAMPLE_DOMAIN_RESPONSE_FORMAT}]
        response = llm.chat(request)
        tool_define_domains = response[0]["content"]
        input_line_json["tool_define_domains"] = tool_define_domains

        # 完成处理后立即写入文件
        with write_lock:
            with open(tool_define_output_file_path, "a+", encoding="utf-8") as f_target:
                f_target.write(json.dumps(input_line_json,ensure_ascii=False) + "\n")

            # 更新进度条
            update_progress_bar(pbar)

            return tool_define_domains
    except Exception as e:
        print(f"Error processing line: {e}")
        with write_lock:
            with open(tool_define_output_file_path, "a+", encoding="utf-8") as f_target:
                input_line_json["tool_define_domains_error"] = e
                f_target.write(json.dumps(input_line_json, ensure_ascii=False) + "\n")

            # 更新进度条
            update_progress_bar(pbar)

            return None

def plot(tool_define_output_file_path):
    domains_sample_list = []
    with open(tool_define_output_file_path,"r") as input_file:
        for input_line in input_file:
            input_line_json = json.loads(input_line)
            if "tool_define_domains_error" not in input_line_json:
                tool_define_domains = input_line_json["tool_define_domains"]
                try:
                    tool_define_domains_json = json.loads(tool_define_domains)
                    tool_define_domains_sort = tool_define_domains_json["sort"]
                    for domain in DOMAIN_LIST:
                        if domain in tool_define_domains_sort:
                            domains_sample_list.append(domain)
                except:
                    for domain in DOMAIN_LIST:
                        if domain in tool_define_domains:
                            domains_sample_list.append(domain)
    domain_counts = Counter(domains_sample_list)
    print(domain_counts)
    sorted_counts, sorted_labels = zip(*sorted(domain_counts.items(), key=lambda x: x[1], reverse=True))
    # 设置图形大小
    plt.figure(figsize=(12, 8))

    print(f"out_of_index:{set(sorted_counts)-set(DOMAIN_LIST)}")
    # 绘制条形图
    plt.bar(sorted_counts, sorted_labels, color='skyblue')

    # 添加标题和标签
    plt.title('各领域的分布统计', fontsize=16)
    plt.xlabel('领域', fontsize=14)
    plt.ylabel('出现次数', fontsize=14)

    # 旋转x轴标签以防止重叠
    plt.xticks(rotation=45, ha='right')

    # 显示网格线
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # 调整布局以防止标签被截断
    plt.tight_layout()

    # 显示图形
    plt.show()

if __name__ == '__main__':
    #merged_tool_defines.jsonl:所有收集而来的API定义文件
    #对所有的API进行domain的分类
    tool_define_input_file_path = "./files/merged_tool_defines.jsonl"
    tool_define_output_file_path = "./files/merged_tool_defines_domains.jsonl"
    multi_thread_sort(tool_define_input_file_path,tool_define_output_file_path)
    #对API进行分类后的统计
    plot(tool_define_output_file_path)