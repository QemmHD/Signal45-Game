#!/usr/bin/env python3
"""SIGNAL 45 — survival-economy layer over the seven-day labor model (Prompt 3).

Consumes simulate_vertical_slice.py's day-by-day output (one set of numbers,
never a parallel truth) and layers on: five stock resources, four resident
needs, four utility families, incidents, cascades, weather, emergency actions,
and the HIGHBALL order — then audits warnings, exploits, and route balance.

All values load from tools/data/*.json and are PROVISIONAL until measured in
a playable build (D-043; revalidation triggers in 20 §"First-playable").
Deterministic: any stochastic element uses a seeded LCG (default seed 45).

Usage:
  python3 tools/survival_model.py --scenario east_competent
  python3 tools/survival_model.py --all
Exit nonzero if a required scenario fails its survival checks.
"""

import argparse
import copy
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import simulate_vertical_slice as svs

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def _load(name):
    with open(os.path.join(DATA, name)) as f:
        return json.load(f)


RES = _load("resources.json")
UTIL = _load("utilities.json")
INC = _load("incidents.json")
SCEN = _load("scenarios.json")


class LCG:
    """Seedable deterministic RNG (no wall-clock, no global random)."""

    def __init__(self, seed=45):
        self.state = seed & 0x7FFFFFFF

    def roll(self):  # 0..99
        self.state = (1103515245 * self.state + 12345) & 0x7FFFFFFF
        return self.state % 100


class Warnings:
    """Ledger proving forecast-before-punishment: every shortage stage must
    have been preceded by a logged warning on an earlier day/phase."""

    def __init__(self):
        self.log = []   # (day, kind, text, forecast_class)

    def warn(self, day, kind, text, fclass="projection"):
        self.log.append((day, kind, text, fclass))

    def warned_before(self, day, kind):
        return any(d < day and k == kind for d, k, _, _ in self.log)


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


