from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class LogRecord(BaseModel):
    app: str = Field(..., description="Name/identifier of the emitting app")
    level: str = Field("info", description="Log level (info, warn, error, debug)")
    message: str = Field(..., description="Log message")
    timestamp: Optional[datetime] = Field(
        default=None,
        description="Timestamp of the log. Defaults to server receive time if omitted.",
    )
    # Arbitrary extra labels to attach to the stream in Loki
    labels: Optional[dict[str, str]] = Field(
        default=None, description="Additional label key/value pairs for Loki"
    )
    # Arbitrary structured context serialized into the log line
    context: Optional[dict] = Field(
        default=None,
        description="Structured context to include with the log line",
    )


class LogBatch(BaseModel):
    records: List[LogRecord] = Field(..., description="List of logs to ingest")
