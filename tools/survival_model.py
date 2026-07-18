#!/usr/bin/env python3
"""SIGNAL 45 — survival-economy layer over the seven-day labor model (Prompt 3).

Consumes simulate_vertical_slice.py's day-by-day output (one set of numbers,
never a parallel truth) and layers on: five stock resources, four resident
needs, four utility families, incidents, cascades, weather, emergency actions,
and the HIGHBALL order — then audits warnings, exploits, and route balance.

Stock/needs values load from tools/data/resources.json, utility values from
utilities.json, incident/condition/HIGHBALL values from incidents.json; the
scenario matrix from scenarios.json. Model-plumbing constants (loop shapes,
day indices of authored beats) live in code; tuning numbers live in config.
All values are PROVISIONAL until measured in a playable build (D-043/D-045).
Deterministic: any stochastic element uses a seeded LCG (default seed 45).

Declared approximations (D-045; also in 20 §1): needs step daily; the
needs->work-efficiency ladder is applied as same-day survival-side accounting
(reported as needs_derate_wu / labor_margin_adjusted) — the precomputed labor
completions are not re-planned; the human ledger beyond HIGHBALL's rest debt
is note-level; materials arithmetic belongs to the labor model.

Usage:
  python3 tools/survival_model.py --scenario east_competent
  python3 tools/survival_model.py --all
Exit nonzero if a required scenario fails its survival checks.
"""

import argparse
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
    """Seedable deterministic RNG (no wall-clock, no global random).
    Note: low-order-bit quality is poor (state % 100 of a 2^31 LCG) —
    acceptable at <=3 rolls/run; replace before any per-phase use (D-045)."""

    def __init__(self, seed=45):
        self.state = seed & 0x7FFFFFFF

    def roll(self):  # 0..99
        self.state = (1103515245 * self.state + 12345) & 0x7FFFFFFF
        return self.state % 100


class Warnings:
    """Ledger proving forecast-before-punishment: every shortage stage must
    have been preceded by a logged warning on an earlier day/phase."""

    def __init__(self):
        self.log = []   # [day, kind, text, forecast_class] (JSON-safe lists)

    def warn(self, day, kind, text, fclass="projection"):
        self.log.append([day, kind, text, fclass])

    def warned_before(self, day, kind):
        return any(d < day and k == kind for d, k, _, _ in self.log)

    def has(self, kind):
        return any(k == kind for _, k, _, _ in self.log)


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


