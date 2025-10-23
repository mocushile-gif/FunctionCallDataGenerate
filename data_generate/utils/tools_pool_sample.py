import random

def tools_pool_sample(tool_nums_distribution):
    total_tool_nums = sum(tool_nums_distribution.values())

    # 计算每个功能长度所占的采样比例
    tool_nums_distribution = {int(length): count / total_tool_nums for length, count in tool_nums_distribution.items()}

    # 采样所需的API数量
    sample_tool_nums = random.choices(
        population=list(tool_nums_distribution.keys()),
        weights=list(tool_nums_distribution.values()),
        k=1
    )[0]  # 直接取出采样的数量
    print(f"sample_tool_nums:{sample_tool_nums}")
    return sample_tool_nums