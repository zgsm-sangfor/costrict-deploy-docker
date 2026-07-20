# 物料清单

请到： https://pan.baidu.com/s/14vFqsjFlWUQD28vhHnp7yg?pwd=6ru5 下载安装物料

每次下载，都只需要下载一个指定版本的数据，比如v0.0.1,其他版本则不要管，其中，images 里面存在多个文件夹，只需要下载一个即可，如果你能直连docker hub和github,可以不用下载images和images_tar。

```
.
├── v0.0.1/  # 版本目录,也就是某个版本所需的所有文件
│   ├── images/ # docker 镜像,分为多种平台版本,一般是amd64或者arm64,根据需求下载一种即可
│   │   ├── amd64/ # 比如这是常用的intel芯片的amd平台的包
│   │   │   ├── base-image.tar # 以下示例,不是真实存在的
│   │   │   └── db-client.tar
│   │   ├── arm64/
│   │   │   ├── base-image.tar
│   │   │   └── db-client.tar
│   │   └── ppc64le/
│   │       └── monitoring-tool.tar
│   ├── images_tar/ # 和images一样，只是同一个平台压缩为一个压缩包,可以不存在
│   ├── static_file/ # 静态文件目录,每个版本村的静态文件可能不一样
│   │   ├── configs/ # 以下示例,不是真实存在的
│   │   │   ├── application.yml
│   │   │   └── logback.xml
│   │   └── certs/
│   │       ├── server.crt
│   │       └── server.key
│   ├── scripts # 辅助脚本目录
│   ├── costrict-mirror.tar.xz  # 离线安装包
│   └── install.sh # 安装脚本
│
└── v0.0.2/
```

下载数据后，将其拷贝到您的服务器上

# 安装

## 安装主要系统

注意，安装时，应当在install.sh所在的目录，比如v0.0.1目录，这个目录是整个安装过程的目录

注意，--backend /opt/costrict --data /data/costrict 参数指的是后端程序目录和数据目录，请根据实际情况指定。

```bash
bash install.sh --backend /opt/costrict --data /data/costrict
```



自动配置脚本内容如下,留在这里方便技术支持时复制一些命令，<font color='red'>请不要管!!!!也不需要运行</font>

```bash
#!/bin/bash

# 当前目录
CURRENT_DIR=$(pwd)
# 获取命令行参数
BACKEND_DIR=""
DATA_DIR=""

if [ "$EUID" -ne 0 ]; then
    echo "错误：此脚本需要 root 权限才能运行"
    echo "请使用: sudo $0"
    exit 1
fi

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --backend)
            BACKEND_DIR="$2"
            shift 2
            ;;
        --data)
            DATA_DIR="$2"
            shift 2
            ;;
        *)
            echo "未知参数: $1"
            echo "用法: $0 --backend <路径> --data <路径>"
            exit 1
            ;;
    esac
done

# 检查必需参数
if [ -z "$BACKEND_DIR" ] || [ -z "$DATA_DIR" ]; then
    echo "错误：缺少必需参数！"
    echo "用法: $0 --backend <路径> --data <路径>"
    exit 1
fi

# 显示获取到的变量（您可以在后续使用这两个变量）
echo "BACKEND_DIR: $BACKEND_DIR"
echo "DATA_DIR: $DATA_DIR"

# 定义目标目录
TARGET_MIRRORS_DIR="./costrict-mirror"

# 创建目标目录（如果不存在）
mkdir -p "$TARGET_MIRRORS_DIR"

# 检查当前目录下的压缩包并解压
if [ -f "costrict-mirror.tar.xz" ]; then
    echo "检测到 costrict-mirror.tar.xz，开始解压..."
    tar -xJvf costrict-mirror.tar.xz -C "$TARGET_MIRRORS_DIR"
elif [ -f "costrict-mirror.tar.gz" ]; then
    echo "检测到 costrict-mirror.tar.gz，开始解压..."
    tar -zxvf costrict-mirror.tar.gz -C "$TARGET_MIRRORS_DIR"
elif [ -f "costrict-mirror.zip" ]; then
    echo "检测到 costrict-mirror.zip，开始解压..."
    unzip -o costrict-mirror.zip -d "$TARGET_MIRRORS_DIR"
else
    echo "错误：未找到任何 costrict-mirror 压缩包！"
    echo "支持的格式：.tar.xz, .tar.gz, .zip"
    exit 1
fi

echo "解压完成！文件已解压到 $TARGET_MIRRORS_DIR"
# 进入mirror目录
cd costrict-mirror/
tar -zxf costrict-mirror.tar.gz
# 安装镜像站点
bash costrict-static/install-costrict-admin.sh
bash costrict-static/install-mirror.sh
cd "$CURRENT_DIR"
# 加载镜像
bash scripts/docker-images-auto-load.sh

# 执行安装, --backend 是程序目录， --data是数据目录
costrict-admin install --mirror http://localhost --backend $BACKEND_DIR --data $DATA_DIR

```

## 其他手动配置

等待所有服务启动后运行：

### cs-cloud

运行:

```bash
# 参数含义和安装脚本一致
bash scripts/cs-cloud-client-register.sh --backend /opt/costrict --data /data/costrict
```

自动配置脚本内容如下,留在这里方便技术支持时复制一些命令，<font color='red'>请不要管!!!!也不需要运行</font>

