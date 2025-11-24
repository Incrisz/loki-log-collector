import json
import time
from typing import Dict, List

import httpx

from .config import get_settings
from .schemas import LogRecord


def _to_nanos(timestamp_seconds: float) -> str:
    return str(int(timestamp_seconds * 1_000_000_000))


def _build_streams(records: List[LogRecord]) -> List[Dict]:
    streams: List[Dict] = []
    grouped: Dict[str, Dict] = {}

    for record in records:
        ts = record.timestamp.timestamp() if record.timestamp else time.time()
        labels = {
            "app": record.app,
            "level": record.level,
        }
        if record.labels:
            labels.update(record.labels)

        label_key = json.dumps(labels, sort_keys=True)
        entry = [
            _to_nanos(ts),
            json.dumps(
                {
                    "message": record.message,
                    "context": record.context or {},
                },
                ensure_ascii=True,
            ),
        ]

        if label_key not in grouped:
            grouped[label_key] = {"stream": labels, "values": [entry]}
        else:
            grouped[label_key]["values"].append(entry)

    streams.extend(grouped.values())
    return streams


async def push_to_loki(records: List[LogRecord]) -> None:
    settings = get_settings()

    payload = {"streams": _build_streams(records)}
    headers = {}
    auth = None

    if settings.tenant_id:
        headers["X-Scope-OrgID"] = settings.tenant_id

    if settings.basic_auth_user and settings.basic_auth_password:
        auth = (settings.basic_auth_user, settings.basic_auth_password)

    async with httpx.AsyncClient() as client:
        url = f"{settings.url.rstrip('/')}/loki/api/v1/push"
        resp = await client.post(url, json=payload, headers=headers, auth=auth, timeout=10)
        resp.raise_for_status()
