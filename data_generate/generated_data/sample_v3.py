import os
import shutil
import json
import random
from tqdm import tqdm
from collections import defaultdict

def get_file_names(folder_path):
    """
    获取指定文件夹下的所有文件路径
    :param folder_path: 文件夹路径
    :return: 文件路径列表
    """
    try:
        return [os.path.join(folder_path, file_name) for file_name in os.listdir(folder_path)]
    except Exception as e:
        print(f"Error reading folder: {e}")
        return []

def reset_folder(folder_path):
    """
    删除并重建指定的文件夹。
    :param folder_path: 要重建的文件夹路径
    """
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
    os.makedirs(folder_path)

def run_sample(folder_path, sample_data_path, sample, target_number=400):
    """
    先按类别采样，如果总数不够 target_number，则从剩余部分随机补充
    :param folder_path: 原始数据集所在目录
    :param sample_data_path: 采样后数据存放目录
    :param sample: 类别采样比例字典 (e.g. {'file': 0.5, 'python': 0.8, 'sql': 0.5, 'xlam': 3})
    :param target_number: 目标采样数据总数
    """
    data_path_lst = get_file_names(folder_path)

    category_data = defaultdict(list)
    total_sample_ratio = sum(sample.values())  # 计算所有类别的权重总和
    sampled_data = []  # 采样结果列表
    remaining_data = []  # 剩余数据（未被采样部分）

    # **第一步：按类别采样**
    for data_path in data_path_lst:
        file_name = os.path.splitext(os.path.basename(data_path))[0]  # 获取文件名（不含扩展名）
        
        file_category = None
        for category in sample.keys():
            if category in file_name:
                file_category = category
                break
        
        if not file_category:
            print(f"Skipping {file_name}: No matching category found")
            continue

        print(f"Processing {file_name} ({file_category})...")

        data=[]
        with open(data_path, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                item=json.loads(line.strip())
                item['data_source']=file_name
                data.append(item)
        category_data[file_category].extend(data)


    for category,data in category_data.items():
        sampling_ratio = sample[category] / total_sample_ratio
        sample_number = int(target_number * sampling_ratio)

        if len(data) <= sample_number:
            print(f"Not enough data in {category}, require {sample_number}, taking all {len(data)} items.")
            sampled_data.extend(data)  # 直接全部加入
        else:
            sampled_subset = random.sample(data, sample_number)
            print(f"sample {sample_number} data from {category}.(all {len(data)} items)")
            sampled_data.extend(sampled_subset)
            remaining_data.extend([d for d in data if d not in sampled_subset])  # 剩余未采样的数据

    # **第二步：检查总数是否足够**
    total_sampled_count = len(sampled_data)
    print(f"Total sampled count: {total_sampled_count} (Target: {target_number})")

    # **第三步：补充不足的数量**
    if total_sampled_count < target_number:
        additional_needed = target_number - total_sampled_count
        print(f"Sampling additional {additional_needed} from remaining data...")

        if len(remaining_data) > additional_needed:
            extra_samples = random.sample(remaining_data, additional_needed)
        else:
            extra_samples = remaining_data  # 如果剩余数据不够，则全部加入

        sampled_data.extend(extra_samples)
    elif total_sampled_count > target_number:
        print('over sampled. Resample...')
        sampled_data=random.sample(sampled_data, target_number)

    # **写入最终的补充数据**
    with open(sample_data_path, 'w+', encoding='utf-8') as out_f:
        for item in sampled_data:
            out_f.write(json.dumps(item, ensure_ascii=False) + '\n')

    print(f"Final sampled dataset size: {len(sampled_data)}")

if __name__ == "__main__":
    import data_generate
    project_dir = os.path.dirname(data_generate.__file__)
    target_number=3000
    data_path = f"{project_dir}/generated_data/executable_tools/filtered/v3"
    sample_data_path = f"{project_dir}/generated_data/executable_tools/sampled/executable_tools_v3_gpt_sample_{target_number}_no_filter.jsonl"
    # sample_data_path = f"{project_dir}/generated_data/executable_tools/sampled/executable_tools_v3_qwq-miss-func_sample_{target_number}.jsonl"
    
    # sample = {'all_self+xlam_multimode_qwq':1}
    sample = {'all_self+xlam_multimode_gpt':3,
                'all_self_multimode_gpt':1,
                'miss_func_or_param_gpt':2}
    # sample={'gpt':1}
    # sample={'miss_func_qwq':1}
    # sample = {'all_self+xlam_multimode_qwq':2,
    #             'all_self_multimode_qwq':1,
    #             'miss_func_or_param_qwq':3}
    run_sample(data_path, sample_data_path, sample, target_number)
