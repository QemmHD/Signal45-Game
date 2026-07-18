from __future__ import annotations

import unittest

from tools.feasibility import model


class SaveAndTransactionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config, cls.scenarios = model.load_inputs()
        options = {"route": "east", "signal": "drainage"}
        selected, _ = model._selected_projects(cls.config, "east", options)
        cls.base_state = model._initial_state(cls.config, selected, {})

    def run_id(self, scenario_id: str) -> dict:
        return model.simulate_scenario(
            self.config, model.scenario_by_id(self.scenarios, scenario_id)
        )

    def test_phase_save_roundtrip(self) -> None:
        state = model.SimulationState.from_json(self.base_state.to_json())
        state.phase = "graymorn"
        restored = model.SimulationState.from_json(state.to_json())
        self.assertEqual(restored.phase, "graymorn")
        self.assertEqual(restored.to_json(), state.to_json())

    def test_partial_construction_save_probe(self) -> None:
        probe = self.run_id("S45")["save_probe"]
        self.assertEqual(probe["probe"], "partial_construction")
        self.assertEqual(probe["roundtrip_equal"], True)

    def test_material_reservation_save_probe(self) -> None:
        probe = self.run_id("S46")["save_probe"]
        self.assertEqual(probe["probe"], "material_reservation")
        self.assertEqual(probe["passed"], True)

    def test_incident_stage_save_probe(self) -> None:
        probe = self.run_id("S47")["save_probe"]
        self.assertEqual(probe["probe"], "incident_stage")
        self.assertEqual(probe["passed"], True)

    def test_expedition_save_probes(self) -> None:
        for scenario_id, probe_name in [("S50", "expedition_node"), ("S51", "expedition_reward")]:
            probe = self.run_id(scenario_id)["save_probe"]
            self.assertEqual(probe["probe"], probe_name)
            self.assertEqual(probe["passed"], True)

    def test_admission_save_probes(self) -> None:
        for scenario_id, probe_name in [("S52", "before_admission"), ("S53", "after_admission")]:
            probe = self.run_id(scenario_id)["save_probe"]
            self.assertEqual(probe["probe"], probe_name)
            self.assertEqual(probe["passed"], True)

    def test_treatment_save_probe(self) -> None:
        probe = self.run_id("S54")["save_probe"]
        self.assertEqual(probe["probe"], "treatment")
        self.assertEqual(probe["passed"], True)

    def test_highball_pre_and_post_commit_saves(self) -> None:
        before = self.run_id("S48")["save_probe"]
        after = self.run_id("S49")["save_probe"]
        self.assertEqual(before["passed"], True)
        self.assertEqual(after["passed"], True)
        self.assertNotEqual(before["probe"], after["probe"])

    def test_reward_is_idempotent_across_reload(self) -> None:
        state = model.SimulationState.from_json(self.base_state.to_json())
        first = model.grant_reward_once(
            state, self.config, "test:reward", stocks={"Materials": 3.0}
        )
        saved = state.to_json()
        restored = model.SimulationState.from_json(saved)
        amount = restored.stocks["Materials"]
        second = model.grant_reward_once(
            restored, self.config, "test:reward", stocks={"Materials": 3.0}
        )
        self.assertEqual(first, True)
        self.assertEqual(second, False)
        self.assertEqual(restored.stocks["Materials"], amount)

    def test_closed_app_causes_no_advancement(self) -> None:
        state = model.SimulationState.from_json(self.base_state.to_json())
        before = state.to_json()
        restored = model.background_without_advancement(state, elapsed_seconds=604800)
        self.assertEqual(restored.to_json(), before)

    def test_every_save_scenario_blocks_duplicate_rewards(self) -> None:
        for number in range(45, 55):
            probe = self.run_id(f"S{number}")["save_probe"]
            self.assertEqual(probe["duplicate_reward_prevented"], True, f"S{number}")
            self.assertEqual(probe["offline_unchanged"], True, f"S{number}")

    def test_transaction_catalog_covers_irreversible_actions(self) -> None:
        ids = {transaction["id"] for transaction in self.config["transactions"]}
        expected = {
            "project_completion",
            "highball_confirmation",
            "signal_commitment",
            "expedition_irreversible_action",
            "trader_transaction",
            "juna_admission",
            "incident_escalation",
            "treatment_completion",
            "end_of_day_ledger",
        }
        self.assertEqual(expected - ids, set())


if __name__ == "__main__":
    unittest.main()
