#!/bin/bash

PROJECT=/mnt/nvme0/qinxinyi/function_call_data/data_generate/generated_data
api_key=afe0db0493a44726968df6606244badb

# 数据路径 (数据报告默认存放此处)
data_dir=$PROJECT/executable_tools

# 单独进行分类（run_score默认会进行分类，无需使用该脚本）
python $PROJECT/category.py \
    --data_dir $data_dir \
    --label_data_dir $data_dir/sampled2 \
    --category_data_dir $data_dir/category_data