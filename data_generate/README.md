# Function Call Data Generation Framework
一个强大的Agent工具调用数据生成框架，专门用于生成高质量的多轮Agent规划与工具使用对话数据，有效提升大语言模型的Agent规划和工具调用能力。基于我们生成的8k高质量数据，通过LoRA微调结合ToolRL强化学习训练qwen-32b-instruct模型后，在BFCL榜单的multi-turn指标上实现了从22.25%到45.88%的显著提升，性能提升幅度达到**105.8%**。在同等数据规模下，我们的数据为模型带来的精度提升显著超越当前所有主流Agent开源数据集（包括ToolACE、xLAM、ToolBench等），展现了卓越的数据质量和训练效果。
<div align="center">
  <img src="https://github.com/mocushile-gif/FunctionCallDataGenerate/blob/main/assets/pipeline.png?raw=true" width="100%" height="100%">
</div>

<br>

## 🚀 项目概述

本项目是一个**高质量多轮工具调用数据生成pipeline**，专门针对BFCL榜单上的multiturn指标进行优化。通过多智能体协作的方式，自动生成包含工具使用、文件系统操作、数据库查询等复杂场景的对话数据。

### 🎯 项目背景
目前开源研究中只公开模型和部分数据，无法通过开源数据大幅提高模型agent能力。现有开源多轮数据很少，即便有也是少量、多样性不足、无法根据业务针对性拓展。

### 🎯 项目目标
开发一个高质量数据生成pipeline，支持生成**高质量、多样、可任意定制拓展的多轮工具调用数据**，主要针对BFCL榜单上的multiturn指标进行优化。

## ✨ 核心特性

### 🏆 Pipeline特点
- **🎯 高质量**: 在数据生成前、中、后采用各种提高数据质量的方法
- **🔧 可拓展**: 可以任意添加工具和文件来生产自定义的agent数据
- **🌍 基于真实可执行环境**: 包含300个可执行工具 + 3400个RapidAPI工具
- **📁 环境可互动性**: 包含80+个不同格式文件作为base环境
- **🔄 工具调用模式多样性**: 支持single、parallel、multiple、dependent、no-tool-use、miss-param等模式
- **📊 多轮长上下文**: 目标生成的数据轮数可任意调整比例

### 🤖 多智能体架构
- **UserAgent**: 基于文件信息、工具、调用模式、语气风格生成贴近真实用户的任务指令
- **AssistantAgent**: 根据上下文和现有工具进行回复，支持众投模式
- **ToolAgent**: 在沙盒环境中执行工具，支持虚拟回复机制
- **CheckerAgent**: 多层次检查机制，确保数据质量

## 🏗️ 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   UserAgent     │    │ AssistantAgent  │    │   ToolAgent     │
│                 │    │                 │    │                 │
│ • 问题生成      │◄──►│ • 工具调用      │◄──►│ • 工具执行      │
│ • 任务澄清      │    │ • 响应生成      │    │ • 环境管理      │
│ • 人格模拟      │    │ • 众投机制      │    │ • 代码解释器    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  CheckerAgent   │    │   Pipeline      │    │   Tools         │
│                 │    │                 │    │                 │
│ • 质量检查      │    │ • 流程控制      │    │ • 文件系统      │
│ • 错误修正      │    │ • 状态管理      │    │ • 数据库       │
│ • 重试机制      │    │ • 数据保存      │    │ • API调用       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 项目结构

```
function_call_data/
├── data_generate/
│   ├── agent/                    # 智能体模块
│   │   ├── user_agent.py        # 用户智能体
│   │   ├── assistant_agent.py   # 助手智能体
│   │   ├── tool_agent.py        # 工具智能体
│   │   ├── checker_agent.py     # 检查智能体
│   │   ├── model/               # LLM模型接口
│   │   └── rapidapi.py          # RapidAPI集成
│   ├── prompt                    # 提示词模板
│   ├── scripts                    # 数据生产脚本
│   ├── tools/                    # 工具系统
│   │   ├── executable_functions/ # 可执行工具
│   │   └── defines/             # 工具定义
│   ├── utils                    # 工具函数集合
│   ├── working_dir/             # 文件系统（智能体交互的环境）
│   ├── .env                    # 环境变量设置
│   └── pipeline.py              # 主流程控制
```

## 🎯 主要功能

### 1. 智能体系统

