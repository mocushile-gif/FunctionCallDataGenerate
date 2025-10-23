import random
from datetime import datetime, timedelta

def random_current_time_generate():
    # 设置日期范围
    start_date = datetime(2020, 1, 1, 0, 0, 0)  # 从2020年1月1日00:00:00开始
    end_date = datetime(2025, 1, 21, 23, 59, 59)  # 到2025年1月21日23:59:59

    # 计算日期范围内的秒数差
    delta = end_date - start_date

    # 随机生成一个秒数差
    random_seconds = random.randint(0, delta.total_seconds())

    # 生成随机日期和时间
    random_datetime = start_date + timedelta(seconds=random_seconds)

    # 输出随机生成的日期和时间
    print("随机生成的日期和时间:", random_datetime.strftime('%Y-%m-%d %H:%M:%S'))
    return random_datetime.strftime('%Y-%m-%d %H:%M:%S')

# Example usage
if __name__ == "__main__":
    print(random_current_time_generate())