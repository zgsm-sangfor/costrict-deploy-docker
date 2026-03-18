#!/bin/sh

# 检查镜像列表是否存在
if [ ! -f "scripts/newest-images.list" ]; then
    echo "镜像列表文件‘scripts/newest-images.list’不存在，生成新的镜像列表..."
    bash scripts/get-images-list.sh -o scripts
else
    echo "使用现有的镜像列表文件‘scripts/newest-images.list’"
fi

# if [ ! -f "scripts/images.list" ]; then
#     echo "镜像列表文件‘scripts/images.list’不存在，生成新的镜像列表..."
#     awk -F'=' '{print $2}' "scripts/newest-images.list" > "scripts/images.list"
# else
#     echo "使用现有的镜像列表文件‘scripts/images.list’"
# fi

awk -F'=' '{print $2}' "scripts/newest-images.list" > "scripts/images.list"

# 验证镜像是否存在
echo "验证镜像..."
bash scripts/verify-images.sh -f scripts/images.list
status=$?

# 根据验证结果决定是否拉取镜像
if [ $status -eq 0 ]; then
    echo "所有镜像已存在，跳过拉取"
    exit 0
else
    read -r -p "部分镜像不存在，是否立即拉取镜像？[y/N] " answer
    case "$answer" in
        [yY][eE][sS]|[yY])
            echo "开始拉取镜像..."
            bash scripts/pull-images.sh -f scripts/images.list
            if [ $? -eq 0 ]; then
                echo "镜像拉取成功"
                bash scripts/verify-images.sh -f scripts/images.list
            else
                echo "镜像拉取失败"
                exit 1
            fi
            ;;
        *)
            echo "用户已取消拉取镜像"
            exit 1
            ;;
    esac
fi
