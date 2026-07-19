from __future__ import annotations

import copy
import unittest

from tools.feasibility import model
from tools.feasibility.validate_data import validate_model, validate_scenarios


class CoreModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config, cls.scenarios = model.load_inputs()

    def scenario(self, scenario_id: str) -> dict:
        return model.scenario_by_id(self.scenarios, scenario_id)

    def fresh_state(self, route: str = "east", optional: str | None = None):
        options = {"route": route, "signal": "drainage"}
        if optional:
            options["optional_project"] = optional
        selected, _ = model._selected_projects(self.config, route, options)
        return options, selected, model._initial_state(self.config, selected, {})

    def test_configuration_validation_accepts_canonical_data(self) -> None:
        self.assertEqual(validate_model(self.config), [])

    def test_configuration_validation_rejects_extra_primary_stock(self) -> None:
        changed = copy.deepcopy(self.config)
        changed["stocks"]["Fuel"] = copy.deepcopy(changed["stocks"]["Charge"])
        errors = validate_model(changed)
        self.assertEqual(len(errors), 1)
        self.assertIn("exactly the five locked stocks", errors[0])

    def test_scenario_validation_rejects_missing_required_case(self) -> None:
        scenario_data = {
            "schema_version": 1,
            "scenarios": [
                copy.deepcopy(item) for item in self.scenarios if item["id"] != "S64"
            ],
        }
        replacement = copy.deepcopy(self.scenarios[-1])
        replacement["id"] = "S177"
        replacement["name"] = "validation-only replacement"
        scenario_data["scenarios"].append(replacement)
        errors = validate_scenarios(scenario_data, self.config)
        self.assertEqual(len(errors), 1)
        self.assertIn("S64", errors[0])

    def test_scenario_validation_rejects_label_only_duplicate(self) -> None:
        changed = {"schema_version": 1, "scenarios": copy.deepcopy(self.scenarios)}
        original = changed["scenarios"][0]
        duplicate = changed["scenarios"][-1]
        duplicate["route"] = original["route"]
        duplicate["signal"] = original["signal"]
        duplicate["options"] = copy.deepcopy(original["options"])
        duplicate["options"]["prompt3_case"] = "label_only_duplicate"
        errors = validate_scenarios(changed, self.config)
        self.assertEqual(len(errors), 1)
        self.assertIn("exact input duplicate", errors[0])

    def test_repeated_run_is_deterministic(self) -> None:
        first = model.simulate_scenario(self.config, self.scenario("S01"))
        second = model.simulate_scenario(self.config, self.scenario("S01"))
        self.assertEqual(first, second)

    def test_base_work_capacity_uses_resident_data(self) -> None:
        result = model.calculate_resident_capacity(self.config, "Ash")
        self.assertEqual(result, self.config["residents"]["Ash"]["base_capacity"])

    def test_condition_reduction_changes_capacity(self) -> None:
        healthy = model.calculate_resident_capacity(self.config, "Ash")
        impaired = model.calculate_resident_capacity(
            self.config,
            "Ash",
            {"health": "impaired", "hunger": "restricted", "fatigue": "tired", "stress": "high"},
        )
        self.assertLess(impaired, healthy)
        self.assertGreater(impaired, 0.0)

    def test_critical_resident_has_zero_project_work(self) -> None:
        profile = model.calculate_resident_work_profile(
            self.config,
            "Maren",
            {"health": "critical", "hunger": "prolonged", "fatigue": "collapse_risk", "stress": "acute"},
        )
        self.assertEqual(profile["productive_capacity"], 0.0)
        self.assertFalse(profile["assignment_eligible"])
        self.assertTrue(profile["emergency_self_action_available"])

    def test_unavailable_resident_has_no_capacity(self) -> None:
        result = model.calculate_resident_capacity(self.config, "Teo", availability=0.0)
        self.assertEqual(result, 0.0)

    def test_parallel_worker_limit_and_diminishing_return(self) -> None:
        two_workers = model.multi_worker_output(self.config, "standard", [10.0, 10.0])
        three_workers = model.multi_worker_output(self.config, "standard", [10.0, 10.0, 10.0])
        self.assertEqual(two_workers, three_workers)
        self.assertLess(two_workers, 20.0)

    def test_missing_dependency_blocks_dependent_projects(self) -> None:
        scenario = copy.deepcopy(self.scenario("S01"))
        scenario["id"] = "TEST_DEPENDENCY"
        scenario["options"]["omit_project"] = "east_reclaim"
        result = model.simulate_scenario(self.config, scenario)
        self.assertFalse(result["slice_proof_complete"])
        self.assertIn("east_utility_connection", result["final"]["incomplete_required_projects"])

    def test_partial_project_progress_survives_interruption(self) -> None:
        options, selected, state = self.fresh_state()
        for project_id in ["platform_lamp_install", "triage_cot_install", "route_survey"]:
            state.completed_projects.add(project_id)
            state.projects[project_id].status = "completed"
            state.projects[project_id].remaining_work = 0.0
        state.day = 2
        used, log = model._allocate_project_work(state, self.config, selected, 5.0, options)
        progress = state.projects["east_reclaim"]
        restored = model.SimulationState.from_json(state.to_json())
        self.assertEqual(used, 5.0)
        self.assertEqual(log[0]["project"], "east_reclaim")
        self.assertEqual(progress.status, "active")
        self.assertEqual(restored.projects["east_reclaim"].remaining_work, progress.remaining_work)

    def test_material_reservation_is_committed_once(self) -> None:
        _, selected, state = self.fresh_state()
        project = selected["platform_lamp_install"]
        progress = state.projects[project["id"]]
        before = state.stocks["Materials"]
        self.assertEqual(model._reserve_project(state, self.config, project, progress), True)
        after_first = state.stocks["Materials"]
        self.assertEqual(model._reserve_project(state, self.config, project, progress), True)
        self.assertEqual(after_first, before - project["materials"])
        self.assertEqual(state.stocks["Materials"], after_first)

    def test_cancellation_refunds_once(self) -> None:
        _, selected, state = self.fresh_state(optional="platform_lighting_upgrade")
        project = selected["platform_lighting_upgrade"]
        progress = state.projects[project["id"]]
        model._reserve_project(state, self.config, project, progress)
        first = model.cancel_project(state, self.config, selected, project["id"])
        after_first = state.stocks["Materials"]
        second = model.cancel_project(state, self.config, selected, project["id"])
        self.assertGreater(first, 0.0)
        self.assertEqual(second, 0.0)
        self.assertEqual(state.stocks["Materials"], after_first)

    def test_commit_once_does_not_repeat_mutation(self) -> None:
        _, _, state = self.fresh_state()
        calls: list[str] = []
        first = model.commit_once(state, "test:commit", lambda: calls.append("called"))
        second = model.commit_once(state, "test:commit", lambda: calls.append("called"))
        self.assertEqual((first, second), (True, False))
        self.assertEqual(calls, ["called"])

    def test_scenario_output_separates_optional_and_required_work(self) -> None:
        baseline = model.simulate_scenario(self.config, self.scenario("S01"))
        optional = model.simulate_scenario(self.config, self.scenario("S11"))
        self.assertEqual(
            sum(day["work"]["optional_project_work"] for day in baseline["days"]),
            0.0,
        )
        self.assertGreater(
            sum(day["work"]["optional_project_work"] for day in optional["days"]),
            0.0,
        )
        self.assertGreater(
            sum(day["work"]["mandatory_route_project_work"] for day in baseline["days"]),
            0.0,
        )


if __name__ == "__main__":
    unittest.main()
