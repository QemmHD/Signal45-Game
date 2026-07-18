from __future__ import annotations

import unittest

from tools.feasibility import model


class Prompt3OutcomeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config, cls.scenarios = model.load_inputs()

    def run_id(self, scenario_id: str) -> dict:
        return model.simulate_scenario(
            self.config, model.scenario_by_id(self.scenarios, scenario_id)
        )

    def test_full_proof_is_distinct_from_survival_only(self) -> None:
        east = self.run_id("S91")
        west = self.run_id("S92")
        self.assertEqual([east["outcome_class"], west["outcome_class"]], ["FULL_PROOF", "FULL_PROOF"])
        self.assertTrue(east["slice_proof_complete"])
        self.assertTrue(west["slice_proof_complete"])

    def test_recover_first_preserves_survival_without_claiming_full_proof(self) -> None:
        result = self.run_id("S94")
        self.assertEqual(result["outcome_class"], "RECOVER_FIRST")
        self.assertTrue(result["survival_viable"])
        self.assertFalse(result["slice_proof_complete"])
        self.assertIn("recover_first", result["ending_directions_available"])

    def test_proof_incomplete_is_not_shelter_death(self) -> None:
        result = self.run_id("S95")
        self.assertEqual(result["outcome_class"], "PROOF_INCOMPLETE")
        self.assertTrue(result["survival_viable"])
        self.assertFalse(result["viable"])
        self.assertIn("component", result["exact_limiting_fact"])

    def test_shelter_failure_has_named_cause(self) -> None:
        result = self.run_id("S96")
        self.assertEqual(result["outcome_class"], "SHELTER_FAILURE")
        self.assertFalse(result["survival_viable"])
        self.assertTrue(result["final"]["failure_reasons"])
        probe = result["prompt3_evidence"]["failure_cause_probe"]
        self.assertFalse(probe["recoverable"])
        self.assertEqual(probe["cascade"], ["Air", "Power", "Water"])

    def test_invariant_error_outranks_fictional_outcomes(self) -> None:
        result = self.run_id("S97")
        self.assertEqual(result["outcome_class"], "INVARIANT_ERROR")
        self.assertFalse(result["invariant_valid"])
        self.assertTrue(result["prompt3_evidence"]["invariant_detected"])

    def test_minimal_hope_uses_earned_state_without_resources(self) -> None:
        result = self.run_id("S93")
        hope = result["final"]["hope_beat"]
        self.assertEqual(hope["type"], "minimal")
        self.assertTrue(hope["uses_earned_state"])
        self.assertFalse(hope["creates_resources"])
        self.assertLessEqual(hope["work"], 2.0)
        self.assertEqual(result["outcome_class"], "RECOVER_FIRST")

    def test_full_hope_setup_remains_richer_proof(self) -> None:
        full = self.run_id("S169")
        fallback = self.run_id("S168")
        self.assertEqual(full["final"]["hope_beat"]["type"], "full")
        self.assertEqual(fallback["final"]["hope_beat"]["type"], "minimal")
        self.assertGreater(full["final"]["hope_beat"]["work"], fallback["final"]["hope_beat"]["work"])

    def test_outcome_convenience_boolean_is_derived(self) -> None:
        for scenario_id in ["S91", "S93", "S95", "S96", "S97"]:
            result = self.run_id(scenario_id)
            self.assertEqual(
                result["viable"],
                result["outcome_class"] in {"FULL_PROOF", "RECOVER_FIRST"},
                scenario_id,
            )

    def test_daily_slack_and_aggregate_buffer_are_reported_separately(self) -> None:
        result = self.run_id("S161")
        metrics = result["final"]["schedule_resilience"]
        self.assertIn("aggregate_weekly_unused_work", metrics)
        self.assertIn("minimum_daily_uncommitted_work", metrics)
        self.assertIn("minimum_phase_slack", metrics)
        self.assertTrue(metrics["aggregate_is_not_complete_safety_margin"])
        self.assertGreater(metrics["aggregate_weekly_unused_work"], metrics["minimum_daily_uncommitted_work"])

    def test_critical_path_and_incident_reserve_are_explicit(self) -> None:
        result = self.run_id("S162")
        metrics = result["final"]["schedule_resilience"]
        self.assertEqual(
            metrics["minimum_critical_path_slack_days"],
            min(metrics["critical_path_slack_by_project_days"].values()),
        )
        self.assertGreater(metrics["incident_response_reserve"], 0.0)
        self.assertGreaterEqual(metrics["incident_response_reserve_unused"], 0.0)

    def test_resilience_scenarios_execute_distinct_metric_probes(self) -> None:
        daily = self.run_id("S161")["prompt3_evidence"]["resilience_probe"]
        critical = self.run_id("S162")["prompt3_evidence"]["resilience_probe"]
        reserve = self.run_id("S163")["prompt3_evidence"]["resilience_probe"]
        self.assertEqual(daily["metric"], "minimum_daily_uncommitted_work")
        self.assertEqual(critical["metric"], "critical_path_slack")
        self.assertEqual(reserve["metric"], "incident_response_reserve")
        self.assertEqual(reserve["reserved"], reserve["used"] + reserve["unused"])

    def test_hope_scenarios_emit_distinct_state_probes(self) -> None:
        minimal = self.run_id("S168")["prompt3_evidence"]["hope_probe"]
        full = self.run_id("S169")["prompt3_evidence"]["hope_probe"]
        self.assertEqual(minimal["type"], "minimal")
        self.assertEqual(full["type"], "full")

    def test_no_scenario_hides_unaccounted_work(self) -> None:
        result = self.run_id("S170")
        evidence = result["prompt3_evidence"]
        self.assertTrue(evidence["all_work_accounted"])
        self.assertEqual({item["difference"] for item in evidence["work_accounting"]}, {0.0})

    def test_day_five_response_work_probe_names_reserve_and_overflow(self) -> None:
        probe = self.run_id("S166")["prompt3_evidence"]["response_work_probe"]
        self.assertEqual(
            probe["actual_incident_work"], probe["reserve_used"] + probe["overflow"]
        )
        self.assertGreater(probe["actual_incident_work"], 0.0)


if __name__ == "__main__":
    unittest.main()