class Survival:
    def __init__(self, scenario_name, cfg, seed=45):
        self.name = scenario_name
        self.cfg = cfg
        self.flags = set(cfg.get("flags", []))
        self._seed = seed
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
        self.overflow_lost = {"clean_water": 0.0, "food": 0.0}
        n = RES["needs"]
        self.needs_cfg = n
        start = n["start"]
        self.residents = {r: {"hunger": float(start["hunger"]),
                              "fatigue": float(start["fatigue"]),
                              "stress": float(start["stress"]),
                              "health": float(start["health"]),
                              "conditions": {}}   # name -> {"since": d, "treated": d|None}
                          for r in svs.RESIDENTS}
        self.juna_present = False
        self.highball_uses = []      # [day, resident] (executed only)
        self.highball_refusals = []  # [day, resident, reason]
        self.highball_debt = []      # [resident, text] promises of rest
        self._overtime_tonight = set()   # residents whose rest is docked tonight
        self.machine_worn = 0        # accumulated breakdown wear
        self.cascade_steps_seen = 0
        self.cascade_interrupted = False
        self.contamination_active = False
        self.illness = False
        self.utility_head = []       # per-day headroom dicts
        self.shed_log = []           # [day, [loads shed]]
        self.needs_derate_wu = 0.0   # same-day efficiency-ladder accounting
        self._crew_mult_floor = 1.0
        self._below40 = {}           # resident -> first day health < 40
        self.reload_check = None

    # ------------------------------------------------------------------
    def run(self):
        labor_kwargs = dict(route=self.cfg["route"],
                            scenario=self.cfg.get("labor", "competent"),
                            efficiency=self.cfg.get("efficiency", svs.EFFICIENCY),
                            verbose=False)
        if "absent" in self.cfg:
            labor_kwargs["absent"] = tuple(self.cfg["absent"])
        self.labor = svs.simulate(**labor_kwargs)
        done_by = {}
        for d in self.labor["days"]:
            for pid in d["completed"]:
                done_by[pid] = d["day"]
        self._done_by = done_by

        snap = None
        for d in self.labor["days"]:
            self._day(d, done_by)
            if "snapshot_midday3" in self.flags and d["day"] == 3 and snap is None:
                # serialize the COMPLETE mutable state through JSON (proves
                # serializability), reload it into a fresh instance, and run
                # the twin through days 4-7 alongside this run.
                snap = json.dumps(self._state_dict(), sort_keys=True)

        self._final_checks()
        result = self._result()

        if snap is not None:
            twin = Survival(self.name, self.cfg, seed=self._seed)
            twin.labor = self.labor
            twin._done_by = done_by
            twin._load_state(json.loads(snap))
            for d in self.labor["days"]:
                if d["day"] > 3:
                    twin._day(d, done_by)
            twin._final_checks()
            twin_result = twin._result()
            # the twin must reach the identical end state: no divergence,
            # no duplicated grants, no lost bookings (17 §5's contract).
            probe = {k: v for k, v in result.items() if k != "reload_check"}
            twin_probe = {k: v for k, v in twin_result.items() if k != "reload_check"}
            if probe == twin_probe:
                self.reload_check = "identical"
                self.notes.append("d3 snapshot: reload-and-resume reached the identical Day-7 state "
                                  "(stocks, needs, bookings, warnings — no dup, no loss)")
            else:
                self.reload_check = "DIVERGED"
                self.failures.append("save/reload divergence: resumed run does not match")
            result = self._result()
        return result

    # -- serializable full state (everything mutable) -------------------
    def _state_dict(self):
        return {
            "stocks": dict(self.stocks),
            "overflow_lost": dict(self.overflow_lost),
            "residents": {n: {"hunger": r["hunger"], "fatigue": r["fatigue"],
                              "stress": r["stress"], "health": r["health"],
                              "conditions": {c: dict(v) for c, v in r["conditions"].items()}}
                          for n, r in self.residents.items()},
            "juna_present": self.juna_present,
            "highball_uses": [list(u) for u in self.highball_uses],
            "highball_refusals": [list(u) for u in self.highball_refusals],
            "highball_debt": [list(u) for u in self.highball_debt],
            "overtime_tonight": sorted(self._overtime_tonight),
            "machine_worn": self.machine_worn,
            "cascade_steps_seen": self.cascade_steps_seen,
            "cascade_interrupted": self.cascade_interrupted,
            "contamination_active": self.contamination_active,
            "illness": self.illness,
            "utility_head": [dict(h) for h in self.utility_head],
            "shed_log": [[d, list(l)] for d, l in self.shed_log],
            "needs_derate_wu": self.needs_derate_wu,
            "below40": dict(self._below40),
            "rng_state": self.rng.state,
            "warnings": [list(w) for w in self.warnings.log],
            "notes": list(self.notes),
            "costs": list(self.costs),
            "failures": list(self.failures),
        }

    def _load_state(self, s):
        self.stocks = dict(s["stocks"])
        self.overflow_lost = dict(s["overflow_lost"])
        self.residents = {n: {"hunger": r["hunger"], "fatigue": r["fatigue"],
                              "stress": r["stress"], "health": r["health"],
                              "conditions": {c: dict(v) for c, v in r["conditions"].items()}}
                          for n, r in s["residents"].items()}
        self.juna_present = s["juna_present"]
        self.highball_uses = [list(u) for u in s["highball_uses"]]
        self.highball_refusals = [list(u) for u in s["highball_refusals"]]
        self.highball_debt = [list(u) for u in s["highball_debt"]]
        self._overtime_tonight = set(s["overtime_tonight"])
        self.machine_worn = s["machine_worn"]
        self.cascade_steps_seen = s["cascade_steps_seen"]
        self.cascade_interrupted = s["cascade_interrupted"]
        self.contamination_active = s["contamination_active"]
        self.illness = s["illness"]
        self.utility_head = [dict(h) for h in s["utility_head"]]
        self.shed_log = [[d, list(l)] for d, l in s["shed_log"]]
        self.needs_derate_wu = s["needs_derate_wu"]
        self._below40 = dict(s["below40"])
        self.rng.state = s["rng_state"]
        self.warnings.log = [list(w) for w in s["warnings"]]
        self.notes = list(s["notes"])
        self.costs = list(s["costs"])
        self.failures = list(s["failures"])

    # ------------------------------------------------------------------
    def _add_condition(self, resident, cond, day):
        r = self.residents[resident]
        if cond in r["conditions"]:
            return
        hit = INC["condition_rules"][cond]["health_hit"]
        r["conditions"][cond] = {"since": day, "treated": None}
        r["health"] = clamp(r["health"] - hit, 0.0, 100.0)
        self._health_watch(resident, day)

    def _health_watch(self, resident, day):
        r = self.residents[resident]
        n = self.needs_cfg
        if r["health"] < n["health_warn_threshold"] and not self.warnings.has("health_%s" % resident):
            self.warnings.warn(day, "health_%s" % resident,
                               "%s is declining — treatment needed soon" % resident, "projection")
        if r["health"] < n["safe"] and resident not in self._below40:
            self._below40[resident] = day
            if not self.warnings.warned_before(day, "health_%s" % resident):
                self.failures.append("critical health (%s) without prior warning" % resident)

    # ------------------------------------------------------------------
    def _day(self, d, done_by):
        day = d["day"]
        route = self.cfg["route"]
        st = RES["stocks"]
        n = self.needs_cfg
        stress_c = n["stress_costs"]
        pop = len(svs.RESIDENTS) + (1 if self.juna_present else 0)
        self._overtime_tonight = set()

        # ---------- STORM TELEGRAPH (free 1-phase tier, every scenario) ----------
        if day == 3:
            self.warnings.warn(day, "storm",
                               "Ash ticking on the intake mesh — cinder storm tomorrow (free telegraph; "
                               "the monitored band would have named severity two days out)", "fact")

        # ---------- WATER ----------
        wcfg = st["clean_water"]
        cistern_online = ("cistern" in done_by and "pump_room" in done_by
                          and day > max(done_by["cistern"], done_by["pump_room"]))
        produced = 0.0
        if cistern_online:
            produced += wcfg["sources"]["cistern_online_per_day"]
        else:
            produced += wcfg["sources"]["water_duty_tank_per_day"]
            if "purifier" in done_by and day >= done_by["purifier"]:
                produced += wcfg["sources"]["purifier_bonus_per_day"]
        if "hoard_water" in self.flags and not cistern_online:
            produced += wcfg["sources"]["hoard_extra_tank_duty_per_day"]
            if day == 1:
                self.notes.append("d1: hoarding — extra tank duty ordered (labor spent topping storage)")
        if "pump_room_offline" in self.flags and cistern_online:
            produced -= 6.0
            self.notes.append("d%d: Pump Room offline — cistern output down (visible cause)" % day)
        if "water_valve_open_day3" in self.flags and day == 3:
            self.stocks["clean_water"] = max(0.0, self.stocks["clean_water"] - wcfg["valve_mistake_loss"])
            self.notes.append("d3: MISTAKE — transfer valve left open overnight (−%d person-days)"
                              % wcfg["valve_mistake_loss"])
        use = pop * wcfg["use_per_resident_per_day"]
        if d["spent"] > wcfg["works_draw_trigger_wu"]:
            use += wcfg["works_draw_big_build_day"]
        if ("water_ration_late" in self.flags
                and self.stocks["clean_water"] < wcfg["ration_trigger_stock"] and day >= 4):
            use -= wcfg["ration_saving_per_day"]
            self._stress_all(stress_c["water_rationing"], "water rationing")
            self.costs.append("d%d: water rationed (stress cost, remembered decision)" % day)
        if d["run"] and svs.RUN_ARCADE in str(d["run"]) and "hoard_water" in self.flags:
            self.stocks["clean_water"] += wcfg["sources"]["arcade_run"]
            self.notes.append("d%d: hoarding — arcade bottled water hauled home (+%d)"
                              % (day, wcfg["sources"]["arcade_run"]))
        cap = wcfg["cap_with_cistern"] if cistern_online else wcfg["storage_cap"]
        over = max(0.0, self.stocks["clean_water"] + produced - use - cap)
        if over > 0:
            self.overflow_lost["clean_water"] += over
            self.warnings.warn(day, "water_storage_full",
                               "storage full — surplus runs to the drain (build capacity or use it)", "fact")
            self.notes.append("d%d: water storage at cap — %.1f person-days overflowed (never silent)"
                              % (day, over))
        self.stocks["clean_water"] = clamp(self.stocks["clean_water"] + produced - use, 0.0, cap)
        days_left = self.stocks["clean_water"] / max(use, 0.1)
        if days_left < wcfg["warn_days_left"]:
            self.warnings.warn(day, "water_low", "Clean water ≈ %.1f days at current use" % days_left)
        if self.stocks["clean_water"] <= 0.0:
            if not self.warnings.warned_before(day, "water_low"):
                self.failures.append("water shortage without prior warning")
            self._stress_all(stress_c["dry_taps"], "dry taps")
            self.costs.append("d%d: water at zero — pressure before harm (dehydration contextual)" % day)

        # ---------- FOOD ----------
        fcfg = st["food"]
        meals_needed = pop * fcfg["meals_per_resident_per_day"]
        if "food_overtrade_day2" in self.flags and day == 2:
            self.stocks["food"] -= 10
            self.notes.append("d2: MISTAKE — traded away 10 meals to Sable")
        if day == 3:   # Sable's first arrival (event 10): staple trade both routes
            self.stocks["food"] = clamp(self.stocks["food"] + fcfg["sources"]["sable_trade"],
                                        0, fcfg["storage_cap"])
            self.notes.append("d3: Sable trade — +%d meals (priced in the manifest)"
                              % fcfg["sources"]["sable_trade"])
        if d["run"] and svs.RUN_ARCADE in str(d["run"]):
            if "arcade_food_missed" in self.flags:
                self.notes.append("d%d: arcade run came home salvage-heavy — no food carried "
                                  "(the third lever, also forfeited)" % day)
            else:
                self.stocks["food"] = clamp(self.stocks["food"] + fcfg["sources"]["arcade_run"],
                                            0, fcfg["storage_cap"])
        if "canteen" in done_by and day > done_by["canteen"]:
            meals_needed -= fcfg["sources"]["canteen_waste_reduction_per_day"]
        if ("food_overtrade_day2" in self.flags and "no_rationing" not in self.flags
                and day >= 5
                and self.stocks["food"] < meals_needed * fcfg["warn_meals_factor"]):
            meals_needed = max(0.0, meals_needed - fcfg["ration_meals_per_day_saving"])
            self._stress_all(stress_c["food_rationing"], "food rationing")
            self.costs.append("d%d: food rationed — fewer meals, stress, a remembered decision" % day)
        if self.stocks["food"] >= meals_needed:
            self.stocks["food"] -= meals_needed
            for r in self.residents.values():
                r["hunger"] = clamp(r["hunger"] - n["hunger_recovery_meal"], 0, 100)
        else:
            short = meals_needed - self.stocks["food"]
            self.stocks["food"] = 0.0
            if not self.warnings.warned_before(day, "food_low"):
                # a shortage may not strike unwarned: the forecast fires the day before
                self.failures.append("food shortage without prior warning (d%d)" % day)
            for r in self.residents.values():
                r["hunger"] = clamp(r["hunger"] + n["hunger_step_missed_meal"], 0, 100)
            self._stress_all(stress_c["short_meals"], "short meals")
            self.costs.append("d%d: %.0f meals short — hunger and stress, no injury "
                              "(one missed meal is never critical harm)" % (day, short))
        if self.stocks["food"] < meals_needed * fcfg["warn_meals_factor"]:
            self.warnings.warn(day, "food_low",
                               "Food: about %.0f meals — thin past tomorrow" % self.stocks["food"])

        # ---------- CHARGE / POWER (tier-ordered shedding, D-045) ----------
        pcfg = UTIL["power"]
        gen = pcfg["generation"]["stabilized"
                                 if "flywheel_stab" in done_by and day >= done_by["flywheel_stab"]
                                 else "partial"]
        loads = pcfg["loads"]
        demand = {"scrubbers": loads["scrubbers"], "lights": loads["lights"], "radio": loads["radio"]}
        if route == "west" and day >= 2 and not cistern_online:
            demand["pump_rig_west"] = loads["pump_rig_west"]
        if cistern_online:
            demand["cistern_pumps"] = loads["cistern_pumps"]
        if day != 4:
            demand["hotplate"] = loads["hotplate"]
        if d["spent"] > 10:
            demand["tools"] = loads["tools"]
        storm_draw = pcfg["storm_intake_clog_draw"] if day == 4 else 0
        boil_draw = (INC["families"]["water_contamination"]["boil_order_charge_per_day"]
                     if (self.contamination_active and "contamination_ignored" not in self.flags) else 0)
        headroom = gen - sum(demand.values()) - storm_draw - boil_draw
        tier_of = pcfg["tier_of"]
        shed = []
        if headroom < 0:
            # shed the lowest occupied tier first, load by load — demand actually
            # falls; only a residual deficit draws the battery/cell rack
            for tier in reversed(pcfg["priority_tiers"]):        # optional, normal, ...
                if tier in ("critical", "essential"):
                    break
                for load in sorted(l for l in demand if tier_of[l] == tier):
                    if headroom < 0:
                        headroom += demand.pop(load)
                        shed.append(load)
            if shed:
                self.shed_log.append([day, list(shed)])
                self.notes.append("d%d: load board shed %s (lowest occupied tier: Normal) — banner, %s"
                                  % (day, "+".join(shed),
                                     "cold meal tonight" if "hotplate" in shed else "hand tools down"))
                self._stress_all(stress_c["brown_out"], "brown-out")
        if headroom < 0:
            self.stocks["charge"] = clamp(self.stocks["charge"] + headroom, 0, self.caps["charge"])
            self.notes.append("d%d: residual deficit %d cell-hours drawn from the rack" % (day, -headroom))
            if self.stocks["charge"] <= 0 and not self.warnings.warned_before(day, "power_tight"):
                self.failures.append("power collapse without warning")
        else:
            self.stocks["charge"] = clamp(self.stocks["charge"]
                                          + min(headroom, st["charge"]["bank_rate_max_per_day"]),
                                          0, self.caps["charge"])
        if headroom < pcfg["overload"]["warn_headroom"]:
            self.warnings.warn(day, "power_tight",
                               "Power headroom %d cell-hours — shed a load or expect brown-out" % headroom)
        self.utility_head.append({"day": day, "power": headroom,
                                  "air": (UTIL["air"]["filtration_capacity"]["repaired"]
                                          if "gate_repair" in done_by
                                          else UTIL["air"]["filtration_capacity"]["damaged"])
                                         - pop - (UTIL["air"]["storm_load_extra"] if day == 4 else 0),
                                  "water_ok": days_left > 1.0,
                                  "structure": "reinforced"
                                               if (("reinforce_e" in done_by or "reinforce_w" in done_by)
                                                   and day >= min(done_by.get("reinforce_e", 99),
                                                                  done_by.get("reinforce_w", 99)))
                                               else "strained-hotspot"})

        # ---------- CASCADE (power -> air -> exposure) ----------
        if "cascade_day3" in self.flags and day == 3:
            self.warnings.warn(day, "flywheel", "Bearing whine — Flywheel unstable (repair or shed load)", "fact")
            self.cascade_steps_seen = 1
            if "highball_rescue" in self.flags:
                if self._use_highball(day, "Imka", "bridge the Flywheel through the whine"):
                    self.cascade_interrupted = True
                    self.notes.append("d3: HIGHBALL bridged power — cascade stopped at step 1")
            elif "cascade_ignored" in self.flags:
                self.cascade_steps_seen = 2
                self.notes.append("d3: scrubbers shed — east-wing air degrading (3-phase window)")
                self.warnings.warn(day, "air_degrade", "East wing air unsafe in ~3 phases", "projection")
                self.cascade_steps_seen = 3
                self._add_condition("Teo", "respiratory_exposure", day)
                self.costs.append("d3-4: ignored cascade reached step 3 — respiratory exposure "
                                  "(bounded there; hard max 3)")
            else:
                # battery bridge: charge cost + the normal tier goes dark while bridging
                self.stocks["charge"] = max(0.0, self.stocks["charge"]
                                            - pcfg["battery"]["bridge_cost_charge"])
                self._stress_all(stress_c["brown_out"], "bridge brown-out")
                self.notes.append("d3: battery bridge (−%d cell-hours) + Normal tier shed while bridging "
                                  "(cold meal) — cascade stopped at step 2 boundary"
                                  % pcfg["battery"]["bridge_cost_charge"])
                self.costs.append("d3: battery bridge — charge spent, cold meal (the free-looking option is not free)")
                self.cascade_interrupted = True

        # ---------- STORM DAY 4 ----------
        if day == 4 and "storm_prep_staged" in self.flags:
            self.notes.append("d4: storm — covers pre-staged, seals held; cleanup order only (prepped path)")
        if self.cfg.get("labor") == "prep_last" and day == 4:
            if not self.warnings.warned_before(4, "storm"):
                self.failures.append("storm punishment landed without the free telegraph")
            self.stocks["medicine"] -= st["medicine"]["sinks"]["storm_injury_unprepped"]
            self._add_condition("Maren", "minor_injury", day)
            self.costs.append("d4: unprepped storm — injury + 1 medicine (serious but recoverable)")

        # ---------- CONTAMINATION ----------
        ccfg = INC["families"]["water_contamination"]
        if "contamination_day5" in self.flags and day == 5:
            self.contamination_active = True
            self.warnings.warn(day, "water_contam",
                               "Water tastes of ash — STORAGE link flagged; boil order available", "fact")
            if "contamination_ignored" in self.flags:
                self.notes.append("d5: contamination warning DISMISSED — no boil order")
                self.warnings.warn(day, "illness_risk",
                                   "unboiled water in the kettles — illness likely within a day", "projection")
            else:
                self.notes.append("d5: contamination — boil order engaged (+%d charge/day, %d days)"
                                  % (ccfg["boil_order_charge_per_day"], ccfg["boil_order_days"]))
        if self.contamination_active and "contamination_ignored" not in self.flags and day >= 6:
            self.contamination_active = False
            self.notes.append("d6: purifier flush complete — water clean (%.0f person-day lost)"
                              % ccfg["flush_water_loss_person_days"])
            self.stocks["clean_water"] = max(0.0, self.stocks["clean_water"]
                                             - ccfg["flush_water_loss_person_days"])
        if self.contamination_active and "contamination_ignored" in self.flags:
            if day == 6 and not self.illness:
                self.illness = True
                self._add_condition("Maren", "waterborne_illness", day)
                self.costs.append("d6: waterborne illness (Maren) — the dismissed warning's price; "
                                  "half capacity, no cooking duty")
            if day == 7:
                self.stocks["medicine"] -= st["medicine"]["sinks"]["illness_course"]
                self.residents["Maren"]["conditions"]["waterborne_illness"]["treated"] = day
                self.contamination_active = False
                self.stocks["clean_water"] = max(0.0, self.stocks["clean_water"]
                                                 - ccfg["flush_water_loss_person_days"])
                self.notes.append("d7: illness course started (2 doses committed) + overdue flush")
                self.costs.append("d7: 2 medicine committed to the illness course "
                                  "(free doses now %.0f)" % max(0.0, self.stocks["medicine"]))

        # ---------- MEDICINE ----------
        mcfg = st["medicine"]
        if day == 3:
            self.stocks["medicine"] -= mcfg["sinks"]["triage_event19"]
        if d["run"] and svs.RUN_CLINIC in str(d["run"]):
            self.stocks["medicine"] = clamp(self.stocks["medicine"] + mcfg["sources"]["clinic_aid_or_barter"],
                                            0, self.caps["medicine"])
        if self.stocks["medicine"] < mcfg["warn_free_doses"]:
            self.warnings.warn(day, "meds_low",
                               "Medicine: %d doses free — one emergency deep" % self.stocks["medicine"], "fact")
        assert self.stocks["medicine"] > -0.001, "medicine went negative"
        self.stocks["medicine"] = max(0.0, self.stocks["medicine"])

        # ---------- HIGHBALL spam scenario ----------
        if "highball_spam" in self.flags:
            if day == 2:
                self._use_highball(day, "Imka", "unnecessary acceleration")
            if day == 3:
                self._use_highball(day, "Imka", "unnecessary acceleration")   # consecutive -> refusal
                self._use_highball(day, "Teo", "unnecessary acceleration")
            if day == 4:
                self._use_highball(day, "Imka", "unnecessary acceleration")

        # ---------- NEEDS: daily steps ----------
        rough = (route == "west" and not ("west_bunks" in done_by and day >= done_by["west_bunks"]))
        for name, r in self.residents.items():
            # a resident's real day = essential duties + project labor, not projects alone
            worked = (d["spent"] + d.get("essential", 0.0)) / max(len(self.residents), 1)
            accrual = n["fatigue_work_day"] * (worked / n["fatigue_day_baseline_wu"])
            rec = n["fatigue_recovery_rough_sleep"] if rough else n["fatigue_recovery_sleep"]
            if "sleeper" in done_by and day >= done_by["sleeper"]:
                rec += n["fatigue_recovery_sleeper_bonus"]
            overtime = 0.0
            if name in self._overtime_tonight:
                rec = max(0.0, rec - INC["highball"]["costs"]["rest_debt_recovery_dock"])
                overtime = INC["highball"]["costs"]["named_resident_overtime_fatigue"]
            # recovery applies to the day's accrual; overtime fatigue lands AFTER
            # the docked night's rest, so a pushed resident starts tomorrow tired
            r["fatigue"] = clamp(clamp(r["fatigue"] + accrual - rec, 0, 100) + overtime, 0, 100)
            if rough:
                r["stress"] = clamp(r["stress"] + n["stress_rough_sleep"], 0, 100)
            else:
                r["stress"] = clamp(r["stress"] - n["stress_recovery_good_day"], 0, 100)
            if "notes" in d and any("injury" in x for x in d["notes"]) and name == "Teo":
                self._add_condition("Teo", "minor_injury", day)
            # treatment: begins the day AFTER the condition lands (dose committed
            # at triage), recovers health_treatment_per_day, never past start health
            for cond, state in list(r["conditions"].items()):
                rules = INC["condition_rules"][cond]
                if state["treated"] is None and day > state["since"]:
                    if cond == "waterborne_illness" and "contamination_ignored" in self.flags:
                        pass   # its treatment day is scripted above (day 7)
                    else:
                        state["treated"] = day
                if state["treated"] is not None and day > state["treated"]:
                    # recovery accrues from the day AFTER treatment begins,
                    # and never past start health (an injury is never a net gain)
                    r["health"] = clamp(r["health"] + n["health_treatment_per_day"],
                                        0, n["start"]["health"])
                if state["treated"] is not None and day >= state["treated"] + rules["recovery_days"]:
                    del r["conditions"][cond]
                elif state["treated"] is None and day > state["since"] \
                        and cond in ("serious_injury", "waterborne_illness"):
                    r["health"] = clamp(r["health"] + n["health_untreated_serious_per_day"], 0, 100)
            self._health_watch(name, day)
            if r["fatigue"] >= 100:
                if "exhaustion" not in r["conditions"]:
                    self._add_condition(name, "exhaustion", day)
                self.warnings.warn(day, "exhaustion_%s" % name,
                                   "%s cannot safely work the next shift without rest" % name, "projection")

        # ---------- efficiency ladder (same-day survival-side accounting) ----------
        mults = []
        for r in self.residents.values():
            worst = max(r["hunger"], r["fatigue"])   # 17 §1: the ladder rides hunger/fatigue
            if worst >= n["strained"]:
                mults.append(n["work_efficiency"]["critical"])
            elif worst >= n["safe"]:
                mults.append(n["work_efficiency"]["strained"])
            else:
                mults.append(1.0)
        crew_mult = sum(mults) / len(mults)
        assert crew_mult >= n["work_efficiency"]["critical"], "efficiency floor breached (never zero)"
        self._crew_mult_floor = min(self._crew_mult_floor, crew_mult)
        if crew_mult < 1.0:
            derate = d["spent"] * (1.0 - crew_mult)
            self.needs_derate_wu += derate
            self.notes.append("d%d: crew slowed by need bands (×%.3f) — ≈%.1f WU of today's work "
                              "lost to hunger/fatigue (reduced, never zero)" % (day, crew_mult, derate))

        # ---------- JUNA ----------
        if day == 6:
            if "juna_refused" in self.flags:
                self.notes.append("d6: no berth — Juna turned away at the gate (witnessed; Ash's line crossed)")
                self._stress_all(stress_c["turn_away"], "the turn-away")
                self.residents["Ash"]["stress"] = clamp(self.residents["Ash"]["stress"]
                                                        + stress_c["turn_away_ash_extra"], 0, 100)
                self.costs.append("d6: Juna refused — human cost, no mechanical collapse")
            elif "berth" in done_by and done_by["berth"] <= 6:
                self.juna_present = True
                self.notes.append("d6: Juna settled — fifth resident (food/water demand up, +labor buffer)")

    # ------------------------------------------------------------------
    def _stress_all(self, amt, why):
        # DECLARED SIMPLIFICATION (D-045): shared hardships stress everyone
        # equally; individual memories/promises/grudges are 19 §6 canon, not
        # modeled here (only HIGHBALL's rest debt is a tracked promise).
        for r in self.residents.values():
            r["stress"] = clamp(r["stress"] + amt, 0, 100)

    def _use_highball(self, day, resident, why):
        hb = INC["highball"]["costs"]
        n = self.needs_cfg
        if any(u[0] == day for u in self.highball_uses):
            self.highball_refusals.append([day, resident, "one per day"])
            self.notes.append("d%d: HIGHBALL refused — one order per day (anti-spam)" % day)
            return False
        if any(u[0] == day - 1 and u[1] == resident for u in self.highball_uses):
            self.highball_refusals.append([day, resident, "consecutive day"])
            r = self.residents[resident]
            r["stress"] = clamp(r["stress"] + n["stress_costs"]["highball_consecutive_refusal"], 0, 100)
            self.notes.append("d%d: HIGHBALL REFUSED — %s was pushed yesterday and will not go again "
                              "(stress; the promise of rest stands)" % (day, resident))
            return False
        r = self.residents[resident]
        if r["fatigue"] >= n["strained"] or "exhaustion" in r["conditions"]:
            self.highball_refusals.append([day, resident, "hazard bar (critical fatigue)"])
            self.notes.append("d%d: HIGHBALL REFUSED — %s is unfit for overtime (hazard bar, 17 §2)"
                              % (day, resident))
            return False
        self.highball_uses.append([day, resident])
        self.highball_debt.append([resident, "rest owed d%d" % (day + 1)])
        self._overtime_tonight.add(resident)   # fatigue + docked rest applied in the needs step
        risk = hb["breakdown_risk_pct"]
        if len(self.highball_uses) >= 3:
            risk *= 2
        if self.rng.roll() < risk:
            self.machine_worn += 1
            self.costs.append("d%d: HIGHBALL breakdown — worn machinery: repair debt %d material + %d WU "
                              "posted to the works queue" % (day, hb["breakdown_cost_materials"],
                                                             hb["breakdown_cost_repair_wu"]))
        self.notes.append("d%d: HIGHBALL (%s): %s — cost visible up front" % (day, resident, why))
        return True

    # ------------------------------------------------------------------
    def _final_checks(self):
        # no negative stocks anywhere
        for k, v in self.stocks.items():
            assert v > -0.001, "%s negative" % k
        # cancel-refund: DESIGN RULE, not simulated arithmetic (D-045) — the
        # reservation policy lives in resources.json materials.reservation and
        # is enforced by the reservation system at first playable.
        if "cancel_canteen_day4" in self.flags:
            self.notes.append("d4: Canteen cancel evaluated — design rule "
                              "(resources.json materials.reservation): unconsumed reserve refunds 100%, "
                              "consumed stages and sunk labor lost; arithmetic deferred to first playable")
            self.costs.append("cancel policy: refund never exceeds reserve (rule-level, unsimulated)")
        # highball spam produced visible cost, never profit
        if "highball_spam" in self.flags:
            debt = len(self.highball_debt)
            assert debt >= 2, "spam left no rest debt"
            self.costs.append("HIGHBALL overuse: %d executed, %d refused, %d rest debts, %d worn-machinery marks"
                              % (len(self.highball_uses), len(self.highball_refusals),
                                 debt, self.machine_worn))
        # death never occurs in slice; sub-critical health must have been warned
        # (checked at the moment of crossing in _health_watch; asserted again here)
        for name, r in self.residents.items():
            assert r["health"] > 0, "resident died in slice (forbidden)"
            if name in self._below40:
                assert self.warnings.warned_before(self._below40[name], "health_%s" % name), \
                    "critical health without warning"
        # cascades bounded (regression guard: the authored chains stop at the
        # config bound; a future chain exceeding it fails here)
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
        end_needs = {name: {"hunger": round(r["hunger"]), "fatigue": round(r["fatigue"]),
                            "stress": round(r["stress"]), "health": round(r["health"]),
                            "conditions": sorted(r["conditions"])}
                     for name, r in self.residents.items()}
        total_avail = sum(x["available"] for x in self.labor["days"])
        adj = self.labor["margin"] - (self.needs_derate_wu / total_avail if total_avail else 0.0)
        ok = not self.failures
        return {"name": self.name, "ok": ok, "failures": list(self.failures),
                "stocks": {k: round(v, 1) for k, v in self.stocks.items()},
                "materials_end": None,  # labor model owns materials (svs report; the two 12s are test-pinned)
                "needs": end_needs, "notes": list(self.notes), "costs": list(self.costs),
                "warnings": len(self.warnings.log),
                "warning_log": [list(w) for w in self.warnings.log],
                "labor_margin": self.labor["margin"],
                "labor_margin_adjusted": round(adj, 4),
                "needs_derate_wu": round(self.needs_derate_wu, 2),
                "crew_mult_floor": round(self._crew_mult_floor, 3),
                "overflow_lost": {k: round(v, 1) for k, v in self.overflow_lost.items()},
                "shed_log": [[d, list(l)] for d, l in self.shed_log],
                "utility_head": self.utility_head, "juna": self.juna_present,
                "highball_uses": len(self.highball_uses),
                "highball_refusals": len(self.highball_refusals),
                "highball_debt": len(self.highball_debt),
                "worn": self.machine_worn,
                "reload_check": self.reload_check}


