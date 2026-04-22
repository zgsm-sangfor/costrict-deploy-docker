#!/bin/bash

base_dir="${1:-.}"

dirs=(
    "data/etcd"
    "data/redis"
    "data/postgres"
    "data/weaviate"
    "data/chat-rag/logs"
    "data/oidc-auth/logs"
    "data/es"
    # "data/higress" # higress 有特殊的创建方法
)

for dir in "${dirs[@]}"; do
    full_path="${base_dir}/${dir}"
    if [ -d "${full_path}" ]; then
        echo "[SKIP] Dir already exists: ${full_path}"
    else
        mkdir -p "${full_path}"
        echo "[CREATE] Dir created: ${full_path}"
    fi
done

echo "Now need root privileges to chown the directories"

sudo chown -R  1001  "${base_dir}/data/etcd/"

# portal 资源准备

if [ ! -d "${base_dir}/data/portal" ]; then
    mkdir -p "${base_dir}/data/portal"
    sudo cp -r -a "${base_dir}/config/portal/static_file/costrict"  "${base_dir}/data/portal/"
    sudo cp -r -a "${base_dir}/config/portal/static_file/costrict-static"  "${base_dir}/data/portal/"
    sudo cp -r -a "${base_dir}/config/portal/static_file/wasm"  "${base_dir}/data/portal/"
    sudo chmod -R +r "${base_dir}/data/portal"
fi