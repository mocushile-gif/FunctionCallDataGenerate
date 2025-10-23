import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from category_code import get_category
from category_summary import generate_report
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process time parameters.')
    parser.add_argument('--data_dir', type=str,  default='data', help='报告存放的路径')
    parser.add_argument('--label_data_dir', type=str,  default='data/label_data', help='需要进行分类的数据存放的路径')
    parser.add_argument('--category_data_dir', type=str,  default='data/category_data', help='分类数据存放路径')
    args = parser.parse_args()

    get_category(args.label_data_dir,args.category_data_dir)
    generate_report(args.data_dir,args.category_data_dir)
    