#### UserAgent (用户智能体)
- **问题生成**: 基于给定文件信息（n个文件的前10行内容和基本信息）、给定工具、给定调用模式、给定语气风格生成贴近真实用户的任务指令
- **任务澄清**: 每次assistant给出总结回复时判断任务是否完成，若无法完成则记录为-1，若完成则进入下一个turn
- **环境补充**: 若任务需要补充信息时，基于环境给出真实补充信息，避免虚构信息
- **人格模拟**: 从persona_hub采样人格类型，支持不同语气风格

#### AssistantAgent (助手智能体)
- **工具调用**: 根据上下文和现有工具进行回复，无法看到环境和文件内容，需要使用特定工具来访问环境
- **众投模式**: 每次生成n个回复，选择最多的回复（如3次里2次都选择了同一个工具）
- **多模型支持**: 支持GPT、Qwen、DeepSeek、豆包等多种LLM模型
- **推理能力**: 支持推理模型的思维链输出

#### ToolAgent (工具智能体)
- **沙盒环境**: 每条数据都建立对应的沙盒环境用于储存对应文件资料
- **工具执行**: 安全执行300个可执行工具（Python函数、文件操作、数据库、统计分析、可视化、操作系统、图像处理、外部API等）
- **RapidAPI集成**: 支持3400个RapidAPI工具，若执行失败则切换虚拟回复
- **输出控制**: 超过特定长度的回复进行截断
- **虚拟回复**: 对于RapidAPI工具，若真实回复出错，则基于历史回复cache使用模型进行虚拟回复

#### CheckerAgent (检查智能体)
- **多层次检查**: 每次assistant agent回复时都给出反馈
- **Rule Checker**: 检查工具是否存在、参数是否存在、参数数据类型是否符合、必需的参数是否都有
- **LLM Checker**: 对于没有调用工具的回复进行检查
- **Tool Call Checker**: 对于调用了工具的回复进行检查
- **重试机制**: 最多反馈n次，若n次都没有pass，则为pass

### 2. 工具系统

#### 工具类型
- **可执行工具**: 300个Python函数，涵盖文件操作、数据库、统计分析、可视化、操作系统、图像处理、外部API等
- **RapidAPI工具**: 3400个API工具，支持虚拟回复机制
- **文件系统工具**: 文件操作、目录遍历、内容读取等
- **数据库工具**: 表结构查询、数据检索、SQL执行等
- **图像处理工具**: 图像分析、处理、生成等
- **Python工具**: 代码执行、数据分析等

#### 工具调用模式
- **Single**: 单工具调用
- **Parallel**: 并行工具调用
- **Multiple**: 多工具调用
- **Dependent**: 依赖工具调用
- **No-tool-use**: 不使用工具
- **Miss-param**: 参数缺失情况

### 3. 文件系统

Agent与环境互动的文件系统，**完全支持自定义配置**，可以根据不同的数据生成需求进行个性化配置。

#### 文件系统特性
- **多样的文件类型**: 目前给出了80+个不同格式的文件作为agent与环境互动的基础（txt、excel、csv、pdf、jpg、json、db数据库等）
- **灵活的文件结构**: 可以创建任意深度的目录结构，模拟真实的文件系统环境
- **动态文件采样**: 支持随机采样指定数量的文件，增加数据生成的多样性
- **临时工作目录**: 每次数据生成都会创建独立的临时文件系统副本，确保数据隔离


### 4. 数据生成流程

```
1. 初始化Pipeline
   ├── 工具采样和配置（支持动态权重调整）
   ├── 文件系统准备（80+种格式文件）
   └── 智能体初始化（沙盒环境）

2. 问题生成阶段
   ├── UserAgent基于文件信息、工具、调用模式、语气风格生成问题
   ├── 支持多种任务模式（single、parallel、multiple、dependent等）
   └── 从persona_hub采样人格类型

3. 问题解决阶段
   ├── AssistantAgent分析问题（无法看到环境和文件内容）
   ├── 选择合适的工具（需要调用工具访问环境）
   ├── ToolAgent在沙盒环境中执行工具
   └── 循环直到任务完成或达到最大轮数

4. 质量检查阶段
   ├── CheckerAgent多层次检查（rule checker、llm checker、tool call checker）
   ├── 错误修正和重试（最多n次）
   └── 确保数据质量

5. 数据后处理
   ├── 筛选存在幻觉、过长、任务无法完成的数据
   ├── 格式转换（支持yaml、toolace、xml、qwen、openai等格式）
   └── 清理临时资源和沙盒环境
```

