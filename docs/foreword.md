
### Core Features

- **Microservices Architecture**: Containerized distributed service architecture
- **AI Gateway Integration**: Supports multiple large language model integrations
- **Identity Authentication System**: Integrates Casdoor for enterprise-grade identity management
- **Intelligent Code Analysis**: Provides code review, completion, optimization, and more
- **Scalable Design**: Supports horizontal scaling and custom plugins

### System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   VSCode Plugin  │────│   API Gateway   │────│  Backend Services│
│   (CoStrict)    │    │  (Apache APISIX) │    │  (Microservices) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                               │                        │
                        ┌─────────────────┐    ┌─────────────────┐
                        │   AI Gateway    │    │  Database Cluster│
                        │   (Higress)     │    │   (PostgreSQL)  │
                        └─────────────────┘    └─────────────────┘
```

## System Requirements

### Model Requirements

All core features of CoStrict rely on large language models. You need to **prepare the following model services and ensure the model API interfaces are functioning properly**:

```
1. Chat model     (provide a complete http://chat_model_ip:chat_model_port/v1/chat/completions interface)
2. Embedding model (provide a complete http://embedding_model_ip:embedding_model_port/v1/embeddings interface)
3. Rerank model   (provide a complete http://rerank_model_ip:rerank_model_port/v1/rerank interface)
4. Completion model (provide a complete http://completion_model_ip:completion_model_port/v1/completions interface)
```

**Note**: Provide and record accurate `model name`, `API KEY`, and `context length` information for use during service deployment configuration.

**Recommended Models** and **Download Links**:

- **Chat model**: `GLM-4.6-FP8` or above, e.g. `GLM-4.7`, `GLM-5`

- **Embedding model**: `gte-modernbert-baseRAG/Embedding`

- **Rerank model**: `gte-reranker-modernbert-baseRAG/Rerank`

- **Download links**:

```
https://modelscope.cn/models/ZhipuAI/GLM-4.7-FP8
https://modelscope.cn/models/iic/gte-modernbert-base
https://modelscope.cn/models/iic/gte-reranker-modernbert-base
```

**Recommended Model Deployment Resources**:

- **Chat model**: `4 * H20` (recommended for GLM-4.7-FP8; double for GLM-4.5-FP8)

- **Embedding model**: `0.5 * H20` or `0.5 * RTX4090`

- **Rerank model**: `0.5 * H20` or `0.5 * RTX4090`

**Trial Reminder**:

- If you have resources available, to experience the full feature set, please ensure **all models meet the above requirements when deployed**.
- If you do not have resources, we offer two alternatives:
  - Use our officially released CoStrict directly without any additional deployment to experience all CoStrict features.
  - We can provide a **time-limited** online `chat` model API for short-term experience of CoStrict's primary `AGENT` and `CODE REVIEW` features.

| Feature | Self-deployed (models meeting requirements) | Official CoStrict Release | Using Time-limited API |
|---------|---------------------------------------------|---------------------------|------------------------|
| AGENT (Vibe) | ✅ Full features | ✅ Full features | ✅ Time-limited experience (no Codebase) |
| AGENT (Strict) | ✅ Full features | ✅ Full features | ✅ Time-limited experience (no Codebase) |
| CODE REVIEW | ✅ Full features | ✅ Full features | ✅ Time-limited experience |
| Code Completion | ✅ Full features | ✅ Full features | ❌ Not supported |
| CoStrict Online API Access | ✅ No CoStrict online API access required | ❌ Requires CoStrict online API access | ❌ Requires CoStrict online API access |


### Self-deployed Backend Service Instance Environment

**Hardware Requirements**:
- CPU: Intel x64 architecture, minimum 16 cores (for Arm architecture deployment, please contact the CoStrict team)
- Memory: Minimum 32GB RAM
- Storage: Minimum 512GB available storage (note: this is runtime space required, including the Docker runtime environment and data generated during service operation)

**Software Requirements**:
- OS: CentOS 7+ or Ubuntu 18.04+ (WSL supported)
- Container Runtime: Docker 20.10+ (refer to [offline Docker installation](./how-to-install-docker-offline.md) for offline setup)
- Orchestration Tool: Docker Compose 2.0+



## Deployment Checklist

Before starting the deployment, please **open and review the [Deployment Checklist](./docs/deploy-checklist.md)** simultaneously; and **check off all checklist items** throughout the entire deployment process to ensure a successful final deployment.
