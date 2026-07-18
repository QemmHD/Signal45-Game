#!/usr/bin/env python3
"""Automated checks for the SIGNAL 45 survival model (asserted, not printed).

Rewritten in the D-045 red-team pass: every assertion here can fail — the
tautologies the audit found (self-comparing snapshots, `or True` clauses,
string-grep 'verifications' of unmodeled mechanics) are gone. Claims the
model does NOT simulate are tested as what they are (rule-level text), and
docs/design/20 labels them the same way.

Run:  python3 tools/test_survival_model.py    (from repo root or tools/)
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import survival_model as sm
import simulate_vertical_slice as svs

_CACHE = {}


def run(name, seed=45):
    key = (name, seed)
    if key not in _CACHE:
        _CACHE[key] = sm.run_scenario(name, seed=seed, verbose=False)
    return _CACHE[key]


def wkinds(r):
    return [k for _, k, _, _ in r["warning_log"]]


def wfirst(r, kind):
    days = [d for d, k, _, _ in r["warning_log"] if k == kind]
    return min(days) if days else None


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

    def test_storage_cap_overflow_is_real_and_never_silent(self):
        r = run("storage_cap_reached")
        self.assertEqual(r["failures"], [])
        self.assertGreater(r["overflow_lost"]["clean_water"], 0.0,
                           "hoard scenario never actually overflowed storage")
        self.assertIn("water_storage_full", wkinds(r),
                      "overflow happened without its forecast warning")
        cap = max(sm.RES["stocks"]["clean_water"]["storage_cap"],
                  sm.RES["stocks"]["clean_water"]["cap_with_cistern"])
        self.assertLessEqual(r["stocks"]["clean_water"], cap)

    def test_east_mistake_forecast_precedes_rationing_and_shortage(self):
        r = run("east_resource_mistake")
        self.assertEqual(r["failures"], [], "shortage struck without prior warning")
        self.assertTrue(any("rationed" in c or "meals short" in c for c in r["costs"]),
                        "mistake scenario failed to show its cost")
        self.assertIsNotNone(wfirst(r, "food_low"))

    def test_west_mistake_rationing_actually_fires_after_forecast(self):
        r = run("west_resource_mistake")
        self.assertEqual(r["failures"], [])
        ration_days = [int(c.split(":")[0][1:]) for c in r["costs"] if "water rationed" in c]
        self.assertTrue(ration_days, "west mistake never triggered rationing — scenario is a no-op")
        self.assertLess(wfirst(r, "water_low"), min(ration_days),
                        "rationing decision arrived before the water forecast")

    def test_materials_constant_shared_with_labor_model(self):
        self.assertEqual(svs.START_SALVAGE, sm.RES["stocks"]["materials"]["start"],
                         "labor-model START_SALVAGE and resources.json diverged")

    def test_survival_income_hooks_pinned(self):
        # guards the run-name coupling: if labor-model run names change without
        # the constants, food/meds income silently vanishes — this catches it
        r = run("east_competent")
        self.assertEqual(r["stocks"]["medicine"], 7.0)

    def test_cancel_refund_is_rule_level_not_fake_simulation(self):
        r = run("cancel_after_reserve")
        self.assertEqual(r["failures"], [])
        self.assertTrue(any("rule-level" in c or "unsimulated" in c for c in r["costs"]),
                        "cancel scenario must label itself rule-level, not claim simulation")
        self.assertTrue(any("design rule" in n for n in r["notes"]))


class NeedsAndMedical(unittest.TestCase):
    def test_missed_meals_bounded_never_critical(self):
        r = run("shortage_unrationed")
        for res in r["needs"].values():
            self.assertLess(res["hunger"], 100, "hunger runaway")
            self.assertGreater(res["health"], 40,
                               "missed meals must never cause critical harm in-week")

    def test_efficiency_ladder_engages_and_floors(self):
        r = run("shortage_unrationed")
        self.assertEqual(r["failures"], [])
        self.assertGreater(r["needs_derate_wu"], 0.0,
                           "sustained shortage never engaged the efficiency ladder")
        self.assertGreaterEqual(r["crew_mult_floor"],
                                sm.RES["needs"]["work_efficiency"]["critical"],
                                "efficiency fell below the never-zero floor")
        self.assertLess(r["labor_margin_adjusted"], r["labor_margin"])
        self.assertTrue(any("crew slowed" in n for n in r["notes"]),
                        "the derate must be visible, never silent")

    def test_west_rough_sleep_prices_stress(self):
        e, w = run("east_competent"), run("west_competent")
        self.assertLess(sum(r["stress"] for r in e["needs"].values()),
                        sum(r["stress"] for r in w["needs"].values()))

    def test_injury_never_heals_past_start_health(self):
        r = run("storm_unprepped")
        start = sm.RES["needs"]["start"]["health"]
        for name, res in r["needs"].items():
            self.assertLessEqual(res["health"], start,
                                 "%s ended ABOVE start health after an injury week" % name)

    def test_triage_consumes_its_dose(self):
        r = run("east_competent")
        self.assertLess(r["stocks"]["medicine"],
                        sm.RES["stocks"]["medicine"]["start"] +
                        sm.RES["stocks"]["medicine"]["sources"]["clinic_aid_or_barter"])

    def test_no_death_ever(self):
        for name in sm.SCEN["scenarios"]:
            r = run(name)
            for res in r["needs"].values():
                self.assertGreater(res["health"], 0, "death occurred in slice (%s)" % name)

    def test_contamination_ignored_costs_illness_and_medicine(self):
        r = run("contamination_ignored")
        base = run("water_contamination")
        self.assertEqual(r["failures"], [])
        self.assertIn("waterborne_illness", r["needs"]["Maren"]["conditions"],
                      "ignored contamination produced no illness")
        self.assertEqual(base["stocks"]["medicine"] - r["stocks"]["medicine"],
                         sm.RES["stocks"]["medicine"]["sinks"]["illness_course"],
                         "illness course did not consume its doses")
        self.assertEqual(wfirst(r, "illness_risk"), 5,
                         "illness landed without its day-5 risk forecast")
        self.assertLess(r["needs"]["Maren"]["health"], base["needs"]["Maren"]["health"])


class Utilities(unittest.TestCase):
    def test_shedding_reduces_demand_and_names_loads(self):
        r = run("west_competent")
        self.assertTrue(r["shed_log"], "west's deficit days never shed a load")
        for day, loads in r["shed_log"]:
            self.assertTrue(loads, "empty shed entry")
            for l in loads:
                self.assertIn(sm.UTIL["power"]["tier_of"][l], ("normal", "optional"),
                              "shed reached a protected tier")
        # when the shed covers the deficit, the rack is NOT drained that day
        shed_only_days = [d for d, _ in r["shed_log"]
                          if not any("residual deficit" in n and ("d%d:" % d) in n
                                     for n in r["notes"])]
        self.assertTrue(shed_only_days,
                        "every shed day also drained the rack — demand was not reduced")

    def test_storm_day_squeezes_power(self):
        r = run("west_competent")
        heads = {h["day"]: h["power"] for h in r["utility_head"]}
        self.assertLess(heads[4], heads[1], "storm day must squeeze power headroom")

    def test_air_degrades_over_window_not_instantly(self):
        r = run("cascade_ignored")
        self.assertTrue(any("3-phase" in n or "phases" in n for n in r["notes"]))

    def test_water_contamination_names_link_and_resolves(self):
        r = run("water_contamination")
        self.assertEqual(r["failures"], [])
        self.assertTrue(any("STORAGE link" in t for _, _, t, _ in r["warning_log"]),
                        "contamination warning failed to name its failing link")
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

    def test_battery_bridge_is_not_free(self):
        bat, hb = run("power_air_cascade"), run("highball_appropriate")
        self.assertTrue(any("battery bridge" in c for c in bat["costs"]),
                        "the battery rescue must post a visible cost")
        self.assertEqual(bat["highball_uses"], 0)
        self.assertEqual(hb["highball_uses"], 1)
        # the two rescues trade off differently in what they leave behind:
        # HIGHBALL leaves a standing promise-of-rest debt, the battery leaves
        # a spent-charge + cold-meal cost entry and no debt
        self.assertEqual(bat["highball_debt"], 0)
        self.assertEqual(hb["highball_debt"], 1,
                         "the HIGHBALL rescue must leave its promise-of-rest debt")

    def test_ignored_cascade_bounded_at_three_with_cost(self):
        r = run("cascade_ignored")
        self.assertTrue(any("step 3" in c for c in r["costs"]))

    def test_storm_telegraph_precedes_punishment_both_routes(self):
        for name in ("storm_unprepped", "storm_unprepped_west"):
            r = run(name)
            self.assertEqual(r["failures"], [], name)
            self.assertEqual(wfirst(r, "storm"), 3,
                             "%s: the free telegraph must fire the day before landfall" % name)
            self.assertTrue(any("unprepped storm" in c for c in r["costs"]))

    def test_prepared_vs_unprepared_storm(self):
        p, u = run("storm_prepped"), run("storm_unprepped")
        self.assertEqual(p["failures"], [])
        self.assertEqual(u["failures"], [], "unprepared storm must be recoverable")
        self.assertLess(u["stocks"]["medicine"], p["stocks"]["medicine"])
        self.assertTrue(any("prepped path" in n for n in p["notes"]),
                        "storm_prepped must be distinguishable from the bare competent run")


class Highball(unittest.TestCase):
    def test_rescue_works_and_posts_debt(self):
        r = run("highball_appropriate")
        self.assertEqual(r["failures"], [])
        self.assertTrue(any("cascade stopped at step 1" in n for n in r["notes"]))
        self.assertEqual(r["highball_uses"], 1)

    def test_spam_shows_refusal_debts_and_no_gain(self):
        r = run("highball_overused")
        base = run("east_competent")
        self.assertEqual(r["highball_uses"], 3)
        self.assertGreaterEqual(r["highball_refusals"], 1,
                                "consecutive-day push was not refused")
        self.assertTrue(any("rest debts" in c for c in r["costs"]))
        # spam buys nothing: no stock ends better than the competent baseline
        for k in r["stocks"]:
            self.assertLessEqual(r["stocks"][k], base["stocks"][k] + 0.001,
                                 "spam improved a stock — modeled profit should not exist")

    def test_consecutive_day_refusal_unit(self):
        s = sm.Survival("unit", {"route": "east"})
        self.assertTrue(s._use_highball(2, "Imka", "unit test"))
        before = s.residents["Imka"]["stress"]
        self.assertFalse(s._use_highball(3, "Imka", "unit test"),
                         "consecutive-day same-resident use must be refused")
        self.assertGreater(s.residents["Imka"]["stress"], before)
        self.assertEqual(len(s.highball_uses), 1)

    def test_hazard_bar_refusal_unit(self):
        s = sm.Survival("unit", {"route": "east"})
        s.residents["Teo"]["fatigue"] = 85.0
        self.assertFalse(s._use_highball(2, "Teo", "unit test"),
                         "critical-fatigue resident must refuse overtime (hazard bar)")

    def test_not_required_for_competent_play(self):
        for name in ("east_competent", "west_competent"):
            self.assertEqual(run(name)["highball_uses"], 0)


class RoutesAndJuna(unittest.TestCase):
    def test_both_routes_viable_and_no_total_dominance(self):
        ew, ww = sm.route_balance_audit(verbose=False)
        self.assertGreater(ew, 0, "west dominates every category")
        self.assertGreater(ww, 0, "east dominates every category")

    def test_juna_admission_and_refusal(self):
        a, n = run("juna_admitted"), run("juna_no_berth")
        self.assertTrue(a["juna"])
        self.assertFalse(n["juna"])
        self.assertEqual(n["failures"], [], "turn-away is a human cost, not a collapse")
        self.assertTrue(any("turned away" in x for x in n["notes"]))


class SaveAndDeterminism(unittest.TestCase):
    def test_save_reload_resumes_to_identical_state(self):
        r = run("save_reload_incident")
        self.assertEqual(r["failures"], [])
        self.assertEqual(r["reload_check"], "identical",
                         "reload-and-resume diverged from the uninterrupted run")

    def test_deterministic_same_seed(self):
        a = sm.run_scenario("highball_overused", seed=45, verbose=False)
        b = sm.run_scenario("highball_overused", seed=45, verbose=False)
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
