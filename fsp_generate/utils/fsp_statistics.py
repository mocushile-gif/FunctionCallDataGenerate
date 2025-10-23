from collections import Counter
import pandas as pd
pd.set_option('display.max_rows', None)  # Display all rows
pd.set_option('display.max_columns', None)  # Display all columns
pd.set_option('display.max_colwidth', None)

def fsps_statistics(fsp_lists):
    # 每个多轮任务列表单独统计（不展开）
    grouped_totals = []

    for tasklist in fsp_lists:
        group_counter = Counter()
        for sublist in tasklist:
            counter = Counter(sublist)
            total_tool_calls = sum(counter.values()) - counter.get('__miss func__', 0)

            multiple_or_dependent = 1 if len(counter)- counter.get('__miss params__', 0) > 1 else 0
            parallel = 1 if any(v > 1 for v in counter.values()) else 0
            miss_func = counter.get('__miss func__', 0)
            miss_params = counter.get('__miss params__', 0)
            single = 1 if total_tool_calls == 1 and not miss_func and not miss_params else 0

            summary = {
                'multiple_or_dependent': multiple_or_dependent,
                'parallel': parallel,
                'single': single,
                'miss_func': miss_func,
                'single_miss_params': miss_params,
                'total_tool_calls': total_tool_calls,
                'total_turns': 1,
            }
            # print(sublist)
            flags = [multiple_or_dependent, parallel, single, miss_func, miss_params]
            assert sum(flags)==1

            group_counter.update(summary)

        n_subtasks = len(tasklist)
        grouped_totals.append(group_counter)

    # 先合并所有组的 total
    combined_total = sum(grouped_totals, Counter())

    # 再计算平均（除以组数）
    num_groups = len(grouped_totals)
    combined_average = {k: round(v / num_groups, 2) for k, v in combined_total.items()}

    # 转为 DataFrame 展示
    df_summary_all = pd.DataFrame([combined_total, combined_average], index=["total", "average"])

    return df_summary_all


if __name__ == "__main__":
    fsp_lists = [[['count_files_in_dir', 'count_files_in_dir'], 
    ['__miss func__'], 
    ['group_t_test', 'count_bits', 'compute_circle_properties'], 
    ['get_text_length'], 
    ['calculator'], 
    ['__miss params__'], 
    ['paired_t_test_from_database'], 
    ['create_histogram']],
    [['check_table_null_values'], 
    ['__miss params__'], 
    ['delete_file_or_directory'], 
    ['__miss func__'], 
    ['get_first_n_rows'], 
    ['create_pie_chart'], 
    ['delete_from_table', 'insert_into_table']]]
    summary=fsps_statistics(fsp_lists)
    print(summary)