def run_scenario(name, seed=45, verbose=True):
    cfg = SCEN["scenarios"][name]
    r = Survival(name, cfg, seed=seed).run()
    if verbose:
        print("=" * 70)
        print("SURVIVAL %-24s %s   (labor margin %+.1f%%, needs-adjusted %+.1f%%)" %
              (name, "PASS" if r["ok"] else "FAIL", r["labor_margin"] * 100,
               r["labor_margin_adjusted"] * 100))
        print("  end stocks: " + "  ".join("%s %.1f" % (k, v) for k, v in r["stocks"].items()))
        hb = ("  highball x%d/ref %d (worn %d)" % (r["highball_uses"], r["highball_refusals"], r["worn"])
              if (r["highball_uses"] or r["highball_refusals"]) else "")
        print("  warnings logged: %d%s  juna: %s" % (r["warnings"], hb, r["juna"]))
        for x in r["notes"]:
            print("   ! " + x)
        for c in r["costs"]:
            print("   $ " + c)
        for f in r["failures"]:
            print("   X " + f)
    return r


def route_balance_audit(verbose=True):
    """Count-based audit: neither route may win every measured category.
    (Magnitudes and the felt experience are playtest questions — 07 §21.)"""
    e = run_scenario("east_competent", verbose=False)
    w = run_scenario("west_competent", verbose=False)
    cats = {
        "labor_margin": (e["labor_margin"], w["labor_margin"]),
        "end_water": (e["stocks"]["clean_water"], w["stocks"]["clean_water"]),
        "end_food": (e["stocks"]["food"], w["stocks"]["food"]),
        "end_charge": (e["stocks"]["charge"], w["stocks"]["charge"]),
        "avg_stress_inverse": (-sum(r["stress"] for r in e["needs"].values()),
                               -sum(r["stress"] for r in w["needs"].values())),
        "avg_fatigue_inverse": (-sum(r["fatigue"] for r in e["needs"].values()),
                                -sum(r["fatigue"] for r in w["needs"].values())),
    }
    east_wins = sum(1 for a, b in cats.values() if a > b)
    west_wins = sum(1 for a, b in cats.values() if b > a)
    if verbose:
        print("ROUTE BALANCE (count-based): east wins %d categories, west wins %d — %s" %
              (east_wins, west_wins,
               "no route wins everything" if east_wins and west_wins else "DOMINANCE DETECTED"))
        for k, (a, b) in cats.items():
            print("   %-20s E %10.3f   W %10.3f" % (k, a, b))
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
