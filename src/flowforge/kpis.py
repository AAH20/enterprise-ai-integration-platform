from __future__ import annotations

import hashlib
import json
from typing import Any


def _metric(name: str, category: str, value: float, unit: str, target: float, direction: str, evidence: str) -> dict[str, Any]:
    passed = value >= target if direction == "higher" else value <= target
    return {"name": name, "category": category, "value": round(value, 4), "unit": unit,
            "target": target, "direction": direction, "passed": passed, "evidence": evidence}


def calculate_kpis(scenario: dict[str, Any], report: dict[str, Any]) -> dict[str, Any]:
    """Compile an executive KPI contract from deterministic replay plus disclosed observations."""
    context = scenario.get("kpi_context", {})
    unique: dict[str, dict[str, Any]] = {}
    for tx in scenario["transactions"]:
        unique.setdefault(tx["idempotency_key"], tx)
    outcomes: dict[str, dict[str, Any]] = {}
    for result in report["transactions"]:
        outcomes.setdefault(result["idempotency_key"], result)
    completed_keys = {key for key, result in outcomes.items() if result["status"] == "completed"}
    submitted_revenue = sum(tx["revenue_usd"] for tx in unique.values())
    completed_revenue = sum(tx["revenue_usd"] for key, tx in unique.items() if key in completed_keys)
    failed_margin = sum(tx["revenue_usd"] * tx["gross_margin_pct"] for key, tx in unique.items() if key not in completed_keys)
    reliability, economics = report["reliability"], report["unit_economics"]
    observations = max(1, int(context.get("event_observations", 1)))
    recommendations = max(1, int(context.get("ai_recommendations", 1)))
    deployments = max(1, int(context.get("deployments", 1)))
    authorization_attempts = max(1, int(context.get("authorization_attempts", 1)))
    platform_cost = economics["modeled_platform_transaction_cost_usd"]
    metrics = [
        _metric("revenue realization", "business", completed_revenue / submitted_revenue * 100, "%", 90, "higher", "synthetic replay"),
        _metric("revenue at risk", "business", submitted_revenue - completed_revenue, "USD", 5000, "lower", "synthetic replay"),
        _metric("margin at risk", "business", failed_margin, "USD", 2000, "lower", "synthetic replay"),
        _metric("completed contribution", "business", economics["modeled_completed_contribution_usd"], "USD", 10000, "higher", "modeled synthetic economics"),
        _metric("value-to-platform-cost ratio", "business", economics["modeled_completed_contribution_usd"] / max(platform_cost, .0001), "ratio", 100, "higher", "modeled synthetic economics"),
        _metric("straight-through processing", "reliability", reliability["straight_through_processing_pct"], "%", 95, "higher", "deterministic replay"),
        _metric("duplicate business transactions", "reliability", reliability["duplicate_business_transactions"], "count", 0, "lower", "deterministic replay"),
        _metric("duplicate suppression", "reliability", 100 if reliability["duplicate_deliveries_suppressed"] else 0, "%", 100, "higher", "deterministic replay"),
        _metric("compensation success", "reliability", 100 if reliability["successful_compensations"] else 0, "%", 100, "higher", "deterministic replay"),
        _metric("mean time to recovery", "operations", float(context.get("mttr_minutes", 0)), "minutes", 30, "lower", "synthetic observation"),
        _metric("deployment frequency", "delivery", float(context.get("deployments_per_week", 0)), "per week", 5, "higher", "synthetic observation"),
        _metric("change failure rate", "delivery", float(context.get("failed_deployments", 0)) / deployments * 100, "%", 10, "lower", "synthetic observation"),
        _metric("connector onboarding lead time", "delivery", float(context.get("connector_onboarding_days", 999)), "days", 10, "lower", "synthetic observation"),
        _metric("schema-valid events", "data", float(context.get("schema_valid_events", 0)) / observations * 100, "%", 99.9, "higher", "synthetic observation"),
        _metric("data lineage coverage", "data", float(context.get("lineage_covered_events", 0)) / observations * 100, "%", 99, "higher", "synthetic observation"),
        _metric("event freshness p95", "data", float(context.get("event_freshness_p95_seconds", 999)), "seconds", 60, "lower", "synthetic observation"),
        _metric("AI recommendation acceptance", "ai", float(context.get("accepted_ai_recommendations", 0)) / recommendations * 100, "%", 60, "higher", "synthetic observation"),
        _metric("AI evaluation pass rate", "ai", float(context.get("ai_eval_pass_pct", 0)), "%", 95, "higher", "synthetic observation"),
        _metric("AI cost per accepted recommendation", "ai", float(context.get("ai_cost_usd", 0)) / max(1, int(context.get("accepted_ai_recommendations", 0))), "USD", 0.25, "lower", "modeled synthetic cost"),
        _metric("cost per unique transaction", "finops", economics["modeled_cost_per_unique_transaction_usd"], "USD", 1, "lower", "modeled synthetic economics"),
        _metric("operating cost reduction", "finops", economics["modeled_operating_cost_delta_usd"] / max(economics["modeled_baseline_operating_cost_usd"], .0001) * 100, "%", 50, "higher", "modeled synthetic economics"),
        _metric("on-time customer outcomes", "customer", float(context.get("on_time_outcomes", 0)) / max(1, len(unique)) * 100, "%", 95, "higher", "synthetic observation"),
        _metric("unauthorized actions blocked", "security", float(context.get("authorization_blocks", 0)) / authorization_attempts * 100, "%", 100, "higher", "synthetic observation"),
        _metric("policy coverage", "security", float(context.get("policy_covered_actions", 0)) / max(1, int(context.get("privileged_actions", 1))) * 100, "%", 100, "higher", "synthetic observation"),
        _metric("evidence completeness", "compliance", float(context.get("evidence_complete_events", 0)) / observations * 100, "%", 100, "higher", "synthetic observation"),
    ]
    hard_gates = {
        "zero_duplicate_business_transactions": reliability["duplicate_business_transactions"] == 0,
        "all_unauthorized_actions_blocked": next(m for m in metrics if m["name"] == "unauthorized actions blocked")["passed"],
        "complete_evidence": next(m for m in metrics if m["name"] == "evidence completeness")["passed"],
    }
    result = {
        "schema_version": "flowforge/kpi-scorecard/v1", "evidence_level": "deterministic replay plus synthetic observations",
        "summary": {"passed": sum(m["passed"] for m in metrics), "total": len(metrics),
                    "target_attainment_pct": round(sum(m["passed"] for m in metrics) / len(metrics) * 100, 2)},
        "hard_gates": hard_gates,
        "decision": "eligible-for-sandbox-canary" if all(hard_gates.values()) and sum(m["passed"] for m in metrics) / len(metrics) >= .8 else "improve-before-canary",
        "metrics": metrics,
        "claim_boundary": "All business values and observations are synthetic. Replace them with signed production telemetry before commercial claims.",
    }
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":"))
    result["receipt_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    return result


def kpi_markdown(scorecard: dict[str, Any]) -> str:
    lines = ["# FlowForge comprehensive KPI scorecard", "", f"**Decision:** `{scorecard['decision']}`  ",
             f"**Target attainment:** `{scorecard['summary']['passed']}/{scorecard['summary']['total']}` (`{scorecard['summary']['target_attainment_pct']}%`)  ",
             f"**Evidence:** `{scorecard['evidence_level']}`", "", "> " + scorecard["claim_boundary"], ""]
    for category in dict.fromkeys(m["category"] for m in scorecard["metrics"]):
        lines += [f"## {category.title()} KPIs", "", "| KPI | Value | Target | Result | Evidence |", "|---|---:|---:|---|---|"]
        for m in (item for item in scorecard["metrics"] if item["category"] == category):
            comparator = "≥" if m["direction"] == "higher" else "≤"
            lines.append(f"| {m['name']} | {m['value']} {m['unit']} | {comparator} {m['target']} {m['unit']} | {'PASS' if m['passed'] else 'GAP'} | {m['evidence']} |")
        lines.append("")
    lines += ["## Hard promotion gates", ""] + [f"- {'PASS' if value else 'FAIL'} — `{name}`" for name, value in scorecard["hard_gates"].items()]
    lines += ["", f"Receipt: `{scorecard['receipt_sha256']}`", ""]
    return "\n".join(lines)
