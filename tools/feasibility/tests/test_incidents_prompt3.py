from __future__ import annotations

import unittest

from tools.feasibility import incidents, model, utilities


class UtilityIncidentAndHighballTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config, cls.scenarios = model.load_inputs()

    def run_id(self, scenario_id: str) -> dict:
        return model.simulate_scenario(
            self.config, model.scenario_by_id(self.scenarios, scenario_id)
        )

    def test_relay_load_test_charge_response_consumes_reserve_once(self) -> None:
        result = self.run_id("S112")
        event = result["relay_load_test"]
        self.assertEqual(event["response"], "charge")
        self.assertTrue(event["resolved"])
        self.assertGreater(event["charge_draw"], 0.0)
        self.assertTrue(event["safe_save_before_commitment"])

    def test_relay_load_test_sheds_and_restores_optional_lighting(self) -> None:
        event = self.run_id("S113")["relay_load_test"]
        self.assertFalse(event["lighting_visible_during"])
        self.assertTrue(event["lighting_restored"])
        self.assertEqual(event["shed_load"], "task_lighting")

    def test_lighting_restore_probe_spans_the_next_stable_phase(self) -> None:
        probe = self.run_id("S117")["prompt3_evidence"]["relay_restore_probe"]
        self.assertTrue(probe["visible_before"])
        self.assertFalse(probe["visible_during"])
        self.assertTrue(probe["visible_next_stable_phase"])
        self.assertTrue(probe["restored_without_new_charge"])

    def test_relay_load_test_delay_preserves_resources_at_forecast_cost(self) -> None:
        event = self.run_id("S114")["relay_load_test"]
        self.assertEqual(event["charge_draw"], 0.0)
        self.assertTrue(event["calibration_delayed"])
        self.assertLess(event["warning_lead_delta"], 0)

    def test_relay_load_test_is_idempotent_across_state_save(self) -> None:
        options = {"route": "east", "signal": "drainage"}
        selected, _ = model._selected_projects(self.config, "east", options)
        state = model._initial_state(self.config, selected, {})
        first = model.apply_relay_load_test(state, self.config, "charge")
        after = state.stocks["Charge"]
        restored = model.SimulationState.from_json(state.to_json())
        second = model.apply_relay_load_test(restored, self.config, "charge")
        self.assertEqual(first, second)
        self.assertEqual(restored.stocks["Charge"], after)

    def test_power_priority_sheds_optional_before_essential(self) -> None:
        result = model.calculate_power(
            self.config,
            {"triage_cot_install", "workshop_install", "comfort_lighting"},
            storm_affected_systems=3,
            demand_multiplier=1.2,
        )
        order = result["shutdown_order_if_uncovered"]
        self.assertTrue(order)
        self.assertIn("comfort", order[0])
        self.assertEqual(result["next_endangered"], "water_pumping")

    def test_air_progresses_one_visible_stage_with_warning(self) -> None:
        result = utilities.progress_air_stage(
            self.config, "stable", pressure_steps=1
        )
        self.assertEqual(result["to"], "loaded")
        self.assertTrue(result["warning_shown"])
        self.assertFalse(result["instant_unexplained_exposure"])

    def test_air_interruption_stops_progression(self) -> None:
        uncontrolled = utilities.progress_air_stage(
            self.config, "loaded", pressure_steps=2
        )
        interrupted = utilities.progress_air_stage(
            self.config, "loaded", pressure_steps=2, interruption_steps=2
        )
        self.assertNotEqual(uncontrolled["to"], interrupted["to"])
        self.assertEqual(interrupted["to"], "loaded")

    def test_water_contamination_names_clean_storage_link(self) -> None:
        result = utilities.diagnose_water_link(
            self.config,
            source=8.0,
            pump=1.0,
            treatment=0.9,
            delivery=0.95,
            storage_state="contaminated",
            demand=4.0,
        )
        self.assertEqual(result["failing_link"], "clean storage")
        self.assertEqual(result["diagnosable_within_taps"], 2)

    def test_structure_warns_before_closure_and_never_rolls_unseen_injury(self) -> None:
        warning = utilities.structure_transition(
            self.config, "strained", pressure_steps=1
        )
        closed = utilities.structure_transition(
            self.config, "critical", pressure_steps=1
        )
        self.assertEqual(warning["to"], "unstable")
        self.assertTrue(warning["warning"])
        self.assertEqual(closed["to"], "closed")
        self.assertTrue(closed["tasks_suspended"])
        self.assertFalse(closed["unseen_injury"])

    def test_incident_record_contains_warning_and_recovery_contract(self) -> None:
        incident = incidents.create_incident(
            self.config, "test:air", "air_contamination", section="east"
        )
        self.assertEqual(incident["current_stage"], "warning")
        self.assertTrue(incident["initial_warning"])
        self.assertGreater(incident["recovery_work"], 0.0)
        self.assertEqual(incident["maximum_propagation_depth"], 1)

    def test_incident_escalation_is_discrete(self) -> None:
        warning = incidents.create_incident(
            self.config, "test:water", "water_contamination"
        )
        active = incidents.advance_incident(warning)
        severe = incidents.advance_incident(active)
        self.assertEqual([warning["current_stage"], active["current_stage"], severe["current_stage"]], ["warning", "active", "severe"])
        self.assertGreater(len(severe["transaction_ids"]), len(warning["transaction_ids"]))

    def test_incident_interruption_stops_propagation(self) -> None:
        incident = incidents.create_incident(
            self.config, "test:structure", "structural_instability"
        )
        interrupted = incidents.interrupt_incident(
            incident, "evacuate", isolate=True, evacuate=True
        )
        self.assertEqual(interrupted["current_stage"], "recovery")
        self.assertTrue(interrupted["propagation_stopped"])
        self.assertTrue(interrupted["isolated"])
        self.assertTrue(interrupted["evacuated"])

    def test_second_major_incident_queues(self) -> None:
        result = self.run_id("S136")["prompt3_evidence"]["incident_probe"]
        self.assertFalse(result["second_major_started"])
        self.assertTrue(result["scheduling"][1]["queued"])

    def test_minor_warning_can_queue_without_second_major_crisis(self) -> None:
        result = self.run_id("S165")["prompt3_evidence"]["incident_probe"]
        self.assertEqual(len(result["queued"]), 1)
        self.assertFalse(result["queued"][0]["major"])
        self.assertLessEqual(result["major_live_count"], 1)

    def test_incident_recovery_is_saved(self) -> None:
        result = self.run_id("S140")["prompt3_evidence"]["incident_probe"]
        self.assertEqual(result["incident"]["status"], "resolved")
        self.assertIn("reward_claim_id", result["incident"])
        self.assertTrue(result["save_roundtrip_equal"])

    def test_incident_recovery_reward_is_idempotent(self) -> None:
        incident = incidents.create_incident(
            self.config, "test:reward", "equipment_breakdown"
        )
        incident = incidents.advance_incident(incident)
        incident = incidents.interrupt_incident(incident, "repair")
        first = incidents.recover_incident(incident)
        second = incidents.recover_incident(first)
        self.assertEqual(first, second)
        self.assertEqual(
            first["transaction_ids"].count("incident:test:reward:resolved"), 1
        )

    def test_every_incident_stage_roundtrips(self) -> None:
        evidence = self.run_id("S141")["prompt3_evidence"]
        self.assertEqual(len(evidence["incident_stage_snapshots"]), 4)
        self.assertTrue(evidence["incident_stage_roundtrip"])

    def test_cascade_validation_bounds_three_unique_systems(self) -> None:
        valid = incidents.validate_cascade(["Air", "Power", "Water"], 3)
        invalid = incidents.validate_cascade(["Air", "Power", "Water", "Structure"], 3)
        self.assertTrue(valid["bounded"])
        self.assertFalse(valid["duplicate_system"])
        self.assertFalse(invalid["bounded"])

    def test_storm_profiles_stop_at_expected_system(self) -> None:
        prepared = self.run_id("S142")["storm"]
        partial = self.run_id("S143")["storm"]
        unprepared = self.run_id("S144")["storm"]
        self.assertEqual(prepared["cascade"], ["Air"])
        self.assertEqual(partial["cascade"], ["Air", "Power"])
        self.assertEqual(unprepared["cascade"], ["Air", "Power", "Water"])

    def test_extended_storm_neglect_is_real_failure(self) -> None:
        result = self.run_id("S145")
        self.assertEqual(result["outcome_class"], "SHELTER_FAILURE")
        self.assertFalse(result["storm"]["recoverable"])
        self.assertGreaterEqual(result["storm"]["affected_system_count"], 3)

    def test_highball_is_deadline_timing_not_free_weekly_value(self) -> None:
        useful = self.run_id("S151")["highball"]
        wasteful = self.run_id("S152")["highball"]
        self.assertGreater(useful["work_saved"], 0.0)
        self.assertLessEqual(wasteful["net_week_work_value"], useful["net_week_work_value"])
        self.assertGreater(wasteful["costs"]["charge_cost"], 0.0)

    def test_highball_promise_repayment_and_breach_differ(self) -> None:
        kept = self.run_id("S153")["highball"]
        broken = self.run_id("S154")["highball"]
        self.assertEqual(kept["promise"], "kept")
        self.assertEqual(broken["promise"], "breached")
        self.assertFalse(kept["refuses_next_highball"])
        self.assertTrue(broken["refuses_next_highball"])

    def test_consecutive_highball_escalates_strain_and_recovery(self) -> None:
        one = self.run_id("S153")["highball"]
        two_result = self.run_id("S155")
        two = two_result["highball"]
        self.assertGreater(two["strain"], one["strain"])
        self.assertGreater(two["inspection_work"], one["inspection_work"])
        self.assertEqual(two_result["outcome_class"], "RECOVER_FIRST")

    def test_highball_rejects_critical_medical_restriction(self) -> None:
        result = self.run_id("S156")
        self.assertFalse(result["highball"]["eligible"])
        self.assertEqual(result["highball"]["work_saved"], 0.0)
        self.assertIn("medically restricted", result["highball"]["rejection_reason"])

    def test_low_condition_equipment_adds_declared_strain(self) -> None:
        normal = self.run_id("S153")["highball"]
        low = self.run_id("S157")["highball"]
        self.assertGreater(low["strain"], normal["strain"])
        self.assertGreaterEqual(low["inspection_work"], normal["inspection_work"])
        self.assertFalse(low["hidden_random_risk"])

    def test_highball_commitment_is_idempotent(self) -> None:
        probe = self.run_id("S159")["prompt3_evidence"]["highball_duplicate_probe"]
        self.assertTrue(probe["duplicate_benefit_prevented"])
        self.assertTrue(probe["stocks_unchanged"])
        self.assertEqual(probe["cost_commit_count"], 1)


if __name__ == "__main__":
    unittest.main()
