import random
from collections import defaultdict

def select_files_for_fsps(fsp, tool_file_graph):
    tool_files = defaultdict(list)  # func -> list of files（一个函数多次出现就存多个）
    all_funcs = [func for turn in fsp for func in turn]

    for func in all_funcs:
        relevant_files = set(tool_file_graph.get(func, []))
        if not relevant_files:
            tool_files[func].append(None)
            continue

        # 获取其他函数的相关文件
        other_funcs = [f for f in all_funcs if f != func]
        other_files = set()
        for other in other_funcs:
            other_files.update(tool_file_graph.get(other, []))

        intersect = relevant_files & other_files
        if intersect:
            selected = random.choice(list(intersect))
        else:
            selected = random.choice(list(relevant_files))

        tool_files[func].append(selected)  # 每次都添加一次对应文件

    # 构造与 fsp 同结构的文件名列表（逐次消费 tool_files[func] 中的文件）
    file_fsp = []
    for turn in fsp:
        turn_files = []
        for func in turn:
            file = tool_files[func].pop(0)
            turn_files.append(file)
        file_fsp.append(turn_files)

    return file_fsp



if __name__ == "__main__":
    fsp = [['copy_file','copy_file'], ['compress_files', 'delete_file'],['search']]
    tool_file_graph = {
        'copy_file': ['a.txt', 'b.csv'],
        'compress_files': ['b.txt', 'c.txt'],
        'delete_file': ['c.txt', 'd.txt'],
        'search':[],
    }
    print(select_files_for_fsps(fsp, tool_file_graph))

