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

save_path="$PROJECT/generated_data/executable_tools/generated/generate_executable_sql_tools.jsonl"
failed_save_path="$PROJECT/generated_data/executable_tools/failed/failed_generate_executable_sql_tools.jsonl"
tool_defines_path="['$PROJECT/tools/defines/database_functions']"
save_path="$PROJECT/generated_data/executable_tools/generated/generate_executable_file_tools.jsonl"
failed_save_path="$PROJECT/generated_data/executable_tools/failed/failed_generate_executable_file_tools.jsonl"
tool_defines_path="['$PROJECT/tools/defines/file_system_functions']"
save_path="$PROJECT/generated_data/executable_tools/generated/generate_executable_python_tools.jsonl"
failed_save_path="$PROJECT/generated_data/executable_tools/failed/failed_generate_executable_python_tools.jsonl"
tool_defines_path="['$PROJECT/tools/defines/python_functions']"
# save_path="$PROJECT/generated_data/executable_tools/generated/generate_executable_xlam_tools.jsonl"
# failed_save_path="$PROJECT/generated_data/executable_tools/generated/failed_generate_executable_xlam_tools.jsonl"
# tool_defines_path="['$PROJECT/tools/defines/xlam_rapidapi_tools']"
# save_path="$PROJECT/generated_data/executable_tools/generated/generate_executable_mix_all_tools_qwen.jsonl"
# failed_save_path="$PROJECT/generated_data/executable_tools/failed/failed_generate_executable_mix_all_tools_qwen.jsonl"
# tool_defines_path="['$PROJECT/tools/defines/python_functions','$PROJECT/tools/defines/file_system_functions','$PROJECT/tools/defines/xlam_rapidapi_tools','$PROJECT/tools/defines/database_functions']"
save_path="$PROJECT/generated_data/executable_tools/generated/generate_executable_mix_all_tools4.jsonl"
failed_save_path="$PROJECT/generated_data/executable_tools/failed/failed_generate_executable_mix_all_tools4.jsonl"
tool_defines_path="['$PROJECT/tools/defines/python_functions','$PROJECT/tools/defines/file_system_functions','$PROJECT/tools/defines/xlam_rapidapi_tools','$PROJECT/tools/defines/database_functions']"
# save_path="$PROJECT/generated_data/executable_tools/generated/generate_executable_mix_all_self_tools_hard.jsonl"
# failed_save_path="$PROJECT/generated_data/executable_tools/failed/failed_generate_executable_mix_all_self_tools_hard.jsonl"
# tool_defines_path="['$PROJECT/tools/defines/python_functions','$PROJECT/tools/defines/file_system_functions','$PROJECT/tools/defines/database_functions']"
save_path="$PROJECT/generated_data/executable_tools/generated/generate_executable_mix_all_self_tools_qwq.jsonl"
failed_save_path="$PROJECT/generated_data/executable_tools/failed/failed_generate_executable_mix_all_self_tools_qwq.jsonl"
tool_defines_path="['$PROJECT/tools/defines/python_functions','$PROJECT/tools/defines/file_system_functions','$PROJECT/tools/defines/database_functions']"

save_path="$PROJECT/generated_data/executable_tools/generated/task/generate_executable_file_system_task_database_gpt.jsonl"
failed_save_path="$PROJECT/generated_data/executable_tools/failed/failed_generate_executable_file_system_task_gpt.jsonl"
tool_defines_path="['$PROJECT/tools/defines/file_system_functions','$PROJECT/tools/defines/database_functions']"
tool_defines_path="['$PROJECT/tools/defines/database_functions']"

num_workers=10 #多线程生成
target_generate_data_number=200
checker_max_retries=1 #checker重试次数
assistant_n_response=1 #众投次数

file_system_path="$PROJECT/working_dir/file_system_database"

python $PROJECT/pipeline.py \
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
    --task_turn_weights '{"1":5,"2":3,"3":1,"4":1}' \
    --mode_weights '{"single":0, "parallel":0, "multiple":0, "dependent":0, "no_tool_use":0, "task":1}' \
    --tool_nums_distribution '{"10": 300,"9": 400, "8": 500, "7": 500, "6": 400, "5": 300, "4": 0, "3": 0, "2": 0, "1": 0}' \
    --file_system_path $file_system_path \
    --files_num '{"1":0.2,"2":0.3,"3":0.4,"4":0,"5":0}' \
    --use_persona \
        # --files_num '{"1":0,"2":0,"3":0.3,"4":0.4,"5":0.3}' \
    # --provide_file_system_info 'all' \
    # --dynamic_adjust_mode_and_task_turn_weight \
    # --dynamic_adjust_mode_and_task_turn_weight \
    # --assistant_model_name 'qwen' \
    # --checker_model_name 'qwen' \
    # --user_model_name 'qwen' \
    # --tool_model_name 'qwen' \
    # --task_turn_weights '{"1":5,"2":3,"3":2,"4":1}' \
    # --tool_nums_distribution '{"9": 100, "8": 100, "7": 200, "6": 300, "5": 400, "4": 300, "3": 200, "2": 100, "1": 50}' \
    # --mode_weights '{"single":1, "parallel":1, "multiple":1, "dependent":1, "no_tool_use":1}' \
    # --use_persona \
    # --debug \
    # --dynamic_adjust_mode_and_task_turn_weight \


# --dynamic_adjust_mode_and_task_turn_weight \
# --use_random_system_time \

#--debug打印生成消息（多线程时建议关闭）
# --use_random_system_time随机系统时间（可执行工具不要用！有些工具是实时的）