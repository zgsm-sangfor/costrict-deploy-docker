## 关于CoStrict
### 核心特性

- **微服务架构**: 基于容器化的分布式服务架构
- **AI 网关集成**: 支持多种大语言模型接入
- **身份认证系统**: 集成 Casdoor 提供企业级身份管理
- **代码智能分析**: 提供代码审查、补全、优化等功能
- **可扩展设计**: 支持横向扩展和自定义插件

### 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   VSCode 插件    │────│   API Gateway   │────│   后端服务群     │
│   (CoStrict)    │    │  (Apache APISIX) │    │  (Microservices) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                        │
                       ┌─────────────────┐    ┌─────────────────┐
                       │   AI 网关       │    │   数据库集群     │
                       │   (Higress)     │    │   (PostgreSQL)  │
                       └─────────────────┘    └─────────────────┘
```

## 系统要求

### 模型要求

CoStrict的核心功能都依赖大语言模型，总共需要 **准备如下模型服务并确保模型接口功能正常**

```
1. 对话模型(提供完整的 http://chat_model_ip:chat_model_port/v1/chat/completions 接口)
2. embedding模型(提供完整的 http://embedding_model_ip:embedding_model_port/v1/embeddings 接口)
3. rerank 模型(提供完整的 http://rerank_model_ip:rerank_model_port/v1/rerank 接口)
4. 补全模型(提供完整的 http://completion_model_ip:completion_model_port/v1/completions 接口)
```

**注意**：提供并记录准确的 `模型名称`、`APIKEY` 和 `上下文长度` 信息。用于部署服务时配置。

**推荐模型** 和 **下载地址**：

- **对话模型**： `GLM-4.6-FP8` 及以上，如 `GLM-4.7` `GLM-5`

- **embedding模型**：`gte-modernbert-baseRAG/Embedding`

- **rerank模型**：`gte-reranker-modernbert-baseRAG/Rerank`

- **下载地址**：

```
https://modelscope.cn/models/ZhipuAI/GLM-4.7-FP8
https://modelscope.cn/models/iic/gte-modernbert-base
https://modelscope.cn/models/iic/gte-reranker-modernbert-base
```

**推荐模型部署资源**：

- **对话模型**：`4 * H20` (GLM-4.7-FP8的推荐值,GLM-4.5-FP8则翻倍)

- **embedding模型**：`0.5 * H20` 或 `0.5 * RTX4090`

- **rerank模型**：`0.5 * H20` 或 `0.5 * RTX4090`

**试用提醒**：

- 若有资源，为了体验完整的功能，请确保 **所有模型部署时满足上述要求**。
- 若无资源，我们可以提供两种方式：
  - 直接使用我们正式发布的CoStrict，无需额外部署，体验CoStrict所有功能。
  - 由我们提供 **限时** 的线上`对话`模型接口，用于短期体验CoStrict主要的`AGNET`和`CODE REVIEW`功能。

| 功能 | 自部署（模型符合要求） | 正式发布CoStrict | 使用限时接口 |
|------|------------|--------------|--------------|
| AGENT（Vibe） | ✅ 完整功能 | ✅ 完整功能 | ✅ 限时体验（缺少Codebase） |
| AGENT（Strict） | ✅ 完整功能 | ✅ 完整功能 | ✅ 限时体验（缺少Codebase） |
| CODE REVIEW | ✅ 完整功能 | ✅ 完整功能 | ✅ 限时体验 |
| 代码补全 | ✅ 完整功能 | ✅ 完整功能 | ❌ 不支持 |
| CoStrict线上接口访问 | ✅ 无需访问CoStrict线上接口 | ❌ 要求访问CoStrict线上接口 | ❌ 要求访问CoStrict线上接口 |


### 自部署后端服务实例环境

**硬件要求**:
- CPU: Intel x64 架构，最低 16 核心 (Arm架构部署，请联系CoStrict团队)
- 内存: 最低 32GB RAM
- 存储: 最低 512GB 可用存储空间 (注意是运行需要的空间，包括了docker运行环境，服务运行产生的数据)

**软件要求**:
- 操作系统: CentOS 7+ 或 Ubuntu 20.04+ (支持 WSL)
- Container Runtime: Docker 20.10+ (可参考[离线安装docker](./how-to-install-docker-offline.zh-CN.md)离线安装)
- 编排工具: Docker Compose 2.0+
