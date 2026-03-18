
## Others

### 域名绑定与负载均衡

对于生产环境，建议通过反向代理或负载均衡器访问服务:

```bash
# Nginx 配置示例
upstream costrict_backend {
    server {COSTRICT_BACKEND}:{PORT_APISIX_ENTRY};
}

server {
    listen 443 ssl;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://costrict_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 故障排除

### 常见问题

**1. 容器启动失败**
```bash
# 检查端口占用
netstat -tlnp | grep {port}

# 检查磁盘空间
df -h

# 查看详细错误日志
docker-compose logs [service_name]
```

**2. 网络连接问题**
```bash
# 测试服务连通性
curl -v http://{COSTRICT_BACKEND}:{PORT_APISIX_ENTRY}/health

# 检查 Docker 网络
docker network ls
docker network inspect {network_name}
```

**3. 数据库连接问题**
```bash
# 检查数据库服务状态
docker-compose exec postgres pg_isready

# 查看数据库日志
docker-compose logs postgres
```

部署常见问题解决: [部署常见问题文档](./docs/deploy-faq.zh-CN.md)

### 日志收集

系统日志位置:
- 应用日志: `./logs/`
- 数据库日志: 容器内 `/var/log/postgresql/`
- 网关日志: 容器内 `/var/log/apisix/`

## 运维管理

### 服务状态监控

检查服务运行状态:

```bash
# 查看所有服务状态
docker-compose ps

# 查看服务日志
docker-compose logs -f [service_name]

# 查看资源使用情况
docker stats
```

### 数据备份与恢复

```
config # 所有配置文件。
data # 所有运行数据。
```

## 安全注意事项

1. **生产环境部署**:
   - 修改所有默认密码
   - 配置 HTTPS 证书
   - 启用防火墙和访问控制
   - 定期更新系统和依赖包

2. **网络安全**:
   - 仅开放必要端口
   - 配置 VPN 或内网访问
   - 启用 API 限流和防护

3. **数据保护**:
   - 定期备份重要数据
   - 启用数据库加密
   - 配置访问审计日志
