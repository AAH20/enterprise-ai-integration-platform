import json
from pathlib import Path

from flowforge.engine import evaluate
from flowforge.kpis import calculate_kpis, kpi_markdown


def fixture():
    scenario = json.loads(Path("examples/order-to-cash/scenario.json").read_text())
    return scenario, calculate_kpis(scenario, evaluate(scenario))


def test_scorecard_has_comprehensive_categories_and_hard_gates():
    _, scorecard = fixture()
    categories = {metric["category"] for metric in scorecard["metrics"]}
    assert categories == {"business", "reliability", "operations", "delivery", "data", "ai", "finops", "customer", "security", "compliance"}
    assert len(scorecard["metrics"]) == 25
    assert all(scorecard["hard_gates"].values())


def test_bad_authorization_observation_blocks_canary():
    scenario, _ = fixture()
    scenario["kpi_context"]["authorization_blocks"] = 6
    scorecard = calculate_kpis(scenario, evaluate(scenario))
    assert scorecard["decision"] == "improve-before-canary"
    assert not scorecard["hard_gates"]["all_unauthorized_actions_blocked"]


def test_kpi_markdown_discloses_synthetic_boundary():
    _, scorecard = fixture()
    output = kpi_markdown(scorecard)
    assert "synthetic" in output.lower()
    assert "Hard promotion gates" in output
