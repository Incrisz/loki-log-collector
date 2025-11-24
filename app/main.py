import logging
from typing import Dict

from fastapi import FastAPI, HTTPException

from . import loki
from .config import Settings, get_settings
from .schemas import LogBatch

logger = logging.getLogger("log-collector")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

app = FastAPI(title="Log Collector", version="0.1.0")


@app.on_event("startup")
async def startup():
    settings = get_settings()
    logger.info("Log collector starting. Loki url=%s", settings.url)


@app.get("/healthz")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/logs", status_code=202)
async def ingest_logs(batch: LogBatch):
    settings: Settings = get_settings()

    if not batch.records:
        raise HTTPException(status_code=400, detail="No records provided")

    if settings.log_payloads:
        logger.info("Received log batch: %s", batch.model_dump())

    try:
        await loki.push_to_loki(batch.records)
    except Exception as exc:
        logger.exception("Failed to push to Loki")
        raise HTTPException(status_code=502, detail="Failed to push to Loki") from exc

    return {"accepted": len(batch.records)}
