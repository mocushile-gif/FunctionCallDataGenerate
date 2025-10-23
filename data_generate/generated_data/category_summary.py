import os
import json
import pandas as pd
from collections import Counter

def load_data_from_folder(folder_path):
    """加载文件夹中的所有JSON文件，并合并为一个DataFrame"""
    data = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            with open(os.path.join(folder_path, filename), 'r') as file:
                for line in file:
                    data.append(json.loads(line))
    return pd.DataFrame(data)

def generate_tool_statistics(df):
    """统计工具调用数量及调用量Top 20的工具"""
    all_tools = Counter()
    tool_num = Counter()
    all_calls = Counter()

    for tools in df['tools_lst']:
        all_tools.update(tools)
        tool_num[len(tools)]+=1

    for call in df['tool_call_lst']:
        all_calls.update(call)

    top_20_tools = all_calls.most_common(20)
    return all_tools, top_20_tools, all_calls,tool_num

def generate_call_mode_statistics(df):
    """统计单工具调用、平行工具调用、串联工具调用的数量和占比"""
    total_rounds = df['round'].sum()
    total_calls = sum(sum(call_counts.values()) for call_counts in df["tool_count_per_call"])
    single_calls = df['single_tool_call'].sum()
    single_from_multiple_calls = df['single_tool_call_from_multiple'].sum()
    parallel_calls = df['parallel_tool_call'].sum()
    multiple_calls = df['multiple_tool_call'].sum()
    sequential_calls = df['sequential_tool_call'].sum()
    total_rounds_with_tool_calls = df["round_with_tool_calls"].sum()


    # 统计 tool_count_per_call
    tool_count_stats = Counter()
    for count_dict in df['tool_count_per_call']:
        tool_count_stats.update(count_dict)

    # 统计 tool_sequence_per_question
    tool_sequence_stats = Counter()
    for seq_dict in df['tool_sequence_per_question']:
        tool_sequence_stats.update(seq_dict)

    #  取出共现次数最高的前20对工具
    co_occurrences=Counter()
    total_co_occurrences=0
    for tools in df['tool_call_lst']:
        tools = list(tools.keys())
        for i in range(len(tools)):
            for j in range(i + 1, len(tools)):
                co_occurrences[(tools[i], tools[j])] += 1
                total_co_occurrences += 1  # 累计总的共现次数

    top_co_occurrences = co_occurrences.most_common(20)

    # 计算每对工具的共现占比，并添加到结果中
    top_co_occurrences_with_ratio = [(pair, count, count / total_co_occurrences) for pair, count in top_co_occurrences]


    # 统计每条数据中工具调用数量及占比
    tools_per_data = df['tool_call_lst'].apply(lambda x: sum(x.values()))
    total_tools_per_data = tools_per_data.sum()
    tools_per_data_stats = tools_per_data.value_counts().to_dict()
    tools_per_data_percent = {k: v / len(df) * 100 for k, v in tools_per_data_stats.items()}

    # 统计每条数据中调用的不同工具总数量及占比
    unique_tools_per_data = df['tool_call_lst'].apply(lambda x: len(x))
    total_unique_tools = unique_tools_per_data.sum()
    unique_tools_per_data_stats = unique_tools_per_data.value_counts().to_dict()
    unique_tools_per_data_percent = {k: v / len(df) * 100 for k, v in unique_tools_per_data_stats.items()}

    return {
        'Total Calls': total_calls,
        'Single Tool Calls': single_calls,
        'Single from Multiple Tool Calls':single_from_multiple_calls,
        'Parallel Tool Calls': parallel_calls,
        'Multiple Tool Calls': multiple_calls,
        'Round with Tool Calls': total_rounds_with_tool_calls,
        'Round with Sequential Tool Calls': sequential_calls,
        'Single Tool Calls %': single_calls / total_calls * 100,
        'Single from Multiple Tool Calls %': single_from_multiple_calls / total_calls * 100,
        'Parallel Tool Calls %': parallel_calls / total_calls * 100,
        'Multiple Tool Calls %': multiple_calls / total_calls * 100,
        'Total Rounds': total_rounds,
        'Round with Tool Calls %': total_rounds_with_tool_calls / total_rounds * 100,
        'Round with Sequential Tool Calls %': sequential_calls / total_rounds * 100,
        'Tool Count Per Call': tool_count_stats,
        'Tool Sequence Per Round': tool_sequence_stats,
        'Tools Per Data': tools_per_data_stats,
        'Tools Per Data Percent': tools_per_data_percent,
        'Unique Tools Per Data': unique_tools_per_data_stats,
        'Unique Tools Per Data Percent': unique_tools_per_data_percent,
        'Top 20 Co-occurrence Tool Pair': top_co_occurrences_with_ratio,
    }

