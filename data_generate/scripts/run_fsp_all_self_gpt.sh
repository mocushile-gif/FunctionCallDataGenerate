#!/bin/bash
PROJECT=$(dirname $(dirname "$(realpath "$0")"))
executable_temp_working_dir="/mnt/afs2/qinxinyi/function_call_data_temp"
# 清空目录内容但保留目录本身
sudo rm -rf "${executable_temp_working_dir:?}"/*

# export http_proxy=http://proxy.sensetime.com:3128/
# export https_proxy=http://proxy.sensetime.com:3128/
# export HTTP_PROXY=http://proxy.sensetime.com:3128/
# export HTTPS_PROXY=http://proxy.sensetime.com:3128/
export https_proxy=http://tool_chain_team:c1231c80eb75@10.119.176.202:3128
export http_proxy=http://tool_chain_team:c1231c80eb75@10.119.176.202:3128
export NO_PROXY=localhost,127.0.0.1,101.230.144.204,103.177.28.206,8.130.32.149,101.230.144.223,101.230.144.221,202.122.157.109,10.198.64.149,api.schedule.mtc.sensetime.com

save_path="$PROJECT/generated_data/executable_tools/generated/fsp/generate_fsp_all_self_gpt_1000_0806.jsonl"
fsp_path="/mnt/afs2/qinxinyi/function_call_data/fsp_generate/data/generated_fsps_execute_step5_1000_0806_enhance.json"
failed_save_path="$PROJECT/generated_data/executable_tools/failed/failed_generate_fsp_all_self_gpt.jsonl"
tool_defines_path="['$PROJECT/tools/defines/python_functions','$PROJECT/tools/defines/file_system_functions','$PROJECT/tools/defines/database_functions','$PROJECT/tools/defines/api_functions']"

save_path="$PROJECT/generated_data/executable_tools/generated/fsp/generate_fsp_all_self_gpt_1000_0810_all_self+xlam_enhance.jsonl"
fsp_path="/mnt/afs2/qinxinyi/function_call_data/fsp_generate/data/generated_fsps_execute_step5_1000_0810_all_self+xlam_enhance.json"
failed_save_path="$PROJECT/generated_data/executable_tools/failed/failed_generate_fsp_all_self_gpt.jsonl"
tool_defines_path="['$PROJECT/tools/defines/python_functions','$PROJECT/tools/defines/file_system_functions','$PROJECT/tools/defines/database_functions','$PROJECT/tools/defines/api_functions','$PROJECT/tools/defines/xlam_rapidapi_tools']"
file_system_path="$PROJECT/working_dir/file_system_new"

num_workers=1 #多线程生成
checker_max_retries=1 #checker重试次数
assistant_n_response=1 #众投次数

python $PROJECT/pipeline_fsp.py \
    --executable_temp_working_dir $executable_temp_working_dir \
    --original_data_path $fsp_path \
    --save_path $save_path \
    --failed_save_path $failed_save_path \
    --num_workers $num_workers \
    --checker_max_retries $checker_max_retries \
    --assistant_n_response $assistant_n_response \
    --tool_defines_path $tool_defines_path \
    --assistant_model_name 'gpt' \
    --checker_model_name 'gpt' \
    --user_model_name 'gpt' \
    --tool_model_name 'gpt' \
    --lang 'en' \
    --file_system_path $file_system_path \
    --tool_output_limit 4096 \
    --use_persona \