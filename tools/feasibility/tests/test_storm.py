from __future__ import annotations

import unittest

from tools.feasibility import model


class StormAndHighballTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config, cls.scenarios = model.load_inputs()

    def run_id(self, scenario_id: str) -> dict:
        return model.simulate_scenario(
            self.config, model.scenario_by_id(self.scenarios, scenario_id)
        )

    def test_prepared_storm_is_manageable(self) -> None:
        result = self.run_id("S18")
        self.assertEqual(result["storm"]["profile"], "prepared")
        self.assertEqual(result["viable"], True)
        self.assertLessEqual(result["storm"]["affected_system_count"], 2)

    def test_unprepared_storm_is_serious_but_recoverable(self) -> None:
        prepared = self.run_id("S18")
        unprepared = self.run_id("S22")
        self.assertEqual(unprepared["viable"], True)
        self.assertGreater(unprepared["storm"]["response_work"], prepared["storm"]["response_work"])
        self.assertGreaterEqual(unprepared["storm"]["affected_system_count"], prepared["storm"]["affected_system_count"])
        self.assertIn("Recovery shift", unprepared["days"][6]["warnings"][0])

    def test_extended_neglect_can_fail(self) -> None:
        result = self.run_id("S24")
        self.assertEqual(result["viable"], False)
        self.assertIn("unrecoverable", result["final"]["exact_failure_reason"])

    def test_cascade_is_interruptible(self) -> None:
        result = self.run_id("S20")
        self.assertEqual(result["storm"]["interruptible"], True)
        self.assertGreater(sum(stage["interruption_point"] for stage in result["storm"]["stages"]), 0)

    def test_cascade_never_exceeds_three_systems(self) -> None:
        for scenario_id in ["S18", "S20", "S22", "S24", "S71"]:
            result = self.run_id(scenario_id)
            self.assertLessEqual(
                result["storm"]["affected_system_count"],
                self.config["storm"]["maximum_affected_systems"],
                scenario_id,
            )
            self.assertEqual(result["storm"]["major_crises"], 1)

    def test_response_strategy_changes_cascade_cost(self) -> None:
        load_shed = self.run_id("S06")
        isolate = self.run_id("S18")
        self.assertNotEqual(load_shed["storm"]["strategy"], isolate["storm"]["strategy"])
        self.assertNotEqual(
            (load_shed["storm"]["charge_use"], load_shed["storm"]["water_loss"]),
            (isolate["storm"]["charge_use"], isolate["storm"]["water_loss"]),
        )

    def test_highball_is_optional_for_both_routes(self) -> None:
        for scenario_id in ["S01", "S02"]:
            result = self.run_id(scenario_id)
            self.assertEqual(result["viable"], True)
            self.assertIsNone(result["highball"])

    def test_highball_promise_repayment_is_modeled(self) -> None:
        result = self.run_id("S66")
        report = result["highball"]
        self.assertEqual(report["promise"], "kept")
        self.assertGreater(sum(report["capacity_losses"].values()), 0.0)
        self.assertGreater(report["costs"]["charge_cost"], 0.0)

    def test_broken_highball_promise_causes_later_loss_and_refusal(self) -> None:
        result = self.run_id("S68")
        report = result["highball"]
        self.assertEqual(report["promise"], "breached")
        self.assertEqual(report["refuses_next_highball"], True)
        self.assertEqual(len(report["capacity_losses"]), 2)

    def test_consecutive_highball_has_escalating_cost_and_negative_work_value(self) -> None:
        one = self.run_id("S66")["highball"]
        two = self.run_id("S73")["highball"]
        self.assertGreater(two["cost_breakdown"][1]["charge_cost"], two["cost_breakdown"][0]["charge_cost"])
        self.assertGreater(two["costs"]["charge_cost"], one["costs"]["charge_cost"])
        self.assertLess(two["net_week_work_value"], 0.0)


if __name__ == "__main__":
    unittest.main()
