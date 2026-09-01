from __future__ import annotations

import argparse
import json
from pathlib import Path

from .engine import evaluate
from .render import markdown
from .kpis import calculate_kpis, kpi_markdown


def main() -> None:
    parser = argparse.ArgumentParser(description="Replay durable enterprise integration transactions")
    parser.add_argument("scenario", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    scenario = json.loads(args.scenario.read_text())
    report = evaluate(scenario)
    scorecard = calculate_kpis(scenario, report)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "transaction-ledger.json").write_text(json.dumps(report, indent=2) + "\n")
    (args.output / "executive-scorecard.md").write_text(markdown(report))
    (args.output / "kpi-scorecard.json").write_text(json.dumps(scorecard, indent=2) + "\n")
    (args.output / "kpi-scorecard.md").write_text(kpi_markdown(scorecard))
    print(json.dumps({"receipt_sha256": report["receipt_sha256"], "auto_execute": report["production_control"]["auto_execute"]}, indent=2))


if __name__ == "__main__":
    main()
