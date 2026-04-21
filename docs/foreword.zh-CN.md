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

4. 补全模型(提供完整的 http://completion_model_ip:completion_model_port/v1/completions 接口)
```

**注意**：提供并记录准确的 `模型名称`、`APIKEY` 和 `上下文长度` 信息。用于部署服务时配置。

**推荐模型** 和 **下载地址**：

当前CoStrict的只保留了对话模型和补全模型

- **对话模型**：`GLM-5.1` `GLM-5` `MiniMax-M2.7` `GLM-4.7` (当前最推荐GLM-5.1)

- **补全模型**：`Qwen/Qwen3-4B`

- **下载地址**：

```
https://modelscope.cn/models/ZhipuAI/GLM-5.1-FP8
https://modelscope.cn/models/ZhipuAI/GLM-5-FP8
https://modelscope.cn/models/MiniMax/MiniMax-M2.7
https://modelscope.cn/models/ZhipuAI/GLM-4.7-FP8

https://modelscope.cn/models/Qwen/Qwen3-4B
```

**推荐模型部署资源**：

- **对话模型**：`4 * H20` (GLM-4.7-FP8的推荐值,GLM-5则翻倍)
- **补全模型**: `1 * 4090` (Qwen3-4B的推荐值)

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

### 国产化/信创支持

支持的CPU: 鲲鹏920(Arm，可搭配Kylin v11, OpenEuler 24.03, Ubuntu 22.04系统) 

支持的系统：Kylin V11、OpenEuler 24.03

支持的数据库：Kingbase V9R1C10 （pgsql兼容模式）、PolarDb-PG 17

未在此列表的，表示未进行测试，而非不支持