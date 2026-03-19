[TOC]

# CoStrict Backend Deployment Tool

## Project Overview

CoStrict Backend Deployment Tool is an enterprise-level AI code assistant backend service deployment solution based on Docker Compose. This project provides a complete microservice architecture, including core components such as AI gateway, identity authentication, code analysis, and chat services, supporting both private deployment and cloud service modes.

> To view the deployment architecture, server requirements, model requirements, model download links, etc., please visit [Foreword](./docs/foreword.md)

## Quick Start

### 1. Get Deployment Configuration

**Method 1: Via GitHub Release**

Visit the following address:

```http
https://github.com/zgsm-ai/costrict-deploy-docker/releases/
```

Download the latest release archive `costrict-backend-deploy-vX.X.X.tar.gz`, e.g. `costrict-backend-deploy-v0.0.2.tar.gz`

Copy the archive to the server, then extract it:

```bash
# costrict-server is the deployment directory
mkdir ./costrict-server
# Extract all files into costrict-server; replace costrict-backend-deploy-v0.0.2.tar.gz with the actual version you downloaded
tar -zxf costrict-backend-deploy-v0.0.2.tar.gz -C costrict-server
```

### 2. Prepare Backend Service Images

Note: if you are deploying in an offline environment, continue reading this section. If your server can access the full internet (including docker.io, quay.io, docker.elastic.co, etc.), you can skip this step — all images will be pulled automatically during deployment.

The images required by the CoStrict backend can be found in the `scripts/newest-images.list` file for a complete list. You can also pull these images manually.

We provide a Baidu Netdisk download link:

**Netdisk address**:

```http
https://pan.baidu.com/s/5H0ppvaTja4g2MKZs0Ki1-g
```

Newest Version is: v0.0.3

After downloading all tar packages and copying them to a directory on the server, run:

```bash
# /root/images is the directory containing the tar packages; scripts/load-images.sh is in the deployment directory
bash scripts/load-images.sh -l /root/images
```


### 3. Environment Configuration

Edit the configuration file:

```bash
vim configure.sh
```

**Key Configuration Parameters**:

For a quick start, you only need to configure one parameter — the server's IP address. The CoStrict client will use this IP to access the CoStrict backend services. Be sure to set this parameter before continuing:

```sh
COSTRICT_BACKEND=""
```


### 4. Service Deployment

A single command is all it takes to bring up all CoStrict services:

```sh
bash costrict.sh install
```

When the process completes, output similar to the following will be displayed — take note of it:

```
[INFO]  Admin user access: http://192.168.79.130:39009/
[INFO]  Configure Chat model at: http://192.168.79.130:38001/
[INFO]  Set BaseUrl to: http://192.168.79.130:39080/
```

## Service Configuration

### AI Gateway Configuration (Higress)

After deployment, access the Higress console at the following address to check and adjust the `chat` model configuration:

```
# This URL is the second URL shown in the output above
http://{COSTRICT_BACKEND}:{PORT_HIGRESS_CONTROL}
```

**Default admin credentials** (please change after login):

```
Username: admin
Password: 123
```

Configuration steps:
1. Access the Higress management interface
2. Configure upstream LLM service providers
3. Set routing rules and load balancing strategies
4. Configure rate limiting and security policies

Detailed configuration guide: [Higress Configuration Document](./docs/higress/higress.md)

After configuration, you can start using CoStrict directly — see the **Client Integration** section below.

### Optional: Identity Authentication System Configuration (Casdoor)

If there are no special requirements, skip this step.

Access the Casdoor management interface at the following address:

```
# The first URL shown after installation completes
http://{COSTRICT_BACKEND}:{PORT_CASDOOR}
```

Basic user setup reference: [Casdoor Basic Settings](./docs/casdoor/casdoor-init-setting.md)

## Client Integration

### CoStrict Plugin Configuration

1. Install the CoStrict VSCode extension
2. Open the "Provider" page in the extension settings
3. Select the API provider as "CoStrict"
4. Configure the backend service address:
   ```
   CoStrict Base URL: {COSTRICT_BACKEND_BASEURL}
   ```
5. Click "Login CoStrict" to complete authentication

**Test login credentials**:
```
Username: costrict
Password: 123
```

Detailed installation guide: [CoStrict Download and Installation Documentation](https://costrict.ai/download) (includes `VSCode` and `JetBrains` IDE)

**Service access address**:
```
# The third URL shown after installation completes
Default backend entry: http://{COSTRICT_BACKEND}:{PORT_APISIX_ENTRY}
```

## Others

[More information](./docs/others.md)

## License

This project is open source under the Apache 2.0 license. See the [LICENSE](LICENSE) file for details.

## Support and Contribution

- **Issue Reporting**: [GitHub Issues](https://github.com/zgsm-ai/zgsm-backend-deploy/issues)
- **Feature Requests**: [GitHub Discussions](https://github.com/zgsm-ai/zgsm-backend-deploy/discussions)
- **Contribution Guidelines**: [CONTRIBUTING.md](CONTRIBUTING.md)

---

**CoStrict** - Let AI power your code development journey
