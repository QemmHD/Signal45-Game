from __future__ import annotations

import unittest

from tools.feasibility.model import load_inputs, run_scenarios
from tools.spatial.tests.helpers import DATA
from tools.spatial.travel import calculate_travel_metrics
from tools.spatial.validate_layouts import run_validation


class FeasibilityIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config, scenarios = load_inputs()
        cls.results = {item["scenario_id"]: item for item in run_scenarios(cls.config, scenarios)}

    def test_cross_model_validation_has_no_mismatch(self) -> None:
        report = run_validation()
        self.assertEqual(report["cross_model_errors"], [])

    def test_platform_lighting_canon_is_unified(self) -> None:
        power = self.config["utilities"]["power"]
        self.assertIn("platform_lighting", power["loads"])
        self.assertNotIn("task_lighting", power["loads"])
        self.assertNotIn("comfort_lighting", power["loads"])
        self.assertEqual(self.config["relay_load_test"]["shed_load"], "platform_lighting")

    def test_temporary_cot_and_repurpose_do_not_increment_area(self) -> None:
        projects = {item["id"]: item for item in self.config["projects"]}
        self.assertNotIn("functional_areas", projects["triage_cot_install"]["benefits"])
        self.assertNotIn("functional_areas", projects["concession_repurpose"]["benefits"])
        for project_id in ["east_utility_connection", "west_utility_connection", "triage_upgrade"]:
            self.assertEqual(projects[project_id]["benefits"]["functional_areas"], 1)

    def test_spatial_factor_replaces_not_adds_to_abstract_allowance(self) -> None:
        for route, scenario_id in [("east", "S01"), ("west", "S02")]:
            mapping = self.config["routes"][route]["spatial_mapping"]
            self.assertTrue(mapping["replaces_abstract"])
            result = self.results[scenario_id]
            for day in result["days"]:
                self.assertEqual(day["work"]["travel_source"], f"spatial:{route}_day7")
                self.assertFalse(day["work"]["travel_double_counted"])
                self.assertEqual(day["work"]["travel_factor"], mapping["travel_factor"])

    def test_coordinate_evidence_does_not_understate_selected_factor(self) -> None:
        for route in ["east", "west"]:
            mapping = self.config["routes"][route]["spatial_mapping"]
            metrics = calculate_travel_metrics(DATA, DATA.layout(mapping["layout_id"]))
            self.assertEqual(mapping["coordinate_travel_factor"], metrics["coordinate_travel_factor"])
            self.assertEqual(mapping["coordinate_hauling_factor"], metrics["coordinate_hauling_factor"])
            self.assertGreaterEqual(mapping["travel_factor"], metrics["coordinate_travel_factor"])
            self.assertGreaterEqual(mapping["hauling_factor"], metrics["coordinate_hauling_factor"])

    def test_resident_base_capacity_was_not_increased(self) -> None:
        self.assertEqual(self.config["work"]["base_capacity_per_resident_day"], 12.0)

    def test_competent_routes_remain_full_proof_without_highball(self) -> None:
        for scenario_id in ["S01", "S02"]:
            result = self.results[scenario_id]
            self.assertEqual(result["outcome_class"], "FULL_PROOF")
            self.assertIsNone(result["highball"])
            self.assertEqual(result["final"]["functional_areas"], 10)

    def test_mistakes_prepared_storm_and_juna_cases_retain_expectations(self) -> None:
        scenario_ids = ["S09", "S10", "S18", "S19"] + [f"S{number:02d}" for number in range(37, 45)]
        for scenario_id in scenario_ids:
            with self.subTest(scenario=scenario_id):
                self.assertTrue(self.results[scenario_id]["expectation_met"])

    def test_every_mandatory_prompt2_prompt3_scenario_still_matches(self) -> None:
        mandatory = [item for item in self.results.values() if item["mandatory"]]
        self.assertEqual(len(mandatory), 176)
        self.assertTrue(all(item["expectation_met"] for item in mandatory))

    def test_day_five_zero_slack_is_not_given_hidden_work(self) -> None:
        for scenario_id in ["S01", "S02"]:
            day5 = self.results[scenario_id]["days"][4]
            self.assertEqual(day5["work"]["daily_uncommitted"], 0.0)
            self.assertEqual(day5["work"]["minimum_phase_slack"], 0.0)
            self.assertFalse(day5["work"]["travel_double_counted"])


if __name__ == "__main__":
    unittest.main()
