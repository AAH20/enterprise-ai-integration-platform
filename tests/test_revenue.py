from datetime import datetime, timezone

from fastapi.testclient import TestClient

from flowforge.api import create_app
from flowforge.revenue import RevenueEvent, exposure


def event(event_id: str = "evt-1", event_type: str = "delivered") -> dict:
    return {
        "event_id": event_id,
        "transaction_id": "order-1001",
        "customer_id": "customer-42",
        "event_type": event_type,
        "source": "sap-sandbox-contract",
        "occurred_at": "2026-08-31T00:00:00+00:00",
        "amount_usd": 50000.0,
        "gross_margin_pct": 0.4,
    }


def test_exposure_maps_stalled_delivery_to_invoice_risk():
    report = exposure([RevenueEvent.from_dict(event())], datetime(2026, 8, 31, 2, 0, tzinfo=timezone.utc), {"delivered": 60})
    assert report["stalled_transactions"] == 1
    assert report["revenue_at_risk_usd"] == 50000
    assert report["margin_at_risk_usd"] == 20000
    assert report["incidents"][0]["expected_next"] == "invoiced"
    assert not report["auto_remediate"]


def test_recognized_transaction_has_no_exposure():
    report = exposure([RevenueEvent.from_dict(event(event_type="recognized"))], datetime(2026, 8, 31, 2, 0, tzinfo=timezone.utc), {})
    assert report["stalled_transactions"] == 0


def test_api_suppresses_duplicate_events(tmp_path):
    with TestClient(create_app(str(tmp_path / "flowforge.db"), {"delivered": 60})) as client:
        first = client.post("/v1/events", json=event())
        second = client.post("/v1/events", json=event())
        assert first.status_code == 202
        assert first.json()["status"] == "accepted"
        assert second.json()["status"] == "duplicate-suppressed"


def test_api_reports_revenue_exposure(tmp_path):
    with TestClient(create_app(str(tmp_path / "flowforge.db"), {"delivered": 1})) as client:
        client.post("/v1/events", json=event())
        report = client.get("/v1/exposure")
        assert report.status_code == 200
        assert report.json()["revenue_at_risk_usd"] == 50000


def test_production_fails_closed_without_auth(monkeypatch, tmp_path):
    monkeypatch.setenv("FLOWFORGE_ENV", "production")
    monkeypatch.delenv("FLOWFORGE_API_TOKEN", raising=False)
    with TestClient(create_app(str(tmp_path / "flowforge.db"))) as client:
        assert client.get("/v1/exposure").status_code == 503
