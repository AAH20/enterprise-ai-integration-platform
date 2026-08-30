import copy
import json
import unittest
from pathlib import Path

from flowforge.engine import evaluate, execute_transaction


ROOT = Path(__file__).parents[1]


class DurableWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.scenario = json.loads((ROOT / "examples/order-to-cash/scenario.json").read_text())

    def test_happy_path_completes_all_systems(self):
        tx = self.scenario["transactions"][0]
        result = execute_transaction(tx, self.scenario["adapter_profiles"][tx["profile"]])
        self.assertEqual(result.status, "completed")
        self.assertEqual(result.completed_steps, 6)
        self.assertEqual(result.compensations, 0)

    def test_transient_failure_retries_idempotently(self):
        tx = self.scenario["transactions"][1]
        result = execute_transaction(tx, self.scenario["adapter_profiles"][tx["profile"]])
        finance = next(item for item in result.steps if item.step == "finance")
        self.assertEqual(finance.status, "completed-after-retry")
        self.assertEqual(finance.attempt, 2)

    def test_permanent_failure_compensates_prior_steps(self):
        tx = self.scenario["transactions"][2]
        result = execute_transaction(tx, self.scenario["adapter_profiles"][tx["profile"]])
        self.assertEqual(result.status, "compensated")
        self.assertEqual(result.completed_steps, 3)
        self.assertEqual(result.compensations, 3)

    def test_duplicate_delivery_does_not_duplicate_business_transaction(self):
        reliability = evaluate(self.scenario)["reliability"]
        self.assertEqual(reliability["duplicate_deliveries_suppressed"], 1)
        self.assertEqual(reliability["duplicate_business_transactions"], 0)

    def test_enterprise_and_oss_profiles_are_exercised(self):
        transactions = evaluate(self.scenario)["transactions"]
        adapters = {step["adapter"] for item in transactions for step in item["steps"]}
        self.assertTrue(any("Salesforce" in item for item in adapters))
        self.assertTrue(any("SAP" in item for item in adapters))
        self.assertTrue(any("Oracle" in item for item in adapters))
        self.assertTrue(any("SuiteCRM" in item for item in adapters))
        self.assertTrue(any("Odoo" in item for item in adapters))
        self.assertTrue(any("PostgreSQL" in item for item in adapters))

    def test_unit_economics_are_reported(self):
        economics = evaluate(self.scenario)["unit_economics"]
        self.assertGreater(economics["modeled_completed_contribution_usd"], 0)
        self.assertGreater(economics["modeled_operating_cost_delta_usd"], 0)

    def test_never_auto_executes(self):
        self.assertFalse(evaluate(self.scenario)["production_control"]["auto_execute"])

    def test_receipt_is_deterministic(self):
        self.assertEqual(evaluate(self.scenario)["receipt_sha256"], evaluate(self.scenario)["receipt_sha256"])

    def test_unknown_profile_is_rejected(self):
        invalid = copy.deepcopy(self.scenario)
        invalid["transactions"][0]["profile"] = "unknown"
        with self.assertRaises(ValueError):
            evaluate(invalid)


if __name__ == "__main__":
    unittest.main()
