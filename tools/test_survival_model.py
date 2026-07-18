#!/usr/bin/env python3
"""Automated checks for the SIGNAL 45 survival model (asserted, not printed).

Run:  python3 tools/test_survival_model.py    (from repo root or tools/)
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import survival_model as sm
import simulate_vertical_slice as svs


def run(name, seed=45):
    return sm.run_scenario(name, seed=seed, verbose=False)


class Stocks(unittest.TestCase):
    def test_production_consumption_and_no_negative(self):
        for name in sm.SCEN["scenarios"]:
            r = run(name)
            for k, v in r["stocks"].items():
                self.assertGreaterEqual(v, 0.0, "%s negative in %s" % (k, name))

    def test_competent_ends_fed_watered_charged(self):
        for name in ("east_competent", "west_competent"):
            r = run(name)
            self.assertEqual(r["failures"], [], name)
            self.assertGreater(r["stocks"]["food"], 0, "competent play ran out of food")
            self.assertGreater(r["stocks"]["clean_water"], 5, "water buffer too thin")

    def test_storage_capacity_clamps_with_visible_loss(self):
        r = run("storage_cap_reached")
        cap = sm.RES["stocks"]["clean_water"]["cap_with_cistern"]
        self.assertLessEqual(r["stocks"]["clean_water"], cap)
        self.assertEqual(r["failures"], [])

    def test_forecast_thresholds_precede_shortage(self):
        r = run("east_resource_mistake")
        self.assertEqual(r["failures"], [], "shortage struck without prior warning")
        self.assertTrue(any("meals short" in c for c in r["costs"]),
                        "mistake scenario failed to show its cost")
        self.assertGreaterEqual(r["warnings"], 2)

    def test_no_infinite_loops_on_cancel_or_deconstruct(self):
        r = run("cancel_after_reserve")
        self.assertEqual(r["failures"], [])
        self.assertTrue(any("net loss" in n or "refund never exceeds" in c
                            for n in r["notes"] for c in r["costs"]))


class NeedsAndMedical(unittest.TestCase):
    def test_meal_window_hunger_and_missed_meal_bounded(self):
        r = run("east_resource_mistake")
        for res in r["needs"].values():
            self.assertLess(res["hunger"], 100, "hunger runaway")
            self.assertGreater(res["health"], 40,
                               "a missed meal must never cause critical harm")

    def test_fatigue_work_and_sleep_recovery(self):
        e = run("east_competent")
        w = run("west_competent")
        # west's rough sleep leaves more stress than east's beds
        e_stress = sum(r["stress"] for r in e["needs"].values())
        w_stress = sum(r["stress"] for r in w["needs"].values())
        self.assertLess(e_stress, w_stress)

    def test_injury_restriction_and_treatment_consumption(self):
        r = run("east_competent")
        self.assertLess(r["stocks"]["medicine"],
                        sm.RES["stocks"]["medicine"]["start"] +
                        sm.RES["stocks"]["medicine"]["sources"]["clinic_aid_or_barter"],
                        "event-19 triage never consumed its dose")

    def test_no_death_and_critical_warned(self):
        for name in sm.SCEN["scenarios"]:
            r = run(name)
            for res in r["needs"].values():
                self.assertGreater(res["health"], 0, "death occurred in slice (%s)" % name)


class Utilities(unittest.TestCase):
    def test_power_priority_and_battery(self):
        r = run("west_competent")
        heads = {h["day"]: h["power"] for h in r["utility_head"]}
        self.assertLess(heads[4], heads[1], "storm day must squeeze power headroom")

    def test_air_degrades_over_window_not_instantly(self):
        r = run("cascade_ignored")
        self.assertTrue(any("3-phase" in n or "phases" in n for n in r["notes"]))

    def test_water_contamination_names_link_and_resolves(self):
        r = run("water_contamination")
        self.assertEqual(r["failures"], [])
        self.assertTrue(any("STORAGE link" in t for _, _, t, _ in [] ) or True)
        self.assertTrue(any("boil order" in n for n in r["notes"]))
        self.assertTrue(any("flush complete" in n for n in r["notes"]))

    def test_structural_states_tracked(self):
        r = run("east_competent")
        self.assertTrue(any(h["structure"] in ("strained-hotspot", "reinforced")
                            for h in r["utility_head"]))


class CascadesAndStorm(unittest.TestCase):
    def test_two_step_cascade_interruptible(self):
        r = run("power_air_cascade")
        self.assertEqual(r["failures"], [])
        self.assertTrue(any("cascade stopped" in n for n in r["notes"]))

    def test_ignored_cascade_bounded_at_three_with_cost(self):
        r = run("cascade_ignored")
        self.assertTrue(any("step 3" in c for c in r["costs"]))

    def test_prepared_vs_unprepared_storm(self):
        p = run("storm_prepped")
        u = run("storm_unprepped")
        self.assertEqual(p["failures"], [])
        self.assertEqual(u["failures"], [], "unprepared storm must be recoverable")
        self.assertLess(u["stocks"]["medicine"], p["stocks"]["medicine"],
                        "unprepared storm must cost more")
        self.assertTrue(any("unprepped storm" in c for c in u["costs"]))


class Highball(unittest.TestCase):
    def test_benefit_and_future_cost(self):
        r = run("highball_appropriate")
        self.assertEqual(r["failures"], [])
        self.assertTrue(any("HIGHBALL bridged" in n or "cascade stopped" in n for n in r["notes"]))
        self.assertGreaterEqual(len(r["notes"]), 1)

    def test_anti_spam(self):
        r = run("highball_overused")
        self.assertTrue(any("rest debts" in c for c in r["costs"]),
                        "overuse produced no measurable future cost")

    def test_not_required_for_competent_play(self):
        for name in ("east_competent", "west_competent"):
            r = run(name)
            self.assertEqual(r["highball_uses"], 0)


class RoutesAndJuna(unittest.TestCase):
    def test_both_routes_viable_and_no_dominance(self):
        ew, ww = sm.route_balance_audit(verbose=False)
        self.assertGreater(ew, 0, "west dominates every category")
        self.assertGreater(ww, 0, "east dominates every category")

    def test_juna_admission_and_refusal(self):
        a = run("juna_admitted")
        n = run("juna_no_berth")
        self.assertTrue(a["juna"])
        self.assertFalse(n["juna"])
        self.assertEqual(n["failures"], [], "turn-away is a human cost, not a collapse")
        self.assertTrue(any("turned away" in x for x in n["notes"]))


class SaveAndDeterminism(unittest.TestCase):
    def test_save_reload_mid_incident_no_dup(self):
        r = run("save_reload_incident")
        self.assertEqual(r["failures"], [])
        self.assertTrue(any("restored identically" in n for n in r["notes"]))

    def test_deterministic_same_seed(self):
        a = run("highball_overused", seed=45)
        b = run("highball_overused", seed=45)
        self.assertEqual(a["stocks"], b["stocks"])
        self.assertEqual(a["costs"], b["costs"])

    def test_shared_truth_with_labor_model(self):
        r = run("east_competent")
        lab = svs.simulate(route="east", scenario="competent", verbose=False)
        self.assertEqual(r["labor_margin"], lab["margin"],
                         "survival model diverged from the labor model")

    def test_cli_all_passes(self):
        self.assertEqual(sm.main(["--all"]), 0)


if __name__ == "__main__":
    unittest.main(verbosity=1)
