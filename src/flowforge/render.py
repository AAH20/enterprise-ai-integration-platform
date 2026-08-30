from __future__ import annotations

from typing import Any


def markdown(report: dict[str, Any]) -> str:
    reliability = report["reliability"]
    economics = report["unit_economics"]
    lines = [
        f"# {report['scenario']}", "",
        f"**Evidence:** `{report['evidence_level']}`  ",
        f"**Receipt:** `{report['receipt_sha256']}`  ",
        "**Production execution:** `disabled`", "",
        "## Executive scorecard", "",
        f"- Unique transactions: `{reliability['unique_transactions']}`",
        f"- Straight-through processing: `{reliability['straight_through_processing_pct']:.2f}%`",
        f"- Duplicate deliveries suppressed: `{reliability['duplicate_deliveries_suppressed']}`",
        f"- Duplicate business transactions: `{reliability['duplicate_business_transactions']}`",
        f"- Successful compensations: `{reliability['successful_compensations']}`",
        f"- Modeled completed contribution: `${economics['modeled_completed_contribution_usd']:,.2f}`",
        f"- Modeled transaction-platform cost: `${economics['modeled_platform_transaction_cost_usd']:,.2f}`", "",
        "## Workflow outcomes", "",
        "| Transaction | Status | Steps | Compensations | Cost | Net contribution |",
        "|---|---|---:|---:|---:|---:|",
    ]
    seen = set()
    for item in report["transactions"]:
        duplicate = item["idempotency_key"] in seen
        seen.add(item["idempotency_key"])
        status = "duplicate-suppressed" if duplicate else item["status"]
        lines.append(f"| {item['transaction_id']} | {status} | {item['completed_steps']} | {item['compensations']} | ${item['workflow_cost_usd']:,.2f} | ${item['net_contribution_usd']:,.2f} |")
    lines.extend(["", "## Claim boundary", ""])
    lines.extend(f"- {item}" for item in report["claim_boundary"])
    return "\n".join(lines) + "\n"