### 5. 实验与结果

基于当前工具系统和文件系统，我们生成了8k条多轮工具调用数据，并基于qwen-32b模型进行LoRA微调，并在此基础上利用ToolRL框架进行了RL训练，当前BFCL榜单上排名第5，已达到Deepseek-R1的效果。以下是详细的实验结果：

#### 实验配置
- **数据规模**: 8k条多轮工具调用数据
- **基础模型**: qwen2.5-32b-instruct
- **微调方法**: LoRA (Low-Rank Adaptation)
- **评估基准**: BFCL (Berkeley Function Call Leaderboard)

#### 实验结果对比

| 实验名称 | 数据量 | BFCL Overall | Multi-turn All | Multi-turn Base | Miss Func | Miss Param | Long Context |
|----------|--------|--------------|----------------|-----------------|-----------|------------|--------------|
| **ToolRL (pretrain model 37.38) step 300** | 61,308 (单轮) 16k | **71.47%** | **45.875%** | **58.50%** | **35.50%** | **37.00%** | **52.50%** |
| **ToolRL (pretrain model 37.38) step 300** | 43,530 (单轮) 8k | 70.57% | 44.00% | 56.50% | 34.00% | 36.50% | 49.00% |
| **qwen2.5-32b-0616-v12500yaml-v2gpt2500toolace-v3gpt2500qwen-qwq500missfunc-epoch5** | 8,000 | 66.19% | 37.38% | 48.50% | 29.50% | 30.00% | 41.50% |
| **qwen2.5-32b-0614-v12500yaml-v2gpt2500toolace-v3gpt2500qwen-epoch5** | 7,500 | 66.74% | 36.75% | 50.5% | 27.5% | 29% | 40% |
| **qwen2.5-32b-0613-v12500yaml-v2gpt1500qwen-v3gpt1000toolace-epoch5** | 6,000 | 65.70% | 34.62% | 42.50% | 28.00% | 30.50% | 37.50% |
| **qwen2d5_32B_instruct (原始模型)** | - | 62.79% | 22.25% | 29.5% | 25.5% | 20.5% | 13.5% |
| **xLAM-2-32b-fc-r (FC)** | - | 76.43% | 67.12% | 79% | 71.5% | 63.5% | 54.5% |
| **GPT-4o-2024-11-20 (FC)** | - | 71.71% | 50% | 61% | 45.5% | 35.5% | 58% |

#### 关键发现

1. **微调效果显著**: 相比原始qwen2.5-32b模型，LoRA微调后在各项指标上都有显著提升
2. **数据质量影响**: 数据量从6k增加到8k，模型性能有稳定提升
3. **格式混合训练**: 采用多种格式混合训练策略，提升了模型的泛化能力
4. **与SOTA对比**: 在部分任务上接近或达到当前最优水平

#### 评估指标说明

- **BFCL Overall**: 综合功能调用能力评分
- **Multi-turn All**: 多轮对话整体表现
- **Multi-turn Base**: 基础多轮对话能力
- **Miss Func**: 函数缺失情况处理能力
- **Miss Param**: 参数缺失情况处理能力
- **Long Context**: 长上下文理解能力         



## 🚀 快速开始

### 环境要求

```bash
# Python 3.8+
cd data_generate
pip install -e .
```

### 环境准备

```bash
# 设置环境变量
export PROJECT_DIR=$(pwd)
export HOME_DIR=$HOME

# 准备文件系统环境（80+种格式文件）
mkdir -p working_dir/file_system
# 添加txt、excel、csv、pdf、jpg、json等格式文件

# 配置.env文件
cp .env.example .env
# 编辑.env文件，配置API密钥等
```

### 基本使用

```python
from data_generate.pipeline import Pipeline

# 创建Pipeline实例
pipeline = Pipeline(
    tool_defines_path=['./tools/defines/'],
    save_path='./output/data.jsonl',
    failed_save_path='./output/failed.jsonl',
    max_task_turns=3,
    assistant_model_name='gpt4o-ptu-client',
    # 工具配置
    tool_nums_distribution={1: 200, 2: 140, 3: 120, 4: 100, 5: 90},
    # 调用模式权重
    mode_weights={"single": 1, "parallel": 1, "multiple": 1, "dependent": 1, "no_tool_use": 1, "miss_param": 1},
    # 任务轮数权重
    task_turn_weights={1: 0.5, 2: 0.3, 3: 0.2}
)

# 生成数据
data = {'data_id': 'test_001'}
success = pipeline._generate(data, save=True)
```

