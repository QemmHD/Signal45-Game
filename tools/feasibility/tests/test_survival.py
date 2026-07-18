from __future__ import annotations

import unittest

from tools.feasibility import forecasts, model, survival, utilities


class SurvivalConditionAndStockTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config, cls.scenarios = model.load_inputs()

    def run_id(self, scenario_id: str) -> dict:
        return model.simulate_scenario(
            self.config, model.scenario_by_id(self.scenarios, scenario_id)
        )

    def test_critical_health_has_zero_productive_work(self) -> None:
        profile = survival.resident_work_profile(
            self.config, "Ash", {"health": "critical"}
        )
        self.assertEqual(profile["productive_capacity"], 0.0)
        self.assertFalse(profile["assignment_eligible"])
        self.assertTrue(profile["treatment_required"])

    def test_medical_incapacity_has_zero_productive_work(self) -> None:
        profile = survival.resident_work_profile(
            self.config, "Imka", medical_restriction="medically_incapacitated"
        )
        self.assertEqual(profile["productive_work_capacity"], 0.0)
        self.assertTrue(profile["requires_assistance"])

    def test_emergency_self_action_is_separate_from_project_work(self) -> None:
        profile = survival.resident_work_profile(
            self.config, "Teo", medical_restriction="severe_respiratory"
        )
        self.assertTrue(profile["emergency_self_action_available"])
        self.assertEqual(profile["productive_capacity"], 0.0)
        self.assertFalse(profile["available_for_assignment"])

    def test_unconscious_resident_has_no_self_action(self) -> None:
        profile = survival.resident_work_profile(
            self.config, "Maren", medical_restriction="unconscious"
        )
        self.assertFalse(profile["emergency_self_action_available"])
        self.assertTrue(profile["evacuation_required"])

    def test_shelter_level_emergency_capacity_uses_other_residents(self) -> None:
        profiles = [
            survival.resident_work_profile(
                self.config,
                name,
                medical_restriction=("medically_incapacitated" if name == "Ash" else "none"),
            )
            for name in ["Ash", "Imka", "Teo", "Maren"]
        ]
        result = survival.shelter_emergency_capacity(profiles, 2.0)
        self.assertTrue(result["met"])
        self.assertNotIn("Ash", result["providers"])
        self.assertFalse(result["forced_incapacitated_labor"])

    def test_all_incapacitated_requires_named_fallback_not_forced_labor(self) -> None:
        result = self.run_id("S102")["prompt3_evidence"]["shelter_emergency_probe"]
        self.assertFalse(result["met"])
        self.assertTrue(result["outside_or_manual_fallback_required"])
        self.assertFalse(result["forced_incapacitated_labor"])

    def test_hunger_reduces_but_does_not_zero_work(self) -> None:
        fed = survival.resident_work_profile(self.config, "Teo")
        hungry = survival.resident_work_profile(
            self.config, "Teo", {"hunger": "restricted"}
        )
        self.assertGreater(fed["productive_capacity"], hungry["productive_capacity"])
        self.assertGreater(hungry["productive_capacity"], 0.0)

    def test_fatigue_collapse_blocks_assignment(self) -> None:
        profile = survival.resident_work_profile(
            self.config, "Maren", {"fatigue": "collapse_risk"}
        )
        self.assertEqual(profile["productive_capacity"], 0.0)
        self.assertEqual(profile["current_work_restriction"], "collapse_risk")

    def test_stress_reduces_without_medical_incapacity(self) -> None:
        steady = survival.resident_work_profile(self.config, "Ash")
        acute = survival.resident_work_profile(
            self.config, "Ash", {"stress": "acute"}
        )
        self.assertLess(acute["productive_capacity"], steady["productive_capacity"])
        self.assertGreater(acute["productive_capacity"], 0.0)
        self.assertFalse(acute["treatment_required"])

    def test_combined_condition_penalty_is_capped(self) -> None:
        profile = survival.resident_work_profile(
            self.config,
            "Ash",
            {"health": "impaired", "hunger": "prolonged", "fatigue": "exhausted", "stress": "acute"},
        )
        self.assertEqual(profile["combined_penalty"], self.config["work"]["condition_combination"]["maximum_penalty"])
        self.assertGreater(profile["productive_capacity"], 0.0)

    def test_food_issue_is_discrete_and_one_missed_meal_is_not_critical(self) -> None:
        normal = survival.food_issue(self.config, 4, issue="normal")
        missed = survival.food_issue(self.config, 4, issue="missed")
        self.assertEqual(normal["amount"], 4.0)
        self.assertEqual(missed["amount"], 0.0)
        self.assertFalse(missed["critical_health_loss"])

    def test_restricted_food_saves_stock_at_a_condition_cost(self) -> None:
        normal = survival.food_issue(self.config, 5, issue="normal")
        restricted = survival.food_issue(self.config, 5, issue="restricted")
        self.assertLess(restricted["amount"], normal["amount"])
        self.assertGreater(restricted["hunger_steps"], 0)
        self.assertGreater(restricted["stress_points"], 0)

    def test_repeated_food_restriction_escalates(self) -> None:
        one = survival.ration_consequence(self.config, 1)
        three = survival.ration_consequence(self.config, 3)
        self.assertGreater(three["stress_points"], one["stress_points"])
        self.assertEqual(three["hunger_band"], "prolonged")
        self.assertFalse(three["immediate_critical_harm"])

    def test_water_restriction_saves_stock_and_limits_treatment(self) -> None:
        normal = survival.water_issue(self.config, 4, issue="normal")
        restricted = survival.water_issue(self.config, 4, issue="restricted")
        self.assertLess(restricted["amount"], normal["amount"])
        self.assertTrue(restricted["treatment_restricted"])
        self.assertGreater(restricted["stress_points"], 0)

    def test_food_pressure_response_changes_failure_to_full_proof_at_cost(self) -> None:
        ignored = self.run_id("S104")
        response = self.run_id("S105")
        self.assertEqual(ignored["outcome_class"], "SHELTER_FAILURE")
        self.assertEqual(response["outcome_class"], "FULL_PROOF")
        self.assertGreater(
            max(day["condition_summary"]["stress_points"] for day in response["days"]),
            0,
        )
        probe = ignored["prompt3_evidence"]["resource_pressure_probe"]
        self.assertEqual(probe["stock"], "Food")
        self.assertLess(probe["ending"], probe["minimum_viable_reserve"])

    def test_east_water_response_restores_viability_without_erasing_west_advantage(self) -> None:
        east = self.run_id("S108")
        west = self.run_id("S110")
        self.assertEqual(east["outcome_class"], "FULL_PROOF")
        self.assertEqual(west["outcome_class"], "FULL_PROOF")
        self.assertLess(east["final"]["stocks"]["Clean Water"], west["final"]["stocks"]["Clean Water"])

    def test_medicine_pressure_priority_has_opportunity_cost(self) -> None:
        response = self.run_id("S171")
        ignored = self.run_id("S174")
        evidence = response["prompt3_evidence"]["medicine_prioritization"]
        self.assertEqual(response["outcome_class"], "RECOVER_FIRST")
        self.assertEqual(ignored["outcome_class"], "SHELTER_FAILURE")
        self.assertFalse(evidence["free_medicine_created"])
        self.assertGreater(evidence["stress_points"], 0)

    def test_materials_deferral_preserves_survival_but_not_full_proof(self) -> None:
        response = self.run_id("S172")
        ignored = self.run_id("S175")
        self.assertEqual(response["outcome_class"], "RECOVER_FIRST")
        self.assertEqual(ignored["outcome_class"], "SHELTER_FAILURE")
        self.assertEqual(response["final"]["hope_beat"]["type"], "minimal")

    def test_charge_shortage_load_shed_preserves_full_proof(self) -> None:
        response = self.run_id("S173")
        ignored = self.run_id("S176")
        self.assertEqual(response["outcome_class"], "FULL_PROOF")
        self.assertEqual(response["relay_load_test"]["response"], "shed_lighting")
        self.assertEqual(ignored["outcome_class"], "SHELTER_FAILURE")

    def test_charge_discharge_applies_conversion_loss_and_stage_limit(self) -> None:
        result = utilities.discharge_charge(
            self.config, 10.0, 99.0, branch_connected=True, stages=1
        )
        self.assertEqual(result["delivered"], self.config["stocks"]["Charge"]["discharge_limit_per_stage"])
        self.assertGreater(result["stock_draw"], result["delivered"])
        self.assertGreater(result["conversion_loss"], 0.0)

    def test_charge_rejects_disconnected_branch(self) -> None:
        result = utilities.discharge_charge(
            self.config, 10.0, 2.0, branch_connected=False
        )
        self.assertFalse(result["accepted"])
        self.assertEqual(result["stock_draw"], 0.0)
        self.assertIn("disconnected", result["reason"])

    def test_forecast_classes_reject_false_unknown(self) -> None:
        with self.assertRaises(ValueError):
            forecasts.build_forecast_card(
                subject="East structure",
                classification="UNKNOWN",
                current=None,
            )

    def test_forecast_names_failing_link_within_two_taps(self) -> None:
        diagnosis = utilities.diagnose_water_link(
            self.config,
            source=8.0,
            pump=0.6,
            treatment=0.9,
            delivery=0.95,
            storage_state="clean",
            demand=5.0,
        )
        card = forecasts.build_forecast_card(
            subject="Water",
            classification="FACT",
            current=diagnosis["throughput"],
            failing_link=diagnosis["failing_link"],
        )
        self.assertEqual(diagnosis["failing_link"], "pumping")
        self.assertLessEqual(card["overview_tap_depth"], 2)


if __name__ == "__main__":
    unittest.main()
