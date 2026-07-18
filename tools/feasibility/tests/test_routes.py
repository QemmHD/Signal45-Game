from __future__ import annotations

import unittest

from tools.feasibility import model


class RouteNarrativeAndExpeditionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config, cls.scenarios = model.load_inputs()

    def run_id(self, scenario_id: str) -> dict:
        return model.simulate_scenario(
            self.config, model.scenario_by_id(self.scenarios, scenario_id)
        )

    def test_east_standard_route_is_viable_with_required_growth(self) -> None:
        result = self.run_id("S01")
        self.assertEqual(result["viable"], True)
        self.assertEqual(result["final"]["functional_areas"], 10)
        self.assertGreaterEqual(result["final"]["usable_buffer_percent"], 15.0)

    def test_west_standard_route_is_viable_with_required_growth(self) -> None:
        result = self.run_id("S02")
        self.assertEqual(result["viable"], True)
        self.assertEqual(result["final"]["functional_areas"], 10)
        self.assertGreaterEqual(result["final"]["usable_buffer_percent"], 15.0)

    def test_common_east_mistake_is_recoverable(self) -> None:
        result = self.run_id("S09")
        self.assertEqual(result["viable"], True)
        self.assertGreater(result["final"]["essential_and_incident_work"], self.run_id("S01")["final"]["essential_and_incident_work"])

    def test_common_west_mistake_is_recoverable(self) -> None:
        result = self.run_id("S10")
        self.assertEqual(result["viable"], True)
        self.assertGreater(len(result["final"]["completed_projects"]), 0)

    def test_temporary_resident_absence_is_recoverable(self) -> None:
        result = self.run_id("S13")
        day = result["days"][3]
        self.assertEqual(result["viable"], True)
        self.assertEqual(day["resident_availability"]["Teo"], 0.5)

    def test_named_role_disruptions_are_not_no_ops(self) -> None:
        results = [self.run_id(scenario_id) for scenario_id in ["S15", "S16", "S17"]]
        baseline = self.run_id("S01")
        for result in results:
            self.assertEqual(result["viable"], True)
            self.assertNotEqual(result["final"]["usable_buffer"], baseline["final"]["usable_buffer"])

    def test_day_two_injury_is_prevented_by_preparation(self) -> None:
        result = self.run_id("S27")
        self.assertEqual(result["construction_risk"]["injury"], "none")
        self.assertEqual(result["construction_risk"]["good_preparation_prevents"], True)
        self.assertGreater(result["days"][1]["work"]["risk_preparation"], 0.0)

    def test_day_two_injury_has_visible_deterministic_causes(self) -> None:
        result = self.run_id("S28")
        risk = result["construction_risk"]
        self.assertEqual(risk["injury"], "minor")
        self.assertEqual(risk["hazard_score"], 2)
        self.assertEqual(len(risk["visible_causes"]), 2)

    def test_teo_exposure_supports_medical_tutorial_without_new_injury(self) -> None:
        result = self.run_id("S29")
        self.assertEqual(result["construction_risk"]["injury"], "none")
        self.assertGreater(result["days"][0]["work"]["treatment_and_rest"], 0.0)
        self.assertLess(result["days"][0]["stocks_end"]["Medicine"], result["days"][0]["stocks_start"]["Medicine"])

    def test_active_and_delegated_use_same_graph_and_primary_reward(self) -> None:
        active = model.resolve_expedition(self.config, "east", "active")
        delegated = model.resolve_expedition(self.config, "east", "delegated")
        self.assertEqual(active["graph_id"], delegated["graph_id"])
        self.assertEqual(active["components"], delegated["components"])
        self.assertEqual(active["exclusive_reward"], False)
        self.assertEqual(delegated["exclusive_reward"], False)

    def test_delegated_policy_is_serialized_with_graph_result(self) -> None:
        delegated = self.run_id("S32")["expedition"]
        self.assertEqual(delegated["delegated_policy"]["risk_tolerance"], "low")
        self.assertEqual(
            delegated["delegated_policy"]["retreat_threshold"],
            "objective_secured",
        )

    def test_active_mode_adds_control_time_not_exclusive_value(self) -> None:
        active = model.resolve_expedition(self.config, "west", "active")
        delegated = model.resolve_expedition(self.config, "west", "delegated")
        self.assertGreater(active["real_minutes"], delegated["real_minutes"])
        self.assertEqual(active["components"], delegated["components"])

    def test_expedition_retreat_can_preserve_partial_success(self) -> None:
        for scenario_id in ["S33", "S34"]:
            expedition = self.run_id(scenario_id)["expedition"]
            self.assertEqual(expedition["retreat"], True)
            self.assertEqual(expedition["required_secured"], True)
            self.assertEqual(expedition["partial_success"], True)

    def test_wrong_tool_changes_cost_without_hard_lock(self) -> None:
        preferred = self.run_id("S31")["expedition"]
        wrong = self.run_id("S35")["expedition"]
        self.assertEqual(wrong["required_secured"], True)
        self.assertEqual(wrong["wrong_tool_alternative_used"], True)
        self.assertGreater(wrong["travel_cost"], preferred["travel_cost"])

    def test_carry_limit_forces_optional_reward_choice(self) -> None:
        expedition = self.run_id("S36")["expedition"]
        self.assertEqual(expedition["required_secured"], True)
        self.assertEqual(expedition["optional_secured"], False)
        self.assertIn("left optional reward", expedition["choices"][-1])

    def test_juna_admission_has_immediate_cost_and_no_free_labor(self) -> None:
        result = self.run_id("S43")
        self.assertEqual(result["juna"]["admitted"], True)
        self.assertEqual(result["juna"]["work_available"], 0.0)
        self.assertGreater(result["juna"]["stabilization_water"], 0.0)
        self.assertGreater(result["juna"]["stabilization_medicine"], 0.0)

    def test_juna_delay_and_refusal_remain_viable(self) -> None:
        for scenario_id in ["S39", "S42"]:
            result = self.run_id(scenario_id)
            self.assertEqual(result["viable"], True)
            self.assertEqual(result["juna"]["admitted"], False)
            self.assertEqual(result["juna"]["viable_alternative"], True)

    def test_juna_is_not_required_for_either_route(self) -> None:
        for scenario_id in ["S01", "S02"]:
            result = self.run_id(scenario_id)
            self.assertEqual(result["juna"]["admitted"], False)
            self.assertEqual(result["viable"], True)

    def test_all_juna_cases_have_an_eligible_ending(self) -> None:
        for number in range(37, 45):
            result = self.run_id(f"S{number}")
            self.assertEqual(result["viable"], True, f"S{number}")
            self.assertIn(True, result["final"]["ending_eligibility"].values())

    def test_signal_route_combinations_are_viable_and_not_identical(self) -> None:
        results = [self.run_id(scenario_id) for scenario_id in ["S05", "S06", "S07", "S08"]]
        self.assertEqual([result["viable"] for result in results], [True, True, True, True])
        outcomes = {
            (result["final"]["stocks"]["Medicine"], result["final"]["stocks"]["Materials"])
            for result in results
        }
        self.assertGreater(len(outcomes), 1)


if __name__ == "__main__":
    unittest.main()
