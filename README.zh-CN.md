# CoStrict 后端部署工具

[English Version](./README.md)

## 项目概述

CoStrict 后端部署工具是基于 Docker Compose 的企业级 AI 代码助手后端服务部署解决方案。该项目提供了完整的微服务架构，包含 AI 网关、身份认证、代码分析、聊天服务等核心组件，支持私有化部署和云端服务两种模式。

> 查看此项目的部署架构，部署的服务器要求、模型要求、模型下载地址等，请访问 [前言](./docs/foreword.zh-CN.md)

## 快速开始

### 1. 获取部署配置

**方式一：通过 Github Release**

访问一下地址：

```http
https://github.com/zgsm-sangfor/costrict-deploy-docker/releases/
```

下载最新的release压缩包 `costrict-backend-deploy-vX.X.X.tar.gz` ,如: `costrict-backend-deploy-v0.0.2.tar.gz
`

将压缩包复制到服务器，然后解压

```bash
# costrict-server 就是部署目录
mkdir ./costrict-server
# 将所有文件解压到 costrict-server,注意，costrict-backend-deploy-v0.0.2.tar.gz 替换为你下载的实际版本的压缩包。
tar -zxf costrict-backend-deploy-v0.0.2.tar.gz -C costrict-server
```

### 2. 准备后端服务镜像

注意，如果你是离线环境部署，继续查看本节，如果你的服务器能正常访问整个互联网(包括docker.io、quay.io、docker.elastic.co等),可以直接跳过这个步骤，部署时会自动拉取所有镜像。

CoStrict后端需要的镜像，可以查看 `scripts/newest-images.list` 文件获取完整列表，你也可以手动拉取这些镜像

我们提供了百度网盘的下载地址：

**网盘地址**：

```http
https://pan.baidu.com/s/5H0ppvaTja4g2MKZs0Ki1-g
```

当前最新版本: v0.0.3

下载后所有的tar包并复制到服务器的某个目录，运行：

```bash
# /root/images 就是tar包所在目录，scripts/load-images.sh 是服务部署目录下的脚本
bash scripts/load-images.sh -l /root/images
```


### 3. 环境配置

编辑配置文件:

```bash
vim configure.sh
```

**关键配置参数**:

为了快速开始，你只需要配置第一个参数为服务器的ip即可，CoStrict客户端将会通过这个ip访问CoStrict后台服务，请务必配置这个参数后继续

```sh
COSTRICT_BACKEND=""
```


### 4. 服务部署

只需要一行命令，就可以拉起所有的costrict服务。

```sh
bash costrict.sh install
```

运行结束后，会提示类似的内容,可以记录下来：

```
[INFO]  管理用户访问 http://192.168.79.130:39009/
[INFO]  配置Chat模型请访问 http://192.168.79.130:38001/
[INFO]  BaseUrl请设置 http://192.168.79.130:39080/
```

## 服务配置

### AI 网关配置 (Higress)

你可以参考下面的教程在页面上配置模型，我们也提供了快速模型配置脚本，简化你的配置过程，见[模型配置自动化脚本](./scripts/model-config/auto-model-config.zh-CN.md)

部署完成后，通过以下地址访问 Higress 控制台，对 `对话` 模型配置检查并调整.

```
# 此url就是提示的第二个url
http://{COSTRICT_BACKEND}:{PORT_HIGRESS_CONTROL}
```

**管理账户默认用户名密码** (登录后请及时修改):

```
用户名: admin
密码: 123
```

配置步骤:
1. 访问 Higress 管理界面
2. 配置上游 LLM 服务提供商
3. 设置路由规则和负载均衡策略
4. 配置限流和安全策略

详细配置指南: [Higress 配置文档](./docs/higress/higress.zh-CN.md)

配置结束后，就可以直接使用CoStrict,请见后续章节 **客户端集成**

### 可选：身份认证系统配置 (Casdoor)

如果没有特殊要求，请直接跳过此步骤

通过以下地址访问 Casdoor 管理界面:

```
# 安装结束后提示的第一个url
http://{COSTRICT_BACKEND}:{PORT_CASDOOR}
```

基本用户添加参考: [casdoor基本设置](./docs/casdoor/casdoor-init-setting.zh-CN.md)

## 客户端集成

### CoStrict 插件配置

1. 安装 CoStrict VSCode 扩展
2. 打开扩展设置中的"提供商"页面
3. 选择 API 提供商为"CoStrict"
4. 配置后端服务地址:
   ```
   CoStrict Base URL: {COSTRICT_BACKEND_BASEURL}
   ```
5. 点击"登录 CoStrict"完成身份验证

**登录测试账户**:
```
用户名: costrict
密码: 123
```

详细安装指南：[CoStrict 下载安装文档](https://costrict.ai/download) (含 `VSCode` 和 `JetBrains` IDE)

**服务访问地址**:
```
# 安装后提示的第三个url
默认后端入口: http://{COSTRICT_BACKEND}:{PORT_APISIX_ENTRY}
```

## Others

[更多信息](./docs/others.zh-CN.md)

## 许可证

本项目基于 Apache 2.0 许可证开源。详见 [LICENSE](LICENSE) 文件。

## 支持与贡献

- **问题报告**: [GitHub Issues](https://github.com/zgsm-ai/zgsm-backend-deploy/issues)
- **功能请求**: [GitHub Discussions](https://github.com/zgsm-ai/zgsm-backend-deploy/discussions)
- **贡献指南**: [CONTRIBUTING.md](CONTRIBUTING.md)

---

**CoStrict** - 让 AI 助力您的代码开发之旅
