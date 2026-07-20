# Bill of Materials

Please go to: https://pan.baidu.com/s/14vFqsjFlWUQD28vhHnp7yg?pwd=6ru5 to download installation materials

Each time you download, only download one specific version of data, e.g., v0.0.1, ignore other versions. Among them, there are multiple folders inside `images`, just download one. If you have direct access to Docker Hub and GitHub, you can skip downloading `images` and `images_tar`.

```
.
├── v0.0.1/  # Version directory, i.e., all files required for a specific version
│   ├── images/ # Docker images, available in multiple platform versions, typically amd64 or arm64, download one as needed
│   │   ├── amd64/ # e.g., the commonly used Intel chip AMD platform package
│   │   │   ├── base-image.tar # Examples below, not real files
│   │   │   └── db-client.tar
│   │   ├── arm64/
│   │   │   ├── base-image.tar
│   │   │   └── db-client.tar
│   │   └── ppc64le/
│   │       └── monitoring-tool.tar
│   ├── images_tar/ # Same as images, but compressed into a single archive per platform, may not exist
│   ├── static_file/ # Static files directory, static files may differ per version
│   │   ├── configs/ # Examples below, not real files
│   │   │   ├── application.yml
│   │   │   └── logback.xml
│   │   └── certs/
│   │       ├── server.crt
│   │       └── server.key
│   ├── scripts # Helper scripts directory
│   ├── costrict-mirror.tar.xz  # Offline installation package
│   └── install.sh # Installation script
│
└── v0.0.2/
```

After downloading, copy the data to your server.

# Installation

## Install the Main System

Note: When installing, you should be in the same directory as `install.sh`, e.g., the v0.0.1 directory, which is the root directory for the entire installation process.

Note: The `--backend /opt/costrict --data /data/costrict` parameters refer to the backend program directory and data directory. Please adjust them according to your actual situation.

```bash
bash install.sh --backend /opt/costrict --data /data/costrict
```



The auto-configuration script content is listed below for technical support to copy commands when needed. <font color='red'>Please ignore it!!!! Do not run it</font>

```bash
#!/bin/bash

# Current directory
CURRENT_DIR=$(pwd)
# Get command line arguments
BACKEND_DIR=""
DATA_DIR=""

if [ "$EUID" -ne 0 ]; then
    echo "Error: This script requires root privileges to run"
    echo "Please use: sudo $0"
    exit 1
fi

# Parse command line arguments
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
            echo "Unknown parameter: $1"
            echo "Usage: $0 --backend <path> --data <path>"
            exit 1
            ;;
    esac
done

# Check required parameters
if [ -z "$BACKEND_DIR" ] || [ -z "$DATA_DIR" ]; then
    echo "Error: Missing required parameters!"
    echo "Usage: $0 --backend <path> --data <path>"
    exit 1
fi

# Display obtained variables (you can use these two variables later)
echo "BACKEND_DIR: $BACKEND_DIR"
echo "DATA_DIR: $DATA_DIR"

# Define target directory
TARGET_MIRRORS_DIR="./costrict-mirror"

# Create target directory (if it doesn't exist)
mkdir -p "$TARGET_MIRRORS_DIR"

# Check and extract the archive in the current directory
if [ -f "costrict-mirror.tar.xz" ]; then
    echo "Detected costrict-mirror.tar.xz, starting extraction..."
    tar -xJvf costrict-mirror.tar.xz -C "$TARGET_MIRRORS_DIR"
elif [ -f "costrict-mirror.tar.gz" ]; then
    echo "Detected costrict-mirror.tar.gz, starting extraction..."
    tar -zxvf costrict-mirror.tar.gz -C "$TARGET_MIRRORS_DIR"
elif [ -f "costrict-mirror.zip" ]; then
    echo "Detected costrict-mirror.zip, starting extraction..."
    unzip -o costrict-mirror.zip -d "$TARGET_MIRRORS_DIR"
else
    echo "Error: No costrict-mirror archive found!"
    echo "Supported formats: .tar.xz, .tar.gz, .zip"
    exit 1
fi

echo "Extraction complete! Files extracted to $TARGET_MIRRORS_DIR"
# Enter the mirror directory
cd costrict-mirror/
tar -zxf costrict-mirror.tar.gz
# Install mirror site
bash costrict-static/install-costrict-admin.sh
bash costrict-static/install-mirror.sh
cd "$CURRENT_DIR"
# Load images
bash scripts/docker-images-auto-load.sh

# Execute installation, --backend is the program directory, --data is the data directory
costrict-admin install --mirror http://localhost --backend $BACKEND_DIR --data $DATA_DIR

```

## Other Manual Configuration

Run after all services have started:

### cs-cloud

Run:

```bash
# The parameter meanings are the same as the installation script
bash scripts/cs-cloud-client-register.sh --backend /opt/costrict --data /data/costrict
```

The auto-configuration script content is listed below for technical support to copy commands when needed. <font color='red'>Please ignore it!!!! Do not run it</font>

