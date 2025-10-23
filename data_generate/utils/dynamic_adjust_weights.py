import json
from datetime import datetime, timedelta
import sys
import os
import shutil
import random
import statistics

def max_task_sample(task_turn_weights):
    choices = list(task_turn_weights.keys())
    weights = list(task_turn_weights.values())
    # 使用权重进行随机选择
    return int(random.choices(choices, weights)[0])

def dynamic_adjust_weights(tool_nums_distribution,base_mode_weights=None,task_turn_weights=None):
    """
    根据随机选择的工具数量动态调整模式权重 (mode_weights) 和任务轮次权重 (task_turn_weights)。

    参数:
    - tool_nums_distribution (str or dict): JSON 字符串或字典，表示工具数量及其出现的概率。

    返回:
    - tuple: 
        - 调整后的 mode_weights (dict)，用于控制不同模式的权重
        - 调整后的 task_turn_weights (dict)，用于控制不同任务轮次的权重
        - 选定的工具数量 (int)
    """
    # 确保 tool_nums_distribution 是字典类型
    if isinstance(tool_nums_distribution, str):
        tool_nums_distribution = json.loads(tool_nums_distribution)

    # 将字典的键转换为整数（JSON 解析后默认是字符串）
    tool_nums_distribution = {int(k): int(v) for k, v in tool_nums_distribution.items()}

    # 1️⃣ 随机选择一个工具数量 (selected_tool_count)，依据其分布概率
    tool_counts, weights = zip(*tool_nums_distribution.items())  # 拆分键值对
    selected_tool_count = random.choices(tool_counts, weights=weights, k=1)[0]  # 根据权重随机选择一个工具数量

    # 2️⃣ 定义基础模式权重（默认值）
    if not base_mode_weights:
        base_mode_weights = {
        "single": 1,      # 单工具调用
        "parallel": 1,    # 并行调用同一工具
        "multiple": 1,    # 多工具调用
        "dependent": 1,   # 依赖调用（工具调用顺序相关）
        "no_tool_use": 1,  # 不使用工具
        "miss_param": 1  # 缺少参数
    }

    # 任务轮次权重初始化，每个任务轮次 (turn) 赋相同的初始权重
    if not task_turn_weights:
        task_turn_weights = {
        1: 1,  # 1轮任务
        2: 1,  # 2轮任务
        3: 1,  # 3轮任务
        4: 1,  # 4轮任务
    }


    max_tools = max(tool_nums_distribution.keys())
    x = selected_tool_count / max_tools

    # 计算中位数（注意：传入的是 key 的列表）
    median = statistics.median(tool_nums_distribution.keys())
    # 归一化处理（偏离程度）
    scaling_factor = abs(selected_tool_count - median) / (max_tools - median) +1
    print(scaling_factor)

    if selected_tool_count > max_tools // 2:  
        # 当选择的工具数量较多时：
        base_mode_weights["multiple"] *= scaling_factor**2.5  # 提高 "multiple" 权重
        base_mode_weights["dependent"] *= scaling_factor**2.5  # 提高 "dependent" 权重
        base_mode_weights["no_tool_use"] *= scaling_factor**2  # 提高 "no_tool_use" 权重
        base_mode_weights["miss_param"] *= scaling_factor**2  # 提高 "no_tool_use" 权重
    else:  
        # 当选择的工具数量较少时：
        base_mode_weights["single"] *= scaling_factor**2.5  # 提高 "single" 权重
        base_mode_weights["parallel"] *= scaling_factor**2.5  # 提高 "parallel" 权重
        base_mode_weights["no_tool_use"] *= scaling_factor**2 # 提高 "no_tool_use" 权重
        base_mode_weights["miss_param"] *= scaling_factor**2  # 提高 "no_tool_use" 权重


    max_turns = max(task_turn_weights.keys())       # 任务轮次数最大值
    max_tools = max(tool_nums_distribution.keys())  # 工具数量最大值

    adjusted_task_turn_weights = {}
    scaling_factor = max(-((selected_tool_count - median) / (max_tools - median)) +1,0.1)
    for turn, weight in task_turn_weights.items():
        # 工具小于中位数时升序、工具大于中位数时降序、工具等于中位数时都为1
        # 防止调整后为负数或0（可选：设置最小值）
        adjusted_task_turn_weights[turn] = weight*scaling_factor**int(turn)

    # 归一化任务轮次权重，使总权重为 1
    total_weight = sum(adjusted_task_turn_weights.values())
    adjusted_task_turn_weights = {k: v / total_weight * 10 for k, v in adjusted_task_turn_weights.items()}

    return base_mode_weights, adjusted_task_turn_weights, selected_tool_count

# Example usage
if __name__ == "__main__":
    tool_nums_distribution = '{"9": 50, "8": 50, "7": 100, "6": 100, "5": 200, "4": 300, "3": 200, "2": 100, "1": 100}'
    tool_nums_distribution = '{"10": 300,"9": 300, "8": 400, "7": 400, "6": 400, "5": 500, "4": 400, "3": 300, "2": 0, "1": 0}'
    mode_weights, adjusted_task_turn_weights, selected_tool_count = dynamic_adjust_weights(tool_nums_distribution)

    # 输出最终调整后的权重
    print(f"选定的工具数量: {selected_tool_count}")
    print("-- 模式权重 (mode_weights) --")
    print(json.dumps(mode_weights, indent=2, ensure_ascii=False))
    print("-- 任务轮次权重 (task_turn_weights) --")
    print(json.dumps(adjusted_task_turn_weights, indent=2, ensure_ascii=False))