```bash
# cs-cloud 文件
while [[ $# -gt 0 ]]; do
    case $1 in
        --backend)
            BACKEND="$2"
            shift 2
            ;;
        --data)
            DATA="$2"
            shift 2
            ;;
        *)
            # 跳过未知参数
            shift
            ;;
    esac
done
cho "Backend: $BACKEND"
echo "Data: $DATA"
# 放置文件到cs-cloud目录
mkdir -p $BACKEND/portal/data/costrict-static/
cp -r static_file/cs-cloud $BACKEND/portal/data/costrict-static/
# 注册
## 加载环境变量 
source $BACKEND/.env
cs_cloud_version=$(basename $(ls -d static_file/cs-cloud/v* 2>/dev/null | head -1))
echo "cs-cloud-version:${cs_cloud_version}"
sudo chmod 755 scripts/publish-cs-cloud.sh
bash scripts/publish-cs-cloud.sh ${cs_cloud_version} "${PASSWORD_COSTRICT_WEB_SYSTEM_TOKEN}" --base-url ${COSTRICT_BASEURL}

```



### csc-cloud 知识库

运行

```bash
# 参数含义和安装脚本一致，运行时间较久。
bash  scripts/cs-cloud-coding-plugin-register.sh  --backend /opt/costrict --data /data/costrict
```



自动配置脚本内容如下,留在这里方便技术支持时复制一些命令，<font color='red'>请不要管!!!!也不需要运行</font>

```bash
# cs-cloud 文件
while [[ $# -gt 0 ]]; do
    case $1 in
        --backend)
            BACKEND="$2"
            shift 2
            ;;
        --data)
            DATA="$2"
            shift 2
            ;;
        *)
            # 跳过未知参数
            shift
            ;;
    esac
done
echo "Backend: $BACKEND"
echo "Data: $DATA"
now_dir="$PWD"
cd $BACKEND
docker compose cp $now_dir/static_file/catalog-bundle.tar.gz costrict-web-api:/tmp/catalog-bundle.tar.gz
# 这条命令运行较长时间，请等待
docker compose exec -it costrict-web-api /app/migrate ingest-upstream --source=/tmp/catalog-bundle.tar.gz
```



# 模型配置

登录nacos，一般是 http://ip:38080
```
用户名: nacos
密码：nacos
```

1. 打开 配置管理-> 配置列表-> costrict(在`配置管理`这四个大字的下方)。
2. 找到 `model-config` 配置，点击编辑,根据提示编辑`配置内容`,其他不要动。
3. 编辑后发布即可，会自动实时更新。

以下是配置说明/示例，注意：

**请严格按照yaml或者json格式配置**

**请严格按照yaml或者json格式配置**

**请严格按照yaml或者json格式配置**

发布时nacos会有格式检查,如果报错: `配置信息可能有语法错误, 确定提交吗?`请不要提交。

配置前，请确定模型的支持情况：
- 模型支持openai的 /v1/chat/completions接口格式的调用,路径(路由)不一样没关系；
- 模型至少支持16000(最小测试上下文,仅测试模型是否正常)；
- 模型支持function call工具调用,也就是请求体中支持 `tools`字段,和`"tool_choice": "auto"`；

```yaml
# 配置示例和解释，请在nacos中修改，不用复制这个配置。
models:
    # 配置示例 1 
    # id,模型的名称, 你在插件中看到的名字,也就是你在模型列表中看到的名字，随便自定义
  - id: Kimi-K2-Moonshot
    # 模型的信息
    publicInfo:
      # 最大输出, 比contextWindow小 (一般32K够用了),请用阿拉伯数字.
      maxTokens: 32000
      # 上下文窗口,找模型提供者给,如果模型提供者给你的值小于16000,请换更大的模型，请用阿拉伯数字.
      # 警告,这个数字不是想调大就调大的，请必须填写模型真实支持的上下文长度.
      contextWindow: 200000
    # 模型的key相关
    privateConfig:
      # 模型的真实名字,找模型提供者给
      convertedName: KimiK1000000
      # 地址,完整的路径/v1/chat/completions
      addr: http://127.0.0.1:6666/v1/chat/completions
      # 自定义头,可以添加任意多个
      extraHeaders:
        # 认证头一般放这里,请询问模型提供者值是多少,请注意，请填写请求模型的实际认证头，不要简写，略写。
        Authorization: "sk-xxxxxxxx"
      # 是否跳过ssl校验,一般只有服务是https且采用自签名的ssl证书才需要设置，请询问模型提供者。
      skipSSLVerify: false
    # 配置示例 2,和1一样，只是有更多的补充说明。
    # 模型2，需要多少个模型就加多少个,请严格按照yaml格式配置
  - id: Qwen3.5
    # 模型的一些配置项,详细
    publicInfo:
      object: model
      maxTokens: 32000
      contextWindow: 200000
      # 是否支持图片
      supportsImages: true
      supportsComputerUse: false
      supportsPromptCache: false
      supportsReasoningBudget: false
      requiredReasoningBudget: false
      # 描述信息
      description: Qwen3.5 to glm
      # 配额，当前这个功能没有。
      creditConsumption: 3
      creditDiscount: 1
    privateConfig:
      convertedName: glm-5-tokens
      addr: http://127.0.0.1:32323/v1/chat/completions
      extraHeaders:
        Authorization: sk-***
      skipSSLVerify: false
```
