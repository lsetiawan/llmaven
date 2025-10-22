# Container Build and Deployment

## Overview

The LLMaven Proxy is containerized using Docker and automatically built/published to GitHub Container Registry (GHCR).

## Container Details

- **Base Image:** `python:3.11-alpine`
- **Build:** Multi-stage build for optimized size
- **Port:** 8888 (internal)
- **Health Check:** `GET /health` endpoint
- **Registry:** `ghcr.io/uw-ssec/llmaven/proxy`

## Automated Builds

### Triggers

- Push to `main` branch (when `proxy/**` files change)
- Manual workflow dispatch via GitHub Actions UI

### Tags Generated

1. `latest` - Always points to most recent build
2. `YYYYMMDD` - Date-based tag (e.g., `20241022`)
3. `YYYYMMDD-sha-abc123` - Date + git commit SHA

### Platforms

- `linux/amd64`
- `linux/arm64`

## Local Development

### Build locally:

```bash
cd /path/to/llmaven
docker build -t llmaven-proxy:dev -f proxy/Dockerfile .
```

### Run locally:

```bash
docker run -it --rm \
  -p 8888:8888 \
  -e OPENAI_API_KEY=your-key \
  -e OPENAI_BASE_URL=your-service \
  -e STORAGE_TYPE=local \
  -v $(pwd)/logs:/app/logs \
  llmaven-proxy:dev
```

### Test:

```bash
curl http://localhost:8888/health
```

## Production Deployment

### Pull from GHCR:

```bash
docker pull ghcr.io/uw-ssec/llmaven/proxy:latest
```

### Kubernetes Deployment:

See main README.md for full Kubernetes manifests.

### Required Environment Variables:

- `OPENAI_API_KEY` - OpenAI API key (from Kubernetes Secret)
- `STORAGE_TYPE` - `local` or `azure`
- `AZURE_STORAGE_ACCOUNT_NAME` - (if using Azure)
- `AZURE_STORAGE_ACCOUNT_KEY` - (if using Azure, from Secret)

### Optional Environment Variables:

- `OPENAI_BASE_URL` - Default: `https://api.openai.com`
- `PROXY_TIMEOUT` - Default: `300` seconds
- `LOCAL_LOG_DIR` - Default: `logs`
- `AZURE_STORAGE_CONTAINER` - Default: `proxy-logs`

## Image Size

Multi-stage Alpine build keeps image size small:

- Builder stage: ~500MB (includes build tools)
- Final image: ~150-200MB (runtime only)

## Security

### Container runs as root (Alpine limitation)

For enhanced security in production:

1. Use Kubernetes security contexts
2. Run with read-only root filesystem (except `/app/logs`)
3. Drop all capabilities except NET_BIND_SERVICE

Example security context:

```yaml
securityContext:
  runAsNonRoot: false # Alpine default
  readOnlyRootFilesystem: true
  allowPrivilegeEscalation: false
  capabilities:
    drop:
      - ALL
```

## Troubleshooting

### Container won't start:

Check logs:

```bash
docker logs llmaven-proxy
```

### Health check failing:

```bash
docker exec llmaven-proxy wget -qO- http://localhost:8888/health
```

### File system issues (Azure):

Verify credentials:

```bash
docker exec llmaven-proxy env | grep AZURE
```

## GitHub Container Registry Access

### Public Access

Images are public by default (for open source projects).

### Pulling in CI/CD

Use GitHub token:

```bash
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
docker pull ghcr.io/uw-ssec/llmaven/proxy:latest
```

### Pulling in Kubernetes

Create image pull secret:

```bash
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=your-github-username \
  --docker-password=your-github-pat
```

Then reference in deployment:

```yaml
spec:
  imagePullSecrets:
    - name: ghcr-secret
```