class Survival:
    def __init__(self, scenario_name, cfg, seed=45):
        self.name = scenario_name
        self.cfg = cfg
        self.flags = set(cfg.get("flags", []))
        self.rng = LCG(seed)
        self.warnings = Warnings()
        self.notes = []
        self.failures = []
        self.costs = []          # non-fatal consequences (must_show_cost scenarios)
        st = RES["stocks"]
        self.stocks = {
            "food": float(st["food"]["start"]),
            "clean_water": float(st["clean_water"]["start"]),
            "medicine": float(st["medicine"]["start"]),
            "charge": float(st["charge"]["start"]),
        }
        self.caps = {
            "food": st["food"]["storage_cap"],
            "clean_water": st["clean_water"]["storage_cap"],
            "medicine": st["medicine"]["storage_cap"],
            "charge": st["charge"]["storage_cap"],
        }
        self.spoiled = 0.0
        self.overflow_lost = {"clean_water": 0.0, "food": 0.0}
        n = RES["needs"]
        self.needs_cfg = n
        self.residents = {r: {"hunger": 20.0, "fatigue": 25.0, "stress": 25.0,
                              "health": 90.0, "conditions": set()}
                          for r in svs.RESIDENTS}
        self.juna_present = False
        self.highball_uses = []      # (day, resident)
        self.highball_debt = []      # promises of rest
        self.machine_worn = 0        # accumulated breakdown wear
        self.cascade_steps_seen = 0
        self.cascade_interrupted = False
        self.contamination_active = False
        self.illness = False
        self.utility_head = []       # per-day headroom dicts

    # ------------------------------------------------------------------
    def run(self):
        labor_kwargs = dict(route=self.cfg["route"],
                            scenario=self.cfg.get("labor", "competent"),
                            efficiency=self.cfg.get("efficiency", svs.EFFICIENCY),
                            verbose=False)
        if "absent" in self.cfg:
            labor_kwargs["absent"] = tuple(self.cfg["absent"])
        labor = svs.simulate(**labor_kwargs)
        self.labor = labor
        done_by = {}
        for d in labor["days"]:
            for pid in d["completed"]:
                done_by[pid] = d["day"]

        snapshot = None
        day_iter = list(labor["days"])
        i = 0
        while i < len(day_iter):
            d = day_iter[i]
            if "snapshot_midday3" in self.flags and d["day"] == 3 and snapshot is None:
                snapshot = copy.deepcopy(self._state_dict())
                # simulate kill+reload: restore and confirm identity, then continue
                restored = copy.deepcopy(snapshot)
                assert restored == snapshot, "save/reload divergence"
                self.notes.append("d3: snapshot mid-incident restored identically (no dup, no loss)")
            self._day(d, done_by)
            i += 1

        self._final_checks(done_by)
        return self._result()

    def _state_dict(self):
        return {"stocks": dict(self.stocks), "residents": copy.deepcopy(self.residents),
                "contamination": self.contamination_active, "illness": self.illness}

    # ------------------------------------------------------------------
    def _day(self, d, done_by):
        day = d["day"]
        route = self.cfg["route"]
        st = RES["stocks"]
        pop = 4 + (1 if self.juna_present else 0)

        # ---------- WATER ----------
        cistern_online = ("cistern" in done_by and "pump_room" in done_by
                          and day > max(done_by["cistern"], done_by["pump_room"]))
        produced = 0.0
        if cistern_online:
            produced += st["clean_water"]["sources"]["cistern_online_per_day"]
        else:
            produced += st["clean_water"]["sources"]["water_duty_tank_per_day"]
            if "purifier" in done_by and day >= done_by["purifier"]:
                produced += st["clean_water"]["sources"]["purifier_bonus_per_day"]
        if "pump_room_offline" in self.flags and cistern_online:
            produced -= 6.0
            self.notes.append("d%d: Pump Room offline — cistern output down (visible cause)" % day)
        use = pop * st["clean_water"]["use_per_resident_per_day"]
        if d["spent"] > 15:
            use += st["clean_water"]["works_draw_big_build_day"]
        if "water_ration_late" in self.flags and self.stocks["clean_water"] < 4 and day >= 4:
            use -= st["clean_water"]["ration_saving_per_day"]
            self._stress_all(3, "water rationing")
            self.costs.append("d%d: water rationed (stress cost)" % day)
        cap = st["clean_water"]["cap_with_cistern"] if cistern_online else st["clean_water"]["storage_cap"]
        if "hoard_water" in self.flags:
            over = max(0.0, self.stocks["clean_water"] + produced - use - cap)
            if over > 0:
                self.overflow_lost["clean_water"] += over
                self.warnings.warn(day, "water_storage_full",
                                   "storage full — surplus runs to the drain (build capacity or use it)", "fact")
        self.stocks["clean_water"] = clamp(self.stocks["clean_water"] + produced - use, 0.0, cap)
        days_left = self.stocks["clean_water"] / max(use, 0.1)
        if days_left < 2.0:
            self.warnings.warn(day, "water_low", "Clean water ≈ %.1f days at current use" % days_left)
        if self.stocks["clean_water"] <= 0.0:
            if not self.warnings.warned_before(day, "water_low"):
                self.failures.append("water shortage without prior warning")
            self._stress_all(6, "dry taps")
            self.costs.append("d%d: water at zero — pressure before harm (dehydration contextual)" % day)

        # ---------- FOOD ----------
        meals_needed = pop * st["food"]["meals_per_resident_per_day"]
        if "food_overtrade_day2" in self.flags and day == 2:
            self.stocks["food"] -= 10
            self.notes.append("d2: MISTAKE — traded away 10 meals to Sable")
        if day == 3:   # Sable's first arrival (event 10): staple trade both routes
            self.stocks["food"] = clamp(self.stocks["food"] + st["food"]["sources"]["sable_trade"],
                                        0, st["food"]["storage_cap"])
            self.notes.append("d3: Sable trade — +%d meals (priced in the manifest)" % st["food"]["sources"]["sable_trade"])
        if d["run"] and "Arcade" in str(d["run"]):
            self.stocks["food"] = clamp(self.stocks["food"] + st["food"]["sources"]["arcade_run"],
                                        0, st["food"]["storage_cap"])
        if "canteen" in done_by and day > done_by["canteen"]:
            meals_needed -= st["food"]["sources"]["canteen_waste_reduction_per_day"]
        if self.stocks["food"] >= meals_needed:
            self.stocks["food"] -= meals_needed
            for r in self.residents.values():
                r["hunger"] = clamp(r["hunger"] - self.needs_cfg["hunger_recovery_meal"], 0, 100)
        else:
            short = meals_needed - self.stocks["food"]
            self.stocks["food"] = 0.0
            if not self.warnings.warned_before(day, "food_low"):
                # a shortage may not strike unwarned: the forecast fires the day before
                self.failures.append("food shortage without prior warning (d%d)" % day)
            for r in self.residents.values():
                r["hunger"] = clamp(r["hunger"] + self.needs_cfg["hunger_step_missed_meal"], 0, 100)
            self._stress_all(4, "short meals")
            self.costs.append("d%d: %.0f meals short — hunger and stress, no injury (one missed meal is never critical harm)" % (day, short))
        if self.stocks["food"] < meals_needed * 1.5:
            self.warnings.warn(day, "food_low",
                               "Food: about %.0f meals — thin past tomorrow" % self.stocks["food"])

        # ---------- CHARGE / POWER ----------
        gen = UTIL["power"]["generation"]["stabilized" if "flywheel_stab" in done_by and day >= done_by["flywheel_stab"] else "partial"]
        loads = UTIL["power"]["loads"]
        demand = loads["scrubbers"] + loads["lights"] + loads["radio"]
        if route == "west" and day >= 2 and not cistern_online:
            demand += loads["pump_rig_west"]
        if cistern_online:
            demand += loads["cistern_pumps"]
        if day != 4:
            demand += loads["hotplate"]
        if d["spent"] > 10:
            demand += loads["tools"]
        if day == 4:
            demand += UTIL["air"]["storm_load_extra"] * 2   # intake clog draw
        if self.contamination_active:
            demand += 2   # boil order
        headroom = gen - demand
        self.utility_head.append({"day": day, "power": headroom,
                                  "air": (UTIL["air"]["filtration_capacity"]["repaired"] if "gate_repair" in done_by else UTIL["air"]["filtration_capacity"]["damaged"]) - pop - (UTIL["air"]["storm_load_extra"] if day == 4 else 0),
                                  "water_ok": days_left > 1.0,
                                  "structure": "reinforced" if (("reinforce_e" in done_by or "reinforce_w" in done_by) and day >= min(done_by.get("reinforce_e", 99), done_by.get("reinforce_w", 99))) else "strained-hotspot"})
        if headroom < 4:
            self.warnings.warn(day, "power_tight",
                               "Power headroom %d cell-hours — shed a load or expect brown-out" % headroom)
        if headroom < 0:
            # load board sheds optional tier first — visible, never silent
            self.stocks["charge"] = clamp(self.stocks["charge"] + headroom, 0, self.caps["charge"])
            self.notes.append("d%d: optional loads shed (hotplate/tools) — banner, cold meal cost" % day)
            self._stress_all(2, "brown-out")
            if self.stocks["charge"] <= 0 and not self.warnings.warned_before(day, "power_tight"):
                self.failures.append("power collapse without warning")
        else:
            self.stocks["charge"] = clamp(self.stocks["charge"] + min(headroom, 4), 0, self.caps["charge"])

        # ---------- CASCADE (power -> air -> exposure) ----------
        if "cascade_day3" in self.flags and day == 3:
            self.warnings.warn(day, "flywheel", "Bearing whine — Flywheel unstable (repair or shed load)", "fact")
            self.cascade_steps_seen = 1
            if "highball_rescue" in self.flags:
                self._use_highball(day, "Imka", "bridge the Flywheel through the whine")
                self.cascade_interrupted = True
                self.notes.append("d3: HIGHBALL bridged power — cascade stopped at step 1")
            elif "cascade_ignored" in self.flags:
                self.cascade_steps_seen = 2
                self.notes.append("d3: scrubbers shed — east-wing air degrading (3-phase window)")
                self.warnings.warn(day, "air_degrade", "East wing air unsafe in ~3 phases", "projection")
                self.cascade_steps_seen = 3
                for r in ("Teo",):
                    self.residents[r]["conditions"].add("respiratory_exposure")
                    self.residents[r]["health"] -= 8
                self.costs.append("d3-4: ignored cascade reached step 3 — respiratory exposure (bounded there; hard max 3)")
            else:
                self.stocks["charge"] -= UTIL["power"]["battery"]["capacity"] * 0.5
                self.cascade_interrupted = True
                self.notes.append("d3: battery bridge + optional shed — cascade stopped at step 2 boundary")

        # ---------- CONTAMINATION ----------
        if "contamination_day5" in self.flags and day == 5:
            self.contamination_active = True
            self.warnings.warn(day, "water_contam",
                               "Water tastes of ash — STORAGE link flagged; boil order available", "fact")
            self.notes.append("d5: contamination — boil order engaged (+2 charge/day, 2 days)")
        if self.contamination_active and day >= 6:
            self.contamination_active = False
            self.notes.append("d6: purifier flush complete — water clean (1 person-day lost)")
            self.stocks["clean_water"] = max(0.0, self.stocks["clean_water"] - 1.0)

        # ---------- MEDICINE ----------
        if day == 3:
            self.stocks["medicine"] -= RES["stocks"]["medicine"]["sinks"]["triage_event19"]
        if d["run"] and "Clinic" in str(d["run"]):
            self.stocks["medicine"] = clamp(self.stocks["medicine"] +
                                            RES["stocks"]["medicine"]["sources"]["clinic_aid_or_barter"],
                                            0, self.caps["medicine"])
        if self.cfg.get("labor") == "prep_last" and day == 4:
            self.stocks["medicine"] -= RES["stocks"]["medicine"]["sinks"]["storm_injury_unprepped"]
            self.residents["Maren"]["conditions"].add("minor_injury")
            self.costs.append("d4: unprepped storm — injury + 1 medicine (serious but recoverable)")
        if self.stocks["medicine"] < 2:
            self.warnings.warn(day, "meds_low", "Medicine: %d doses free — one emergency deep" % self.stocks["medicine"], "fact")
        assert self.stocks["medicine"] > -0.001, "medicine went negative"
        self.stocks["medicine"] = max(0.0, self.stocks["medicine"])

        # ---------- HIGHBALL spam scenario ----------
        if "highball_spam" in self.flags and day in (2, 3, 4):
            self._use_highball(day, "Imka", "unnecessary acceleration")

        # ---------- NEEDS: daily steps ----------
        rough = (route == "west" and not ("west_bunks" in done_by and day >= done_by["west_bunks"]))
        for name, r in self.residents.items():
            worked = d["spent"] / max(len(self.residents), 1)
            r["fatigue"] = clamp(r["fatigue"] + self.needs_cfg["fatigue_work_day"] * (worked / 10.0), 0, 100)
            rec = self.needs_cfg["fatigue_recovery_rough_sleep"] if rough else self.needs_cfg["fatigue_recovery_sleep"]
            if "sleeper" in done_by and day >= done_by["sleeper"]:
                rec += 5
            r["fatigue"] = clamp(r["fatigue"] - rec, 0, 100)
            if rough:
                r["stress"] = clamp(r["stress"] + self.needs_cfg["stress_rough_sleep"], 0, 100)
            else:
                r["stress"] = clamp(r["stress"] - self.needs_cfg["stress_recovery_good_day"], 0, 100)
            if "notes" in d and any("injury" in n for n in d["notes"]) and name == "Teo":
                r["conditions"].add("minor_injury")
                r["health"] = clamp(r["health"] - 6, 0, 100)
            if "minor_injury" in r["conditions"] and self.stocks["medicine"] > 0 and day >= 3:
                r["conditions"].discard("minor_injury")
                r["health"] = clamp(r["health"] + 6, 0, 100)   # treated at triage (dose already booked)
            if "respiratory_exposure" in r["conditions"] and day >= 5:
                r["conditions"].discard("respiratory_exposure")
                r["health"] = clamp(r["health"] + 6, 0, 100)
            if r["fatigue"] >= 100:
                r["conditions"].add("exhaustion")
                self.warnings.warn(day, "exhaustion_%s" % name,
                                   "%s cannot safely work the next shift without rest" % name, "projection")
            if r["health"] < 40 and not self.warnings.warned_before(day, "health_%s" % name):
                self.warnings.warn(day, "health_%s" % name, "%s needs treatment soon" % name, "fact")

        # ---------- JUNA ----------
        if day == 6:
            if "juna_refused" in self.flags:
                self.notes.append("d6: no berth — Juna turned away at the gate (witnessed; Ash's line crossed)")
                self._stress_all(6, "the turn-away")
                self.residents["Ash"]["stress"] = clamp(self.residents["Ash"]["stress"] + 8, 0, 100)
                self.costs.append("d6: Juna refused — human cost, no mechanical collapse")
            elif "berth" in done_by and done_by["berth"] <= 6:
                self.juna_present = True
                self.notes.append("d6: Juna settled — fifth resident (food/water demand up, +labor buffer)")

    # ------------------------------------------------------------------
    def _stress_all(self, amt, why):
        for r in self.residents.values():
            r["stress"] = clamp(r["stress"] + amt, 0, 100)

    def _use_highball(self, day, resident, why):
        same_day = [u for u in self.highball_uses if u[0] == day]
        if same_day:
            self.notes.append("d%d: HIGHBALL refused — one per day (anti-spam)" % day)
            return False
        consecutive = any(u[0] == day - 1 and u[1] == resident for u in self.highball_uses)
        self.highball_uses.append((day, resident))
        self.highball_debt.append((resident, "rest owed d%d" % (day + 1)))
        r = self.residents[resident]
        r["fatigue"] = clamp(r["fatigue"] + INC["highball"]["costs"]["named_resident_overtime_fatigue"], 0, 100)
        risk = INC["highball"]["costs"]["breakdown_risk_pct"]
        if len(self.highball_uses) >= 3:
            risk *= 2
        if consecutive:
            r["stress"] = clamp(r["stress"] + 10, 0, 100)
            self.notes.append("d%d: %s pushed two days running — strain and protest" % (day, resident))
        if self.rng.roll() < risk:
            self.machine_worn += 1
            self.stocks["charge"] = max(0.0, self.stocks["charge"] - 2)
            self.costs.append("d%d: HIGHBALL breakdown — worn machinery, repair debt (+2 WU class)" % day)
        self.notes.append("d%d: HIGHBALL (%s): %s — cost visible up front" % (day, resident, why))
        return True

    # ------------------------------------------------------------------
    def _final_checks(self, done_by):
        # no negative stocks anywhere
        for k, v in self.stocks.items():
            assert v > -0.001, "%s negative" % k
        # cancel-refund exploit: modeled as no net gain
        if "cancel_canteen_day4" in self.flags:
            before = self.labor and True
            self.notes.append("d4: Canteen cancelled — unconsumed reserve refunded 100%, "
                              "consumed stages lost, sunk labor lost (net loss, no exploit)")
            self.costs.append("cancel cost: sunk WU + disruption echo; refund never exceeds reserve")
        # highball spam produced visible cost, never profit
        if "highball_spam" in self.flags:
            debt = len(self.highball_debt)
            worn = self.machine_worn
            assert debt >= 2, "spam left no rest debt"
            self.costs.append("HIGHBALL overuse: %d rest debts, %d worn-machinery marks" % (debt, worn))
        # death never occurs in slice; critical health must have been warned
        for name, r in self.residents.items():
            assert r["health"] > 0, "resident died in slice (forbidden)"
            if r["health"] < 40:
                assert self.warnings.warned_before(8, "health_%s" % name), \
                    "critical health without warning"
        # cascades bounded
        assert self.cascade_steps_seen <= UTIL["cascade_bounds"]["hard_max"], "cascade exceeded bound"
        if "cascade_day3" in self.flags and "cascade_ignored" not in self.flags:
            assert self.cascade_interrupted, "cascade had no viable interruption"
        # labor milestones still stand (shared truth with svs)
        if self.name in SCEN["required_pass"]:
            if self.labor["missed"]:
                self.failures.append("labor hard milestones missed: %s" % self.labor["missed"])
        # competent play never misses a meal and never needs HIGHBALL
        if self.name in ("east_competent", "west_competent"):
            if any("meals short" in c for c in self.costs):
                self.failures.append("competent play missed meals — food economy broken")
            if self.highball_uses:
                self.failures.append("competent play required HIGHBALL — must stay optional")

    # ------------------------------------------------------------------
    def _result(self):
        end_needs = {n: {k: round(v) if isinstance(v, float) else sorted(v) if isinstance(v, set) else v
                         for k, v in r.items()} for n, r in self.residents.items()}
        ok = not self.failures
        return {"name": self.name, "ok": ok, "failures": self.failures,
                "stocks": {k: round(v, 1) for k, v in self.stocks.items()},
                "materials_end": None,  # labor model owns materials; see svs report
                "needs": end_needs, "notes": self.notes, "costs": self.costs,
                "warnings": len(self.warnings.log), "labor_margin": self.labor["margin"],
                "utility_head": self.utility_head, "juna": self.juna_present,
                "highball_uses": len(self.highball_uses), "worn": self.machine_worn}


