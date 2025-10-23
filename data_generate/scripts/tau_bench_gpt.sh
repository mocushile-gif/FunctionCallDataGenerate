#!/bin/bash
PROJECT=$(dirname $(dirname "$(realpath "$0")"))
executable_temp_working_dir="/mnt/afs2/qinxinyi/function_call_data_temp"
# 清空目录内容但保留目录本身
# rm -rf "${executable_temp_working_dir:?}"/*

# export http_proxy=http://proxy.sensetime.com:3128/
# export https_proxy=http://proxy.sensetime.com:3128/
# export HTTP_PROXY=http://proxy.sensetime.com:3128/
# export HTTPS_PROXY=http://proxy.sensetime.com:3128/
export https_proxy=http://tool_chain_team:c1231c80eb75@10.119.176.202:3128
export http_proxy=http://tool_chain_team:c1231c80eb75@10.119.176.202:3128
export NO_PROXY=localhost,127.0.0.1,101.230.144.204,103.177.28.206,8.130.32.149,101.230.144.223,101.230.144.221

save_path="$PROJECT/generated_data/executable_tools/generated/tau_bench/generate_tau_bench_airline_gpt.jsonl"
failed_save_path="$PROJECT/generated_data/executable_tools/failed/failed_generate_tau_bench_airline_gpt.jsonl"
tool_defines_path="['$PROJECT/tools/defines/tau_bench/tau_bench_airline']"
file_system_path="$PROJECT/working_dir/tau_bench_airline"


save_path="$PROJECT/generated_data/executable_tools/generated/tau_bench/generate_tau_bench_retail_gpt.jsonl"
failed_save_path="$PROJECT/generated_data/executable_tools/failed/failed_generate_tau_bench_retail_gpt.jsonl"
tool_defines_path="['$PROJECT/tools/defines/tau_bench/tau_bench_retail']"
file_system_path="$PROJECT/working_dir/tau_bench_retail"

num_workers=10 #多线程生成
target_generate_data_number=200
checker_max_retries=1 #checker重试次数
assistant_n_response=1 #众投次数

python $PROJECT/pipeline_tau_bench.py \
    --executable_temp_working_dir $executable_temp_working_dir \
    --save_path $save_path \
    --failed_save_path $failed_save_path \
    --num_workers $num_workers \
    --checker_max_retries $checker_max_retries \
    --assistant_n_response $assistant_n_response \
    --target_generate_data_number $target_generate_data_number \
    --tool_defines_path $tool_defines_path \
    --assistant_model_name 'gpt' \
    --checker_model_name 'gpt' \
    --user_model_name 'gpt' \
    --tool_model_name 'gpt' \
    --lang 'en' \
    --task_turn_weights '{"1":1,"2":1,"3":1,"4":1}' \
    --mode_weights '{"single":1, "parallel":1, "multiple":1, "dependent":1, "no_tool_use":1, "miss_param":1,"task":0}' \
    --file_system_path $file_system_path \
    # --use_persona \