def generate_round_statistics(df):
    """统计轮次数量及占比"""
    total_data = len(df)
    round_counts = df['round'].value_counts()
    round_stats = round_counts.to_dict()
    round_percent = {k: v / total_data * 100 for k, v in round_stats.items()}

    # 只显示Top 20
    top_20_rounds = dict(list(round_stats.items())[:20])
    top_20_percent = {k: round_percent[k] for k in top_20_rounds.keys()}

    return top_20_rounds, top_20_percent

def create_html_report(data_path,df,tool_stats, call_mode_stats, round_stats):
    """生成HTML统计报告"""
    total_tools_calls = sum(tool_stats[2].values())
    total_tool_count_calls = sum(call_mode_stats['Tool Count Per Call'].values())
    total_tool_seq_calls = sum(call_mode_stats['Tool Sequence Per Round'].values())

    html_content = f"""
    <html>
    <head>
        <title>工具调用数据统计报告</title>
        <style>
            body {{font-family: Arial, sans-serif; background-color: #f4f4f9; color: #333;}}
            table {{width: 45%; border-collapse: collapse; margin: 0 20px;}}
            th, td {{border: 1px solid #ddd; padding: 8px; transition: background-color 0.3s ease;}}
            th {{background-color: #333; color: #fff; text-align: center;}}
            td {{background-color: #fff; text-align: center;}}
            a {{color: #004080; text-decoration: underline; border-bottom: 2px solid transparent; transition: border-bottom 0.3s;}}
            a:hover {{border-bottom: 2px solid #004080;}}
            .highlight {{font-weight: bold; background-color: #FFFF00;}}
            .charts, .intent-section, .tables {{display: flex; justify-content: space-around; width: 100%;}}
            .charts div, .tables table, .intent-section table, .intent-section div {{
                flex: 1 1 30%;
                margin: 10px;
                min-width: 300px;
            }}
            .charts iframe, .intent-section iframe {{
                width: 100%;
                height: auto;
                aspect-ratio: 16 / 9;
                border: none;
                margin: 0;
                padding: 0;
            }}
        </style>
    </head>
    <body>
        <h1>工具调用数据统计报告</h1>

        <h2>数据总量：{len(df)}</h2>

        <h2>1. 涉及工具总数目以及调用量Top 20的工具</h2>
        <p>涉及工具总数：{len(tool_stats[0])}</p>
        <table border="1">
            <tr><th>工具名称</th><th>调用量</th><th>占比</th></tr>
            {"".join(f"<tr><td>{tool}</td><td>{count}</td><td>{(count / total_tools_calls * 100):.2f}%</td></tr>" for tool, count in tool_stats[1])}
        </table>

        <h2>2. 每条数据给定的工具个数统计</h2>
        <table border="1">
            <tr><th>工具名称</th><th>调用量</th><th>占比</th></tr>
            {"".join(f"<tr><td>{number}</td><td>{count}</td><td>{(count / len(df) * 100):.2f}%</td></tr>" for number, count in tool_stats[3].items())}
        </table>

        <h2>2. 共现频率Top 20的工具对</h2>
        <table border="1">
            <tr><th>工具1</th><th>工具2</th><th>共现次数</th><th>占比</th></tr>
            {"".join(f"<tr><td>{tool1}</td><td>{tool2}</td><td>{count}</td><td>{(ratio *100):.2f}%</td></tr>" for (tool1, tool2), count, ratio in call_mode_stats['Top 20 Co-occurrence Tool Pair'])}
        </table>

        <h2>3. 每条数据中工具调用总数量及占比</h2>
        <table border="1">
            <tr><th>工具调用总数量</th><th>数量</th><th>占比</th></tr>
            {"".join(f"<tr><td>{count}</td><td>{freq}</td><td>{percent:.2f}%</td></tr>" for count, (freq, percent) in zip(call_mode_stats['Tools Per Data'].keys(), zip(call_mode_stats['Tools Per Data'].values(), call_mode_stats['Tools Per Data Percent'].values())))}
        </table>

        <h3>每条数据中调用不同工具的总数量及占比</h2>
        <table border="1">
            <tr><th>调用不同工具总数量</th><th>数量</th><th>占比</th></tr>
            {"".join(f"<tr><td>{count}</td><td>{freq}</td><td>{percent:.2f}%</td></tr>" for count, (freq, percent) in zip(call_mode_stats['Unique Tools Per Data'].keys(), zip(call_mode_stats['Unique Tools Per Data'].values(), call_mode_stats['Unique Tools Per Data Percent'].values())))}
        </table>

        <h2>4. 工具调用中单工具调用、平行工具调用数量及占比</h2>
        <table border="1">
            <tr><th>调用类型</th><th>数量</th><th>占比</th></tr>
            <tr><td>总调用次数</td><td>{call_mode_stats['Total Calls']}</td><td>100%</td></tr>
            <tr><td>单工具调用（仅给了单个工具）</td><td>{call_mode_stats['Single Tool Calls']}</td><td>{call_mode_stats['Single Tool Calls %']:.2f}%</td></tr>
            <tr><td>单工具调用（但给了多个工具）</td><td>{call_mode_stats['Single from Multiple Tool Calls']}</td><td>{call_mode_stats['Single from Multiple Tool Calls %']:.2f}%</td></tr>
            <tr><td>平行工具调用</td><td>{call_mode_stats['Parallel Tool Calls']}</td><td>{call_mode_stats['Parallel Tool Calls %']:.2f}%</td></tr>
            <tr><td>多工具调用</td><td>{call_mode_stats['Multiple Tool Calls']}</td><td>{call_mode_stats['Multiple Tool Calls %']:.2f}%</td></tr>
        </table>

        <h3>工具调用个数分布 (每次调用时调用的工具个数)</h3>
        <table border="1">
            <tr><th>调用个数</th><th>数量</th><th>占比</th></tr>
            {"".join(f"<tr><td>{count}</td><td>{freq}</td><td>{(freq / total_tool_count_calls * 100):.2f}%</td></tr>" for count, freq in call_mode_stats['Tool Count Per Call'].items())}
        </table>

        <h2>5. 轮次中工具调用、串联工具调用数量及占比</h2>
        <table border="1">
            <tr><th>轮次</th><th>数量</th><th>占比</th></tr>
            <tr><td>总轮次</td><td>{call_mode_stats['Total Rounds']}</td><td>100%</td></tr>
            <tr><td>有工具调用的轮次</td><td>{call_mode_stats['Round with Tool Calls']}</td><td>{call_mode_stats['Round with Tool Calls %']:.2f}%</td></tr>
            <tr><td>有串联工具调用的轮次</td><td>{call_mode_stats['Round with Sequential Tool Calls']}</td><td>{call_mode_stats['Round with Sequential Tool Calls %']:.2f}%</td></tr>
        </table>

        <h3>工具调用序列分布 (每轮中连续调用工具的序列长度)</h3>
        <table border="1">
            <tr><th>调用序列长度</th><th>数量</th><th>占比</th></tr>
            {"".join(f"<tr><td>{seq}</td><td>{freq}</td><td>{(freq / total_tool_seq_calls * 100):.2f}%</td></tr>" for seq, freq in call_mode_stats['Tool Sequence Per Round'].items())}
        </table>

        <h2>6. 轮次统计及占比 (Top 20)</h2>
        <table border="1">
            <tr><th>轮次数量</th><th>数量</th><th>占比</th></tr>
            {"".join(f"<tr><td>{round_}</td><td>{count}</td><td>{percent:.2f}%</td></tr>" for round_, (count, percent) in zip(round_stats[0].keys(), zip(round_stats[0].values(), round_stats[1].values())))}
        </table>
    </body>
    </html>
    """
    with open(f'{data_path}/tool_usage_report.html', 'w') as f:
        f.write(html_content)
    print("HTML报告已生成：tool_usage_report.html")

def generate_report(data_path,category_data_path):
    df = load_data_from_folder(category_data_path)
    # 生成统计数据
    tool_stats = generate_tool_statistics(df)
    call_mode_stats = generate_call_mode_statistics(df)
    round_stats = generate_round_statistics(df)
    # 生成HTML报告
    create_html_report(data_path,df,tool_stats, call_mode_stats, round_stats)

if __name__ == "__main__":
    # 主程序
    data_path='/mnt/nvme0/qinxinyi/fc_score/data'
    category_data_path = '/mnt/nvme0/qinxinyi/fc_score/data/categories'  # 替换为文件夹路径
    generate_report(data_path,category_data_path)
