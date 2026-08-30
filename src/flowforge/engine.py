from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class StepResult:
    step: str
    system: str
    adapter: str
    status: str
    attempt: int
    compensable: bool
    cost_usd: float
    detail: str


@dataclass(frozen=True)
class WorkflowResult:
    transaction_id: str
    idempotency_key: str
    status: str
    steps: list[StepResult]
    completed_steps: int
    compensations: int
    workflow_cost_usd: float
    contribution_usd: float
    net_contribution_usd: float


STEP_ORDER = ("crm", "erp", "finance", "logistics", "provisioning", "billing")
COMPENSABLE = {"crm": True, "erp": True, "finance": True, "logistics": True, "provisioning": True, "billing": False}


def _adapter_label(profile: dict[str, Any], system: str) -> str:
    selected = profile[system]
    return f"{selected['product']} ({selected['mode']})"


def execute_transaction(transaction: dict[str, Any], profile: dict[str, Any]) -> WorkflowResult:
    failure = transaction.get("failure_injection")
    steps: list[StepResult] = []
    completed: list[str] = []
    cost = 0.0

    for step in STEP_ORDER:
        adapter = _adapter_label(profile, step)
        step_cost = float(profile[step]["cost_per_call_usd"])
        attempts = 2 if failure == f"transient:{step}" else 1
        cost += step_cost * attempts
        if failure in {f"permanent:{step}", f"transient-exhausted:{step}"}:
            steps.append(StepResult(step, step, adapter, "failed", attempts, COMPENSABLE[step], round(step_cost * attempts, 4), "failure injected before commit"))
            for completed_step in reversed(completed):
                if COMPENSABLE[completed_step]:
                    compensation_cost = float(profile[completed_step]["compensation_cost_usd"])
                    cost += compensation_cost
                    steps.append(StepResult(f"compensate:{completed_step}", completed_step, _adapter_label(profile, completed_step), "compensated", 1, False, round(compensation_cost, 4), "reverse prior committed operation"))
            contribution = transaction["revenue_usd"] * transaction["gross_margin_pct"]
            return WorkflowResult(transaction["transaction_id"], transaction["idempotency_key"], "compensated", steps, len(completed), sum(item.status == "compensated" for item in steps), round(cost, 4), round(contribution, 2), round(-cost, 2))
        status = "completed-after-retry" if attempts == 2 else "completed"
        steps.append(StepResult(step, step, adapter, status, attempts, COMPENSABLE[step], round(step_cost * attempts, 4), "idempotent operation committed"))
        completed.append(step)

    contribution = transaction["revenue_usd"] * transaction["gross_margin_pct"]
    return WorkflowResult(transaction["transaction_id"], transaction["idempotency_key"], "completed", steps, len(completed), 0, round(cost, 4), round(contribution, 2), round(contribution - cost, 2))


def evaluate(scenario: dict[str, Any]) -> dict[str, Any]:
    validate(scenario)
    profiles = scenario["adapter_profiles"]
    results: list[WorkflowResult] = []
    idempotency_ledger: dict[str, WorkflowResult] = {}
    duplicate_deliveries = 0
    for transaction in scenario["transactions"]:
        key = transaction["idempotency_key"]
        if key in idempotency_ledger:
            duplicate_deliveries += 1
            results.append(idempotency_ledger[key])
            continue
        result = execute_transaction(transaction, profiles[transaction["profile"]])
        idempotency_ledger[key] = result
        results.append(result)

    unique_results = list(idempotency_ledger.values())
    completed = [item for item in unique_results if item.status == "completed"]
    compensated = [item for item in unique_results if item.status == "compensated"]
    completed_contribution = sum(item.net_contribution_usd for item in completed)
    total_cost = sum(item.workflow_cost_usd for item in unique_results)
    baseline = scenario["unit_economics"]["baseline_cost_per_transaction_usd"] * len(unique_results)
    human_baseline = scenario["unit_economics"]["baseline_human_minutes_per_transaction"] * len(unique_results)
    report: dict[str, Any] = {
        "schema_version": "flowforge/v1",
        "scenario": scenario["scenario"],
        "evidence_level": "deterministic-synthetic-integration-test",
        "transactions": [serialize_result(item) for item in results],
        "reliability": {
            "unique_transactions": len(unique_results),
            "completed_transactions": len(completed),
            "compensated_transactions": len(compensated),
            "duplicate_deliveries_suppressed": duplicate_deliveries,
            "duplicate_business_transactions": 0,
            "straight_through_processing_pct": round(len(completed) / len(unique_results) * 100, 2),
            "successful_compensations": sum(item.compensations for item in compensated),
        },
        "unit_economics": {
            "modeled_completed_contribution_usd": round(completed_contribution, 2),
            "modeled_platform_transaction_cost_usd": round(total_cost, 2),
            "modeled_baseline_operating_cost_usd": round(baseline, 2),
            "modeled_operating_cost_delta_usd": round(baseline - total_cost, 2),
            "modeled_baseline_human_minutes": human_baseline,
            "modeled_cost_per_unique_transaction_usd": round(total_cost / len(unique_results), 2),
            "modeled_net_contribution_per_completed_transaction_usd": round(completed_contribution / len(completed), 2) if completed else None,
        },
        "production_control": {
            "auto_execute": False,
            "status": "simulation-only",
            "required_gates": ["real sandbox contract tests", "identity and authorization", "financial reconciliation", "bounded canary", "operator approval", "rollback drill"],
        },
        "claim_boundary": [
            "No Salesforce, SAP, Oracle, Odoo, ERPNext, SuiteCRM, EspoCRM or cloud tenant was called",
            "All transactions, failures, revenue, contribution and costs are synthetic inputs",
            "Adapter names describe target contracts rather than certified vendor integrations",
            "Modeled contribution and cost deltas are not realized customer revenue or savings",
        ],
    }
    canonical = json.dumps(report, sort_keys=True, separators=(",", ":"))
    report["receipt_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    return report


def serialize_result(result: WorkflowResult) -> dict[str, Any]:
    value = asdict(result)
    value["steps"] = [asdict(item) for item in result.steps]
    return value


def validate(scenario: dict[str, Any]) -> None:
    required = {"scenario", "adapter_profiles", "transactions", "unit_economics"}
    missing = sorted(required - scenario.keys())
    if missing:
        raise ValueError(f"missing keys: {', '.join(missing)}")
    if not scenario["transactions"]:
        raise ValueError("transactions must not be empty")
    for profile_name, profile in scenario["adapter_profiles"].items():
        missing_steps = sorted(set(STEP_ORDER) - profile.keys())
        if missing_steps:
            raise ValueError(f"profile {profile_name} missing adapters: {', '.join(missing_steps)}")
    for transaction in scenario["transactions"]:
        if transaction["profile"] not in scenario["adapter_profiles"]:
            raise ValueError(f"unknown profile: {transaction['profile']}")
        if transaction["revenue_usd"] <= 0 or not 0 < transaction["gross_margin_pct"] <= 1:
            raise ValueError("transaction economics must be positive and bounded")
