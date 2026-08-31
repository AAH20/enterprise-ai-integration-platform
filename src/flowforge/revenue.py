from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any


EVENT_ORDER = ("opportunity_won", "order_created", "inventory_reserved", "shipped", "delivered", "invoiced", "paid", "recognized")


@dataclass(frozen=True)
class RevenueEvent:
    event_id: str
    transaction_id: str
    customer_id: str
    event_type: str
    source: str
    occurred_at: str
    amount_usd: float
    gross_margin_pct: float

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "RevenueEvent":
        event = cls(**value)
        if event.event_type not in EVENT_ORDER:
            raise ValueError("unsupported revenue event type")
        if event.amount_usd <= 0 or not 0 < event.gross_margin_pct <= 1:
            raise ValueError("revenue economics must be positive and bounded")
        datetime.fromisoformat(event.occurred_at.replace("Z", "+00:00"))
        return event


def exposure(events: list[RevenueEvent], now: datetime, stage_slos_minutes: dict[str, int]) -> dict[str, Any]:
    grouped: dict[str, list[RevenueEvent]] = {}
    for event in events:
        grouped.setdefault(event.transaction_id, []).append(event)
    incidents = []
    total_revenue = 0.0
    total_margin = 0.0
    for transaction_id, transaction_events in sorted(grouped.items()):
        ordered = sorted(transaction_events, key=lambda item: EVENT_ORDER.index(item.event_type))
        latest = ordered[-1]
        if latest.event_type == EVENT_ORDER[-1]:
            continue
        next_event = EVENT_ORDER[EVENT_ORDER.index(latest.event_type) + 1]
        occurred = datetime.fromisoformat(latest.occurred_at.replace("Z", "+00:00"))
        age_minutes = (now.astimezone(timezone.utc) - occurred.astimezone(timezone.utc)).total_seconds() / 60
        slo_minutes = stage_slos_minutes[latest.event_type]
        if age_minutes <= slo_minutes:
            continue
        margin = latest.amount_usd * latest.gross_margin_pct
        incidents.append({
            "transaction_id": transaction_id,
            "customer_id": latest.customer_id,
            "stalled_after": latest.event_type,
            "expected_next": next_event,
            "age_minutes": round(age_minutes, 2),
            "slo_minutes": slo_minutes,
            "revenue_at_risk_usd": round(latest.amount_usd, 2),
            "margin_at_risk_usd": round(margin, 2),
            "recommended_action": "collect diagnostics and request bounded replay approval",
        })
        total_revenue += latest.amount_usd
        total_margin += margin
    result = {
        "schema_version": "flowforge/revenue-exposure/v1",
        "evaluated_at": now.astimezone(timezone.utc).isoformat(),
        "stalled_transactions": len(incidents),
        "revenue_at_risk_usd": round(total_revenue, 2),
        "margin_at_risk_usd": round(total_margin, 2),
        "incidents": incidents,
        "auto_remediate": False,
    }
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":"))
    result["receipt_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    return result


def serialize(event: RevenueEvent) -> dict[str, Any]:
    return asdict(event)