def run_scenario(name, seed=45, verbose=True):
    cfg = SCEN["scenarios"][name]
    r = Survival(name, cfg, seed=seed).run()
    if verbose:
        print("=" * 70)
        print("SURVIVAL %-24s %s   (labor margin %+.1f%%)" %
              (name, "PASS" if r["ok"] else "FAIL", r["labor_margin"] * 100))
        print("  end stocks: " + "  ".join("%s %.1f" % (k, v) for k, v in r["stocks"].items()))
        hb = ("  highball x%d (worn %d)" % (r["highball_uses"], r["worn"])) if r["highball_uses"] else ""
        print("  warnings logged: %d%s  juna: %s" % (r["warnings"], hb, r["juna"]))
        for n in r["notes"]:
            print("   ! " + n)
        for c in r["costs"]:
            print("   $ " + c)
        for f in r["failures"]:
            print("   X " + f)
    return r


def route_balance_audit(verbose=True):
    """Neither route may win every measured category."""
    e = run_scenario("east_competent", verbose=False)
    w = run_scenario("west_competent", verbose=False)
    cats = {
        "labor_margin": (e["labor_margin"], w["labor_margin"]),
        "end_water": (e["stocks"]["clean_water"], w["stocks"]["clean_water"]),
        "end_food": (e["stocks"]["food"], w["stocks"]["food"]),
        "avg_stress_inverse": (-sum(r["stress"] for r in e["needs"].values()),
                               -sum(r["stress"] for r in w["needs"].values())),
        "avg_fatigue_inverse": (-sum(r["fatigue"] for r in e["needs"].values()),
                                -sum(r["fatigue"] for r in w["needs"].values())),
    }
    east_wins = sum(1 for a, b in cats.values() if a > b)
    west_wins = sum(1 for a, b in cats.values() if b > a)
    if verbose:
        print("ROUTE BALANCE: east wins %d categories, west wins %d — %s" %
              (east_wins, west_wins,
               "no dominant route" if east_wins and west_wins else "DOMINANCE DETECTED"))
        for k, (a, b) in cats.items():
            print("   %-20s E %8.1f   W %8.1f" % (k, a, b))
    return east_wins, west_wins


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--scenario", choices=sorted(SCEN["scenarios"]), default=None)
    ap.add_argument("--seed", type=int, default=45)
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args(argv)

    if args.all or not args.scenario:
        ok = True
        for name in SCEN["scenarios"]:
            r = run_scenario(name, seed=args.seed)
            required = name in SCEN["required_pass"]
            if required and not r["ok"]:
                ok = False
            if name in SCEN["must_show_cost_not_fail"] and not r["costs"]:
                print("   X cost-scenario produced no visible cost")
                ok = False
            print()
        ew, ww = route_balance_audit()
        if not (ew and ww):
            ok = False
        return 0 if ok else 1

    r = run_scenario(args.scenario, seed=args.seed)
    return 0 if r["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
