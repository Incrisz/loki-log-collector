# Log Collector (FastAPI → Loki)

FastAPI service that accepts logs from multiple apps and forwards them to Grafana Loki so you can visualize them in Grafana.

## Features
- `/logs` endpoint that accepts batches of log records with app/level/message/timestamp/labels/context.
- Forwards logs to Loki's push API, grouping by labels.
- Health check at `/healthz`.
- Configurable Loki URL, tenant, and basic auth via env vars.

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration
Create a `.env` (auto-loaded) or set environment variables (prefixed with `LOKI_`):
- `LOKI_URL` (default `http://localhost:3100`)
- `LOKI_TENANT_ID` (optional, for multi-tenant Loki)
- `LOKI_BASIC_AUTH_USER` / `LOKI_BASIC_AUTH_PASSWORD` (optional)
- `LOKI_LOG_PAYLOADS` (default `false`)

## Run
```bash
uvicorn app.main:app --reload --port 8000
```

### Docker
```bash
docker build -t log-collector .
docker run -p 8000:8000 --env-file .env log-collector
```

## Usage
Send a batch of logs:
```bash
curl -X POST http://localhost:8000/logs \
  -H "Content-Type: application/json" \
  -d '{
    "records": [
      {
        "app": "checkout",
        "level": "info",
        "message": "payment processed",
        "labels": {"region": "us-east-1"},
        "context": {"order_id": "12345"}
      }
    ]
  }'
```

Loki will receive streams grouped by `app`, `level`, and any extra `labels` you send. Each log line contains the message and context JSON.

## Notes
- Timestamps default to server receive time if not provided (Loki expects nanoseconds).
- Ensure your Grafana is configured to read from the target Loki instance.
# loki-log-collector
