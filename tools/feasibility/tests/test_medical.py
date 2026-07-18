from __future__ import annotations

import unittest

from tools.feasibility import medical, model


class MedicalTransactionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config, cls.scenarios = model.load_inputs()
        options = {"route": "east", "signal": "drainage"}
        selected, _ = model._selected_projects(cls.config, "east", options)
        cls.selected = selected

    def fresh_state(self):
        return model._initial_state(self.config, self.selected, {})

    def run_id(self, scenario_id: str) -> dict:
        return model.simulate_scenario(
            self.config, model.scenario_by_id(self.scenarios, scenario_id)
        )

    def test_treatment_start_reserves_named_medicine_and_water_once(self) -> None:
        state = self.fresh_state()
        medicine_before = state.stocks["Medicine"]
        water_before = state.stocks["Clean Water"]
        first = model.start_named_treatment(
            state,
            self.config,
            treatment_id="test:serious",
            resident="Ash",
            condition="serious_injury",
            severity="serious",
        )
        second = model.start_named_treatment(
            state,
            self.config,
            treatment_id="test:serious",
            resident="Ash",
            condition="serious_injury",
            severity="serious",
        )
        self.assertEqual(first, second)
        self.assertEqual(state.stocks["Medicine"], medicine_before - first["medicine_reserved"])
        self.assertEqual(state.stocks["Clean Water"], water_before - first["water_reserved"])

    def test_treatment_blocker_prevents_reservation(self) -> None:
        state = self.fresh_state()
        before = dict(state.stocks)
        plan = model.start_named_treatment(
            state,
            self.config,
            treatment_id="test:blocked",
            resident="Teo",
            condition="respiratory_exposure",
            severity="severe",
            room_available=False,
        )
        self.assertEqual(plan["status"], "planned")
        self.assertTrue(plan["blockers"])
        self.assertEqual(state.stocks, before)

    def test_treatment_interruption_keeps_reservation(self) -> None:
        state = self.fresh_state()
        plan = model.start_named_treatment(
            state,
            self.config,
            treatment_id="test:interrupt",
            resident="Maren",
            condition="waterborne_illness",
            severity="moderate",
        )
        medicine_after_start = state.stocks["Medicine"]
        interrupted = model.interrupt_named_treatment(state, plan["treatment_id"], "Power shed")
        self.assertEqual(interrupted["status"], "interrupted")
        self.assertFalse(interrupted["medicine_reserved_again"])
        self.assertEqual(state.stocks["Medicine"], medicine_after_start)

    def test_interrupted_treatment_resumes_and_completes_idempotently(self) -> None:
        state = self.fresh_state()
        plan = model.start_named_treatment(
            state,
            self.config,
            treatment_id="test:resume",
            resident="Teo",
            condition="respiratory_exposure",
            severity="limited",
        )
        model.interrupt_named_treatment(state, plan["treatment_id"], "Move cot")
        first = model.complete_named_treatment(state, plan["treatment_id"], current_health=65.0)
        snapshot = state.to_json()
        second = model.complete_named_treatment(state, plan["treatment_id"], current_health=65.0)
        self.assertEqual(first, second)
        self.assertEqual(state.to_json(), snapshot)
        self.assertEqual(first["status"], "completed")

    def test_treatment_never_heals_beyond_precondition_maximum(self) -> None:
        plan = medical.treatment_plan(
            self.config,
            "test:cap",
            "Ash",
            "minor_injury",
            "minor",
        )
        completed = medical.complete_treatment(
            plan, current_health=99.0, precondition_max_health=92.0
        )
        self.assertEqual(completed["health_after"], 92.0)
        self.assertTrue(completed["overhealing_prevented"])

    def test_severe_respiratory_treatment_blocks_productive_work(self) -> None:
        result = self.run_id("S121")
        plan = result["prompt3_evidence"]["medical_probe"]
        self.assertTrue(plan["productive_work_blocked"])
        self.assertEqual(plan["auto_pause_tier"], "critical")
        self.assertEqual(plan["progression_if_delayed"], "evacuate")

    def test_examination_is_distinct_from_completed_early_treatment(self) -> None:
        examination = self.run_id("S119")["prompt3_evidence"]["medical_probe"]
        treated = self.run_id("S120")["prompt3_evidence"]["medical_probe"]
        self.assertEqual(examination["stage"], "examination")
        self.assertEqual(examination["status"], "active")
        self.assertEqual(treated["stage"], "recovery")
        self.assertEqual(treated["status"], "completed")

    def test_minor_injury_remains_light_duty_not_forced_incapacity(self) -> None:
        result = self.run_id("S122")
        plan = result["prompt3_evidence"]["medical_probe"]
        self.assertFalse(plan["productive_work_blocked"])
        self.assertEqual(plan["movement_restriction"], "light duty")

    def test_serious_injury_is_restricted_and_recoverable_without_slice_death(self) -> None:
        result = self.run_id("S123")
        plan = result["prompt3_evidence"]["medical_probe"]
        self.assertTrue(plan["productive_work_blocked"])
        self.assertEqual(plan["status"], "completed")
        self.assertFalse(plan["slice_death_possible"])

    def test_waterborne_illness_uses_named_water_and_medicine(self) -> None:
        result = self.run_id("S125")
        plan = result["prompt3_evidence"]["medical_probe"]
        self.assertGreater(plan["medicine_reserved"], 0.0)
        self.assertGreater(plan["water_reserved"], 0.0)
        self.assertEqual(plan["condition"], "waterborne_illness")

    def test_treatment_survives_serialization(self) -> None:
        result = self.run_id("S128")
        self.assertTrue(result["prompt3_evidence"]["medical_save_roundtrip"])
        plan = result["prompt3_evidence"]["medical_probe"]
        self.assertEqual(plan["status"], "interrupted")
        self.assertFalse(plan["medicine_reserved_again"])

    def test_single_missed_warning_does_not_kill_in_slice(self) -> None:
        result = self.run_id("S130")
        self.assertNotEqual(result["outcome_class"], "SHELTER_FAILURE")
        self.assertFalse(result["prompt3_evidence"]["medical_probe"]["slice_death_possible"])


if __name__ == "__main__":
    unittest.main()
