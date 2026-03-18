
## Others

### Domain Binding and Load Balancing

For production environments, it is recommended to access services through a reverse proxy or load balancer:

```bash
# Nginx configuration example
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

## Troubleshooting

### Common Issues

**1. Container Startup Failure**
```bash
# Check port usage
netstat -tlnp | grep {port}

# Check disk space
df -h

# View detailed error logs
docker-compose logs [service_name]
```

**2. Network Connectivity Issues**
```bash
# Test service connectivity
curl -v http://{COSTRICT_BACKEND}:{PORT_APISIX_ENTRY}/health

# Check Docker networks
docker network ls
docker network inspect {network_name}
```

**3. Database Connection Issues**
```bash
# Check database service status
docker-compose exec postgres pg_isready

# View database logs
docker-compose logs postgres
```

Common deployment issue resolutions: [Deployment FAQ](./docs/deploy-faq.md)

### Log Collection

System log locations:
- Application logs: `./logs/`
- Database logs: `/var/log/postgresql/` (inside container)
- Gateway logs: `/var/log/apisix/` (inside container)

## Operations Management

### Service Status Monitoring

Check service running status:

```bash
# View status of all services
docker-compose ps

# View service logs
docker-compose logs -f [service_name]

# View resource usage
docker stats
```

### Data Backup and Recovery

```
config # All configuration files.
data   # All runtime data.
```

## Security Considerations

1. **Production Deployment**:
   - Change all default passwords
   - Configure HTTPS certificates
   - Enable firewall and access controls
   - Regularly update the system and dependency packages

2. **Network Security**:
   - Open only necessary ports
   - Configure VPN or intranet access
   - Enable API rate limiting and protection

3. **Data Protection**:
   - Regularly back up important data
   - Enable database encryption
   - Configure access audit logging
