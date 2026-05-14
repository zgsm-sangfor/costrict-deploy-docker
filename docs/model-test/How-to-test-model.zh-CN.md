# 如何测试模型

如果遇到模型无法访问，访问报错等问题，可以按照以下方案进行测试：

## 首先测试模型是否正常

使用命令测试你准备的模型API是否正常(注意，本测试测试的是模型服务，和CoStrict无关，请使用正确的模型地址)

将以下命令的 `http://ip:port/v1/chat/completions` 替换为真实的模型地址，将`Bearer ***`替换为真实的认证头,将`GLM-4.5-FP8`替换为真实模型名，运行测试，看模型是否正常输出，确保模型能正常运行。

```bash
curl -X POST "http://ip:port/v1/chat/completions" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer ***" \
--data-binary '{
  "model": "GLM-4.5-FP8",
  "messages": [
    {"role": "user", "content": "Hello, how are you?"}
  ],
  "max_tokens": 50,
  "temperature": 0.7
}'
```

## 客户端测试

本测试仅测试模型列表，是测试CoStrict 服务接口，和CoStrict服务相关，需要将CoStrict服务部署起来并配置模型后测试。

浏览器访问 `${BASE_URL}/ai-gateway/api/v1/models`,请将${BASE_URL}替换为CoStrict的服务地址(输出中的BaseUrl),查看模型列表是否正常。


## 服务测试

用于测试costrict服务是否能访问模型服务。

到部署目录下，运行以下命令

```bash
# 进入model-proxy 容器
docker compose exec -it model-proxy sh

# 使用wget命令,请将 Kimi-K2-Moonshot 替换为模型的id,也就是nacos中配置的id.
wget http://127.0.0.1:8080/model-test/Kimi-K2-Moonshot?stream=false -O test.txt
cat test.txt
```