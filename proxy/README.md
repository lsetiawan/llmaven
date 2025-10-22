# OpenAI API Proxy

A FastAPI-based proxy service for the OpenAI API with streaming support.

## Features

- ✅ Proxies all OpenAI API v1 endpoints
- ✅ Full streaming support for chat completions (Server-Sent Events)
- ✅ Request/response logging to local file system or Azure Blob Storage
- ✅ Dynamic log file naming: `{model}_{YYYYMMDD}.jsonl`
- ✅ Environment-based configuration
- ✅ Health check endpoint

## Setup

1. **Install dependencies:**

   ```bash
   # From the project root
   pixi add fastapi uvicorn httpx python-dotenv fsspec

   # Optional: For Azure Blob Storage logging
   pixi add adlfs  # Azure Data Lake Storage for fsspec
   ```

2. **Configure environment variables:**

   Copy the example environment file and add your OpenAI API key:

   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

3. **Run the proxy:**

   ```bash
   # From the proxy directory
   python main.py
   ```

   Or with uvicorn directly:

   ```bash
   uvicorn main:app --reload --port 8888
   ```

## Docker Deployment

See [CONTAINER.md](CONTAINER.md)

### Health Check:

```bash
curl http://localhost:8888/health
```

## Usage

Once running, the proxy will be available at `http://localhost:8000`.

### Example: Chat completion (non-streaming)

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

### Example: Chat completion (streaming)

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Hello!"}],
    "stream": true
  }'
```

### Example: List models

```bash
curl http://localhost:8000/v1/models
```

### Health check

```bash
curl http://localhost:8000/health
```

## Configuration

Configure the proxy using environment variables in `.env`:

### Core Settings

| Variable          | Required | Default                  | Description                |
| ----------------- | -------- | ------------------------ | -------------------------- |
| `OPENAI_API_KEY`  | Yes      | -                        | Your OpenAI API key        |
| `OPENAI_BASE_URL` | No       | `https://api.openai.com` | OpenAI API base URL        |
| `PROXY_PORT`      | No       | `8000`                   | Port for the proxy server  |
| `PROXY_TIMEOUT`   | No       | `300`                    | Request timeout in seconds |

### Logging Settings

| Variable                     | Required | Default      | Description                       |
| ---------------------------- | -------- | ------------ | --------------------------------- |
| `STORAGE_TYPE`               | No       | `local`      | Storage type: `local` or `azure`  |
| `LOCAL_LOG_DIR`              | No       | `logs`       | Directory for local log files     |
| `AZURE_STORAGE_ACCOUNT_NAME` | If Azure | -            | Azure Storage account name        |
| `AZURE_STORAGE_ACCOUNT_KEY`  | If Azure | -            | Azure Storage account key         |
| `AZURE_STORAGE_CONTAINER`    | No       | `proxy-logs` | Azure Blob Storage container name |

**Log File Naming:**

- Files are automatically named: `{model}_{YYYYMMDD}.jsonl`
- Example: `gpt-4_20241021.jsonl`, `gpt-3.5-turbo_20241021.jsonl`
- Each file contains all requests/responses for that model on that day

### Local Storage Example

```bash
STORAGE_TYPE=local
LOCAL_LOG_DIR=logs
```

Logs will be saved to: `logs/gpt-4_20241021.jsonl`

### Azure Blob Storage Example

```bash
STORAGE_TYPE=azure
AZURE_STORAGE_ACCOUNT_NAME=mystorageaccount
AZURE_STORAGE_ACCOUNT_KEY=your-account-key-here
AZURE_STORAGE_CONTAINER=proxy-logs
```

Logs will be uploaded to: `az://proxy-logs/gpt-4_20241021.jsonl`

## Architecture

The proxy forwards all requests to the OpenAI API while:

1. Adding the API key from environment variables
2. Preserving request headers (except auth/host)
3. Detecting and handling streaming responses
4. Supporting all HTTP methods (GET, POST, PUT, DELETE, PATCH)
5. Logging all requests and responses to storage (local or Azure)

### Log Format

Each log entry is a single JSON line with:

```json
{
  "timestamp": "2024-10-21T10:30:45.123456",
  "request": {
    "method": "POST",
    "path": "/v1/chat/completions",
    "headers": {...},
    "body": {
      "model": "gpt-4",
      "messages": [...]
    }
  },
  "response": {
    "status_code": 200,
    "headers": {...},
    "body": {...},
    "streaming": true
  }
}
```

## Architecture Notes

- **Storage**: Uses `fsspec` for unified interface to local filesystem and Azure
  Blob Storage
- **Azure Backend**: Uses `adlfs` (Azure Data Lake File System) for Azure
  operations
- Both storage backends support efficient append operations

## Future Enhancements

- [ ] Rate limiting
- [ ] Caching
- [ ] Authentication for proxy clients
- [ ] Metrics and monitoring
- [ ] Support for other cloud storage backends (S3, GCS)

## API Endpoints

- `GET /` - Service information
- `GET /health` - Health check
- `* /v1/{path}` - Proxy to OpenAI API v1 endpoints

## CI/CD

The proxy container is automatically built and pushed to GitHub Container
Registry on:

- Push to `main` branch (when files in `proxy/` change)
- Manual workflow dispatch

**Image tags:**

- `latest` - Most recent build
- `YYYYMMDD` - Date-based tag (e.g., `20241022`)
- `YYYYMMDD-sha-abc123` - Date + git SHA

**Registry:** `ghcr.io/uw-ssec/llmaven/proxy`
