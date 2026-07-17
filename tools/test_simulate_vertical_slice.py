#!/usr/bin/env python3
"""Automated checks for the SIGNAL 45 slice feasibility model.

Run:  cd tools && python3 -m unittest test_simulate_vertical_slice -v
 or:  python3 tools/test_simulate_vertical_slice.py   (from repo root)
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from simulate_vertical_slice import (simulate, REQUIRED_RUNS, main,
                                     absence_sweep, efficiency_sweep)


class SliceFeasibility(unittest.TestCase):

    def test_required_scenarios_meet_hard_milestones(self):
        for cfg in REQUIRED_RUNS:
            r = simulate(verbose=False, **cfg)
            self.assertEqual(r["missed"], [],
                             "hard milestones missed in %r: %s" % (cfg, r["missed"]))

    def test_competent_margins_and_beats(self):
        for route in ("east", "west"):
            r = simulate(route=route, scenario="competent", verbose=False)
            self.assertGreaterEqual(r["margin"], 0.15,
                                    "%s competent margin %.1f%% below 15%%" % (route, r["margin"] * 100))
            self.assertEqual(r["missed_soft"], [],
                             "%s competent play misses soft milestones" % route)
            # dramaturgy beats hold in competent play
            self.assertNotIn("Beat drift", r["report"],
                             "%s competent run drifts from beat targets" % route)
            trunk = "trunk_e" if route == "east" else "trunk_w"
            self.assertLessEqual(r["done_days"][trunk], 4, "trunk misses the mid-storm beat")

    def test_exclusive_choice_holds(self):
        r = simulate(route="east", scenario="competent", both_wings=True, verbose=False)
        second = r["done_days"].get("drain_west", 0)
        self.assertFalse(second and second <= 3,
                         "second wing opened pre-storm: exclusivity broken")

    def test_disruption_scenarios_survive(self):
        for cfg in (dict(route="east", scenario="mistake"),
                    dict(route="west", scenario="mistake"),
                    dict(route="east", scenario="absence"),
                    dict(route="east", scenario="interrupted"),
                    dict(route="east", scenario="prep_last")):
            r = simulate(verbose=False, **cfg)
            self.assertEqual(r["missed"], [], "slice does not survive %r" % cfg)
            self.assertGreaterEqual(r["margin"], 0.0, "negative margin under %r" % cfg)

    def test_absence_sweep_worst_cell_survives(self):
        _route, _who, _day, worst = absence_sweep(verbose=False)
        self.assertEqual(worst["missed"], [],
                         "worst absence cell breaks a hard milestone")

    def test_efficiency_sensitivity_floor(self):
        for eff, route, _margin, hard, _soft in efficiency_sweep(verbose=False):
            if eff >= 0.80:
                self.assertEqual(hard, [],
                                 "hard milestones fail at efficiency %.3f (%s)" % (eff, route))

    def test_neglecting_essentials_is_not_profitable(self):
        base = simulate(route="east", scenario="competent", verbose=False)
        cheese = simulate(route="east", scenario="neglect", verbose=False)
        self.assertLess(cheese["margin"], base["margin"],
                        "suspending essential duties must be net-negative")

    def test_deterministic(self):
        a = simulate(route="west", scenario="competent", verbose=False)
        b = simulate(route="west", scenario="competent", verbose=False)
        self.assertEqual(a["report"], b["report"])

    def test_delegated_and_active_share_world_outcomes(self):
        d = simulate(route="east", scenario="competent", night_mode="delegated", verbose=False)
        a = simulate(route="east", scenario="competent", night_mode="active", verbose=False)
        self.assertEqual(d["done_days"], a["done_days"],
                         "night mode changed world outcomes")
        self.assertGreater(a["minutes"], d["minutes"])

    def test_session_time_budgets(self):
        for route in ("east", "west"):
            d = simulate(route=route, scenario="competent", night_mode="delegated", verbose=False)
            a = simulate(route=route, scenario="competent", night_mode="active", verbose=False)
            self.assertTrue(60 <= d["minutes"] <= 100,
                            "delegated week %.1f min outside 60-100" % d["minutes"])
            self.assertTrue(60 <= a["minutes"] <= 100,
                            "active week %.1f min outside the 07-section-14 gate" % a["minutes"])
            self.assertLessEqual(d["minutes"] / 7.0, 12.0)
            self.assertLessEqual(a["minutes"] / 7.0, 16.0)
            # active runs stay a minority of playtime (<= ~1/3)
            self.assertLessEqual(a["active_minutes"] / a["minutes"], 1.0 / 3.0)

    def test_runs_only_on_scheduled_nights(self):
        r = simulate(route="east", scenario="competent", verbose=False)
        self.assertEqual(sorted(r["runs"]), [2, 3, 5])

    def test_cli_all_passes(self):
        self.assertEqual(main(["--all"]), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
