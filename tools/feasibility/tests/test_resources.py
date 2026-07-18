from __future__ import annotations

import unittest

from tools.feasibility import model


class ResourceAndUtilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config, cls.scenarios = model.load_inputs()
        options = {"route": "east", "signal": "drainage"}
        cls.selected, _ = model._selected_projects(cls.config, "east", options)

    def fresh_state(self):
        return model._initial_state(self.config, self.selected, {})

    def test_food_consumption_occurs_at_issue_boundary(self) -> None:
        state = self.fresh_state()
        amount = 4 * self.config["stocks"]["Food"]["normal_per_resident_day"]
        shortfall = model.consume_stock(state, "Food", amount, "ration")
        self.assertEqual(shortfall, 0.0)
        self.assertEqual(state.stocks["Food"], self.config["stocks"]["Food"]["start"] - amount)

    def test_water_consumption_occurs_at_issue_boundary(self) -> None:
        state = self.fresh_state()
        amount = 4 * self.config["stocks"]["Clean Water"]["normal_per_resident_day"]
        model.consume_stock(state, "Clean Water", amount, "water issue")
        self.assertEqual(state.stocks["Clean Water"], self.config["stocks"]["Clean Water"]["start"] - amount)

    def test_medicine_consumption_tracks_treatment(self) -> None:
        state = self.fresh_state()
        amount = self.config["stocks"]["Medicine"]["minor_injury_use"]
        model.consume_stock(state, "Medicine", amount, "minor treatment")
        self.assertEqual(state.stocks["Medicine"], self.config["stocks"]["Medicine"]["start"] - amount)

    def test_consumption_never_produces_negative_stock(self) -> None:
        state = self.fresh_state()
        shortfall = model.consume_stock(state, "Food", 999.0, "adversarial drain")
        self.assertEqual(state.stocks["Food"], 0.0)
        self.assertGreater(shortfall, 0.0)
        self.assertIn("adversarial drain", state.failures[0])

    def test_charge_discharges_during_storm(self) -> None:
        scenario = model.scenario_by_id(self.scenarios, "S22")
        result = model.simulate_scenario(self.config, scenario)
        self.assertGreater(result["storm"]["charge_use"], 0.0)
        self.assertLess(result["final"]["stocks"]["Charge"], self.config["stocks"]["Charge"]["start"])

    def test_power_shortfall_names_shutdown_and_next_risk(self) -> None:
        result = model.calculate_power(
            self.config,
            {"triage_cot_install", "workshop_install", "comfort_lighting"},
            storm_affected_systems=3,
            demand_multiplier=1.2,
        )
        self.assertLess(result["headroom"], 0.0)
        self.assertGreater(len(result["shutdown_order_if_uncovered"]), 0)
        self.assertEqual(result["next_endangered"], "water_pumping")

    def test_air_degradation_identifies_filter_link(self) -> None:
        result = model.calculate_air(
            self.config,
            set(),
            5,
            storm_profile="unprepared",
            filter_condition_multiplier=0.85,
        )
        self.assertLess(result["headroom"], 0.0)
        self.assertIn(result["state"], {"degraded", "exposure", "evacuate"})
        self.assertEqual(result["failing_link"], "filter condition")

    def test_water_impairment_names_failing_links(self) -> None:
        normal = model.calculate_water_utility(self.config, "west", {"west_water_treatment"}, 4)
        impaired = model.calculate_water_utility(
            self.config, "west", {"west_water_treatment"}, 4, impaired=True
        )
        self.assertLess(impaired["delivery"], normal["delivery"])
        self.assertEqual(impaired["contamination_state"], "suspect")
        self.assertIn("pump", impaired["failing_link"])

    def test_structure_closure_removes_access(self) -> None:
        result = model.calculate_structure("east", {"east_reclaim"}, force_closed=True)
        self.assertEqual(result["state"], "closed")
        self.assertFalse(result["access_open"])

    def test_forecast_threshold_changes_plain_status(self) -> None:
        stock = self.config["stocks"]["Clean Water"]
        critical = model.forecast_stock(self.config, "Clean Water", stock["minimum_viable_reserve"] - 1)
        comfortable = model.forecast_stock(self.config, "Clean Water", stock["comfortable_reserve"])
        self.assertEqual(critical["status"], "critical")
        self.assertEqual(comfortable["status"], "comfortable")


if __name__ == "__main__":
    unittest.main()
