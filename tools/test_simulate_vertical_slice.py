#!/usr/bin/env python3
"""Automated checks for the SIGNAL 45 slice feasibility model.

Run:  python3 -m unittest tools.test_simulate_vertical_slice -v
 or:  python3 tools/test_simulate_vertical_slice.py
"""

import unittest

from simulate_vertical_slice import simulate, REQUIRED_RUNS, main


class SliceFeasibility(unittest.TestCase):

    def test_all_required_scenarios_meet_milestones(self):
        for cfg in REQUIRED_RUNS:
            r = simulate(verbose=False, **cfg)
            self.assertEqual(r["missed"], [],
                             "milestones missed in %r: %s" % (cfg, r["missed"]))

    def test_competent_margins_at_least_15_percent(self):
        for route in ("east", "west"):
            r = simulate(route=route, scenario="competent", verbose=False)
            self.assertGreaterEqual(
                r["margin"], 0.15,
                "%s competent margin %.1f%% below 15%% target" % (route, r["margin"] * 100))

    def test_exclusive_choice_holds(self):
        r = simulate(route="east", scenario="competent", both_wings=True, verbose=False)
        self.assertTrue(r["missed"],
                        "both wings completed pre-storm: exclusivity is broken")

    def test_disruption_scenarios_survive(self):
        for cfg in (dict(route="east", scenario="mistake"),
                    dict(route="west", scenario="mistake"),
                    dict(route="east", scenario="absence"),
                    dict(route="east", scenario="interrupted")):
            r = simulate(verbose=False, **cfg)
            self.assertEqual(r["missed"], [], "slice does not survive %r" % cfg)
            self.assertGreaterEqual(r["margin"], 0.0,
                                    "negative margin under %r" % cfg)

    def test_deterministic(self):
        a = simulate(route="west", scenario="competent", verbose=False)
        b = simulate(route="west", scenario="competent", verbose=False)
        self.assertEqual(a["report"], b["report"])

    def test_delegated_and_active_share_world_outcomes(self):
        d = simulate(route="east", scenario="competent", night_mode="delegated", verbose=False)
        a = simulate(route="east", scenario="competent", night_mode="active", verbose=False)
        self.assertEqual(d["done_days"], a["done_days"],
                         "night mode changed world outcomes — modes must share results")
        self.assertGreater(a["minutes"], d["minutes"])

    def test_session_time_budgets(self):
        for route in ("east", "west"):
            d = simulate(route=route, scenario="competent", night_mode="delegated", verbose=False)
            a = simulate(route=route, scenario="competent", night_mode="active", verbose=False)
            self.assertTrue(60 <= d["minutes"] <= 100,
                            "delegated week %.1f min outside 60-100" % d["minutes"])
            self.assertTrue(60 <= a["minutes"] <= 105,
                            "active week %.1f min outside 60-105" % a["minutes"])
            # per-day averages inside the phase-model bands
            self.assertLessEqual(d["minutes"] / 7.0, 12.0)
            self.assertLessEqual(a["minutes"] / 7.0, 16.0)

    def test_cli_all_passes(self):
        self.assertEqual(main(["--all"]), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
