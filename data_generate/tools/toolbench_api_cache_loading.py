import json
import os
import shutil

path_cache = "./tools/tool_response_cache/"
# 重置文件夹
for path in [path_cache]:
    if os.path.exists(path):
        shutil.rmtree(path)  # 删除文件夹及其内容
    os.mkdir(path)  # 重新创建文件夹

with open('./tools/xlam_rapidapi_tools_metadata.json','r',encoding='utf-8') as f:
    api_metadata=json.load(f)

cnt=0
for api,metadata in api_metadata.items():
    cache_path=f'/mnt/nvme0/qinxinyi/StableToolBench/server/tool_response_cache/{metadata["category"]}/{metadata["tool_name"]}_for_{metadata["category"]}/{api}.json'
    new_cache_path=f'/mnt/nvme0/qinxinyi/StableToolBench/server/tool_response_cache/{metadata["category"]}/{metadata["tool_name"]}_for_{metadata["category"]}/{api}.json'
    all_cache={}
    if os.path.exists(cache_path):
        with open(cache_path,'r',encoding='utf-8') as f:
            all_cache.update(json.load(f))
    if os.path.exists(new_cache_path):
        with open(new_cache_path,'r',encoding='utf-8') as f:
            all_cache.update(json.load(f))
    if len(all_cache)>0:
        with open(f'{path_cache}/{api}.json','w',encoding='utf-8') as f:
            json.dump(all_cache,f,ensure_ascii=False,indent=4)
    else:
        print(api)
        print(metadata)
        cnt+=1
print(cnt)