from __future__ import annotations

import argparse
import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

from .revenue import EVENT_ORDER, RevenueEvent, exposure, serialize


class EventInput(BaseModel):
    event_id: str
    transaction_id: str
    customer_id: str
    event_type: str
    source: str
    occurred_at: str
    amount_usd: float
    gross_margin_pct: float


DEFAULT_SLOS = {stage: 60 for stage in EVENT_ORDER[:-1]}


def create_app(database_path: str | None = None, stage_slos: dict[str, int] | None = None) -> FastAPI:
    path = database_path or os.getenv("FLOWFORGE_DB", "flowforge.db")
    if os.getenv("FLOWFORGE_ENV", "development") == "production" and path == "flowforge.db":
        raise RuntimeError("production requires an explicit durable database path")
    connection = sqlite3.connect(path, check_same_thread=False)
    connection.execute("CREATE TABLE IF NOT EXISTS events (event_id TEXT PRIMARY KEY, transaction_id TEXT NOT NULL, payload TEXT NOT NULL)")
    connection.execute("CREATE INDEX IF NOT EXISTS idx_events_transaction ON events(transaction_id)")
    connection.commit()
    slos = stage_slos or DEFAULT_SLOS
    app = FastAPI(title="FlowForge Revenue Reliability Control Plane", version="1.0.0")

    def authorize(authorization: str | None) -> None:
        expected = os.getenv("FLOWFORGE_API_TOKEN")
        if os.getenv("FLOWFORGE_ENV", "development") == "production" and not expected:
            raise HTTPException(503, "control-plane authentication is not configured")
        if expected and authorization != f"Bearer {expected}":
            raise HTTPException(401, "invalid bearer token")

    @app.get("/health/live")
    def live() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/health/ready")
    def ready() -> dict[str, str]:
        connection.execute("SELECT 1").fetchone()
        return {"status": "ready"}

    @app.post("/v1/events", status_code=202)
    def ingest(payload: EventInput, authorization: str | None = Header(default=None)) -> dict[str, Any]:
        authorize(authorization)
        try:
            event = RevenueEvent.from_dict(payload.model_dump())
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc
        existing = connection.execute("SELECT payload FROM events WHERE event_id = ?", (event.event_id,)).fetchone()
        if existing:
            return {"status": "duplicate-suppressed", "event": json.loads(existing[0])}
        value = serialize(event)
        connection.execute("INSERT INTO events VALUES (?, ?, ?)", (event.event_id, event.transaction_id, json.dumps(value, sort_keys=True)))
        connection.commit()
        return {"status": "accepted", "event": value}

    @app.get("/v1/exposure")
    def current_exposure(authorization: str | None = Header(default=None)) -> dict[str, Any]:
        authorize(authorization)
        rows = connection.execute("SELECT payload FROM events ORDER BY transaction_id, event_id").fetchall()
        events = [RevenueEvent.from_dict(json.loads(row[0])) for row in rows]
        return exposure(events, datetime.now(timezone.utc), slos)

    return app


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", type=Path, default=None)
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    uvicorn.run(create_app(str(args.database) if args.database else None), host="0.0.0.0", port=args.port)


if __name__ == "__main__":
    main()