### 命令行使用

```bash
# 基本数据生成
python pipeline.py --target_generate_data_number 100

# 指定工具和模型
python pipeline.py \
    --tool_defines_path "['./tools/defines/file_system_functions']" \
    --assistant_model_name "gpt4o-ptu-client" \
    --target_generate_data_number 50

# 多线程生成
python pipeline.py \
    --num_workers 4 \
    --target_generate_data_number 200
```

## ⚙️ 配置选项

### 核心参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `tool_defines_path` | 工具定义路径列表 | `['./tools/defines/']` |
| `save_path` | 成功数据保存路径 | `./generated_data/data.jsonl` |
| `failed_save_path` | 失败数据保存路径 | `./generated_data/failed.jsonl` |
| `max_task_turns` | 最大任务轮数 | `3` |
| `checker_max_retries` | 检查器最大重试次数 | `1` |
| `assistant_n_response` | 助手响应数量（众投） | `1` |
| `tool_nums_distribution` | 工具数量分布权重 | `{1: 200, 2: 140, 3: 120, 4: 100, 5: 90}` |
| `mode_weights` | 工具调用模式权重 | `{"single": 1, "parallel": 1, "multiple": 1, "dependent": 1, "no_tool_use": 1, "miss_param": 1}` |
| `task_turn_weights` | 任务轮数权重 | `{1: 0.5, 2: 0.3, 3: 0.2}` |
| `files_num` | 文件数量分布 | `{1: 0, 2: 0.2, 3: 0.3, 4: 0.3, 5: 0.2}` |

### 模型配置

| 参数 | 说明 | 支持值 |
|------|------|--------|
| `assistant_model_name` | 助手模型名称 | `gpt4o-ptu-client`, `qwq`, `qwen`, `deepseek` |
| `user_model_name` | 用户模型名称 | 同上 |
| `tool_model_name` | 工具模型名称 | 同上 |
| `checker_model_name` | 检查器模型名称 | 同上 |

### 工具配置

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `fixed_tools` | 固定工具列表 | `[]` |
| `tool_nums_distribution` | 工具数量分布权重 | `{1: 200, 2: 140, 3: 120, 4: 100, 5: 90}` |
| `category_fixed_tools` | 分类固定工具 | `{'file_system_functions': ['display_directory_tree', 'get_file_info'], 'database_functions': ['get_database_info']}` |
| `tool_output_limit` | 工具输出限制 | `4096` |
| `dynamic_adjust_mode_and_task_turn_weight` | 动态调整权重 | `False` |

### 文件系统配置

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `file_system_path` | 文件系统根路径 | `./working_dir/file_system/` |
| `files_num` | 文件数量分布 | `{1: 0, 2: 0.2, 3: 0.3, ...}` |
| `provide_file_system_info` | 文件系统信息提供方式 | `'none'` |


## 📊 数据格式

### 生成的数据结构

```json
{
    "data_id": "unique_id",
    "messages": [
        {"role": "system", "content": "系统提示词"},
        {"role": "user", "content": "用户问题"},
        {"role": "assistant", "content": "助手响应", "tool_calls": [...]},
        {"role": "tool", "content": "工具执行结果"},
        {"role": "user", "content": "任务澄清或完成确认"}
    ],
    "tools": ["使用的工具列表"],
    "assistant_reasonings": {"推理过程"},
    "selected_files": ["涉及的文件"],
    "checker_not_pass_index": [检查未通过的索引],
    "task_complete_index": [任务完成索引],
    "is_task_completable": [任务可完成性],
    "dialog_mode": ["对话模式"],
    "round_cnt": 任务轮数
}
```


## 🤝 贡献指南

### 开发环境设置

```bash
# 克隆项目
git clone [<repository_url>]
cd function_call_data

# 安装依赖
pip install -e .

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 邮件联系: mocuishle439@gmail.com
- 项目主页: [GitLab Repository](https://github.com/mocushile-gif/FunctionCallDataGenerate/tree/main/data_generate)

---