```bash
# cs-cloud file
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
            # Skip unknown parameters
            shift
            ;;
    esac
done
echo "Backend: $BACKEND"
echo "Data: $DATA"
# Place files in the cs-cloud directory
mkdir -p $BACKEND/portal/data/costrict-static/
cp -r static_file/cs-cloud $BACKEND/portal/data/costrict-static/
# Register
## Load environment variables
source $BACKEND/.env
cs_cloud_version=$(basename $(ls -d static_file/cs-cloud/v* 2>/dev/null | head -1))
echo "cs-cloud-version:${cs_cloud_version}"
sudo chmod 755 scripts/publish-cs-cloud.sh
bash scripts/publish-cs-cloud.sh ${cs_cloud_version} "${PASSWORD_COSTRICT_WEB_SYSTEM_TOKEN}" --base-url ${COSTRICT_BASEURL}

```



### csc-cloud Knowledge Base

Run:

```bash
# The parameter meanings are the same as the installation script. This may take a while to run.
bash  scripts/cs-cloud-coding-plugin-register.sh  --backend /opt/costrict --data /data/costrict
```



The auto-configuration script content is listed below for technical support to copy commands when needed. <font color='red'>Please ignore it!!!! Do not run it</font>

```bash
# cs-cloud file
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
            # Skip unknown parameters
            shift
            ;;
    esac
done
echo "Backend: $BACKEND"
echo "Data: $DATA"
now_dir="$PWD"
cd $BACKEND
docker compose cp $now_dir/static_file/catalog-bundle.tar.gz costrict-web-api:/tmp/catalog-bundle.tar.gz
# This command takes a long time to run, please wait
docker compose exec -it costrict-web-api /app/migrate ingest-upstream --source=/tmp/catalog-bundle.tar.gz
```



# Model Configuration

Log in to Nacos, typically at http://ip:38080

```
Username: nacos
Password: nacos
```

1. Go to Configuration Management -> Configuration List -> costrict (below the text "Configuration Management").
2. Find the `model-config` configuration, click Edit, edit the `Configuration Content` as prompted, do not modify anything else.
3. After editing, publish it, and it will update automatically in real-time.

Below are configuration instructions/examples. Note:

**Please strictly follow YAML or JSON format**

**Please strictly follow YAML or JSON format**

**Please strictly follow YAML or JSON format**

Nacos will perform format validation upon publishing. If the error `"The configuration may have syntax errors. Are you sure you want to submit?"` appears, please do not submit.

Before configuring, ensure the model's capabilities:
- The model supports OpenAI's `/v1/chat/completions` interface format; different paths/routes are acceptable.
- The model supports at least 16000 (minimum test context, only for testing if the model works properly).
- The model supports function call (tool calling), i.e., the request body supports the `tools` field and `"tool_choice": "auto"`.

```yaml
# Configuration example and explanation, modify in Nacos, do not copy this configuration.
models:
    # Configuration Example 1
    # id: The model name, the name you see in plugins, i.e., the name visible in the model list, can be customized
  - id: Kimi-K2-Moonshot
    # Model information
    publicInfo:
      # Maximum output tokens, smaller than contextWindow (32K is generally sufficient), use Arabic numerals.
      maxTokens: 32000
      # Context window, obtain from the model provider. If the value provided is less than 16000, switch to a larger model. Use Arabic numerals.
      # Warning: This number cannot be arbitrarily increased; it must reflect the model's actual supported context length.
      contextWindow: 200000
    # Model key configuration
    privateConfig:
      # The actual model name, obtain from the model provider
      convertedName: KimiK1000000
      # URL, full path to /v1/chat/completions
      addr: http://127.0.0.1:6666/v1/chat/completions
      # Custom headers, can add any number
      extraHeaders:
        # Authentication header is usually placed here. Ask the model provider for the value. Please fill in the actual authentication header for the model request, do not abbreviate.
        Authorization: "sk-xxxxxxxx"
      # Whether to skip SSL verification. Only needed if the service uses HTTPS with a self-signed SSL certificate. Ask the model provider.
      skipSSLVerify: false
    # Configuration Example 2, same as 1, but with additional explanations.
    # Model 2, add as many models as needed. Please strictly follow YAML format.
  - id: Qwen3.5
    # Detailed model configuration options
    publicInfo:
      object: model
      maxTokens: 32000
      contextWindow: 200000
      # Whether images are supported
      supportsImages: true
      supportsComputerUse: false
      supportsPromptCache: false
      supportsReasoningBudget: false
      requiredReasoningBudget: false
      # Description
      description: Qwen3.5 to glm
      # Quota, currently not functional
      creditConsumption: 3
      creditDiscount: 1
    privateConfig:
      convertedName: glm-5-tokens
      addr: http://127.0.0.1:32323/v1/chat/completions
      extraHeaders:
        Authorization: sk-***
      skipSSLVerify: false
```
