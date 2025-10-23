# Function Call Data Generation Framework
一个强大的Agent工具调用数据生成框架，专门用于生成高质量的多轮Agent规划与工具使用对话数据，有效提升大语言模型的Agent规划和工具调用能力。基于我们生成的8k高质量数据，通过LoRA微调结合ToolRL强化学习训练qwen-32b-instruct模型后，在BFCL榜单的multi-turn指标上实现了从22.25%到45.88%的显著提升，性能提升幅度达到**105.8%**。在同等数据规模下，我们的数据为模型带来的精度提升显著超越当前所有主流Agent开源数据集（包括ToolACE、xLAM、ToolBench等），展现了卓越的数据质量和训练效果。
<div align="center">
  <img src="https://github.com/mocushile-gif/FunctionCallDataGenerate/blob/main/assets/pipeline.png?raw=true" width="100%" height="100%">
</div>

<br>

一个强大的函数调用数据生成框架，用于生成高质量的AI工具使用对话数据。

## 🚀 项目概述

本项目是一个**高质量多轮工具调用数据生成pipeline**，专门针对BFCL榜单上的multiturn指标进行优化。通过多智能体协作的方式，自动生成包含工具使用、文件系统操作、数据库查询等复杂场景的对话数据。
- **No-tool-use**: 不使用工具
- **Miss-param**: 参数缺失情况

### 3. 数据生成流程
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
# 克隆项目
git clone <repository_url>
cd function_call_data

# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export PROJECT_DIR=$(pwd)
export HOME_DIR=$HOME
```
pip install -e .

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 邮件联系: mocuishle439@gmail.com
---
