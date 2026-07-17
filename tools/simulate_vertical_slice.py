#!/usr/bin/env python3
"""SIGNAL 45 — vertical-slice feasibility model ("The First Count", Days 1-7).

Engine-independent, deterministic labor/materials/schedule simulation of the
seven-day slice. It answers: do the required building, survival, and radio
beats fit the four residents' work capacity on BOTH routes, with margin,
under disruption — WITHOUT letting the model do anything the fiction forbids.

Fiction constraints encoded (red-team pass 3, D-042):
  * Day 1 is the guided first session: only the gate repair, purifier,
    surveys, and Flywheel stabilization are orderable. The route
    breakthrough cannot begin before Day 2 (the community scene).
  * Nightrun rewards require an able runner that night; an absent runner
    shifts the run (and its items) one night later.
  * The human ledger is priced: west's rough sleeping and bench triage
    cost labor until bunks/Aid Car exist; east's real beds pay a small
    rest bonus; west earns its canonical storm-recovery refund.
  * Storm preparation is positive-EV: skipping it costs +4 WU emergency
    labor AND -2 salvage storm damage against prep's 3 WU price.

Units: 1 WU ~= 45 simulated minutes of one resident's focused work.
Capacity: 7.5 WU/resident/day gross x 0.85 global inefficiency.

Usage:
  python3 tools/simulate_vertical_slice.py --route east --scenario competent
  python3 tools/simulate_vertical_slice.py --all      # required suite + sweeps
Exit nonzero if any required scenario misses a HARD milestone, a competent
margin drops below 15%, or the exclusivity stress unexpectedly passes.
"""

import argparse
import sys
from dataclasses import dataclass, field

EFFICIENCY = 0.85
BASE_WU = 7.5
DAILY_PROJECT_CAP = 12.0
MAX_CONCURRENT = 3
SHORT_INSTALL_WU = 3.0      # authored class boundary (see 11 s5: authored, not runtime)
DAY1_ONBOARDING_LOSS = 2.0  # guided pace only; Day-1 repair is priced work now
STORM_EMERGENCY_WU = 4.0
STORM_EMERGENCY_WU_UNPREPPED = 8.0
STORM_DAMAGE_SALVAGE_UNPREPPED = 2
RUNNER_NEXT_DAY_PENALTY = 3.0
TRIAGE_WU = 2.0
BENCH_TRIAGE_EXTRA = 1.0    # no Aid Car when event-19 triage lands (Ash's penalty)
EVENT_FRICTION_WU = 4.0
MISTAKE_EXTRA_WU = 8.0
MISTAKE_STORM_EXTRA = 7.0
INTERRUPT_REDO_WU = 3.0
ROUGH_SLEEP_MALUS = 1.0     # west: per day until bunks exist (Strain/rest quality)
REST_BONUS_EAST = 0.75      # east: per day from first Sleeper-Car night (Day 4+)
STORM_RECOVERY_REFUND_W = 3.0  # west: canonical Day-5 refund (10 s15)
NEGLECT_SAVED_WU = 2.0      # 'neglect' scenario: cleaning suspended
NEGLECT_CONSEQUENCE_WU = 3.0   # ...accidents/illness overhead from Day 3 on

MEAL_COOK_WU = 2.0
CLEANING_WU = 2.0
WATER_DUTY_TANK = 3.0
WATER_DUTY_CISTERN = 1.0

START_SALVAGE = 12
JUNA_BUFFER_WU = 4.0        # uncounted Day-7 buffer if her berth landed by Day 6

RESIDENTS = ("Imka", "Ash", "Teo", "Maren")
DAY1_ORDERABLE = {"gate_repair", "purifier", "survey_east", "survey_west",
                  "survey_lift", "flywheel_stab"}
RUN_NIGHTS = {2: ("Depot 9 (wire + tools)", ("wire", "tools"), 7),
              3: ("Marrow Street Clinic (meds)", (), 0),
              5: ("Fenwick Arcade (food/water/salvage)", (), 5)}


@dataclass
class Project:
    pid: str
    label: str
    wu: float
    salvage: int = 0
    prereqs: tuple = ()
    needs_item: str = ""
    due_day: int = 0
    mandatory: bool = True
    hard: bool = True           # soft milestones have authored miss-branches
    earliest_day: int = 1
    done_day: int = field(default=0, compare=False)
    progress: float = field(default=0.0, compare=False)

    @property
    def done(self):
        return self.progress >= self.wu - 1e-9


def build_projects(route, both_wings=False, late_second_wing=False):
    P = [
        Project("gate_repair", "Repair Scrubber Gate intake (Day 1)", 4, salvage=2, due_day=1),
        Project("purifier", "Purifier cartridge on the tank", 1, salvage=1, due_day=1),
        Project("survey_east", "Survey east rubble", 2, due_day=2),
        Project("survey_west", "Survey west flood", 2, due_day=2),
        Project("survey_lift", "Survey freight lift", 1, due_day=4),
        Project("flywheel_stab", "Stabilize the Flywheel (partial -> steady)", 4, salvage=2),
        Project("seal", "Install Level-1 seal (chosen bulkhead)", 4, salvage=3, due_day=3, earliest_day=2),
        Project("storm_prep", "Pre-stage seals & intake covers", 3, due_day=3, hard=False, earliest_day=2),
        Project("storm_repair", "Scrubber Gate storm repair", 6, due_day=5, earliest_day=4),
        Project("lp_upgrade", "Listening Post: improvised -> wired", 4, salvage=2),
        Project("splice", "Antenna wire splice", 3, needs_item="wire", due_day=6),
        Project("lift_repair", "Free the freight lift", 5, salvage=2, needs_item="tools"),
        Project("fitters", "Activate the Fitters' Shop", 4, salvage=2, prereqs=("lift_repair",)),
        Project("staging", "Repurpose Camp -> Staging Room", 3, prereqs=("beds",)),
        Project("berth", "Prepare Juna's berth", 3, prereqs=("beds",), due_day=6, hard=False),
        Project("module", "Module expansion (pantry/filtration)", 4, salvage=2, prereqs=("module_host",)),
        Project("cold_store", "Cold Store (discretionary siting build)", 5, salvage=2,
                mandatory=False, earliest_day=5),
    ]
    east = [
        Project("clear_east", "Clear east rubble (staged)", 12, salvage=-10, due_day=3, earliest_day=2),
        Project("reinforce_e", "Reinforce east bays", 3, salvage=2, prereqs=("clear_east",)),
        Project("trunk_e", "Extend trunk to east node", 6, salvage=3, prereqs=("reinforce_e",)),
        Project("sleeper", "Convert railcar -> Sleeper Car", 7, salvage=3, prereqs=("clear_east",), due_day=3),
        Project("canteen", "Convert kiosk row -> Canteen", 6, salvage=3, prereqs=("trunk_e",)),
        Project("aid_car", "Convert railcar -> Aid Car", 6, salvage=3, prereqs=("trunk_e",)),
    ]
    west = [
        Project("drain_west", "Drain west gallery (pump rig)", 12, salvage=-8, due_day=3, earliest_day=2),
        Project("reinforce_w", "Reinforce west bays", 3, salvage=2, prereqs=("drain_west",)),
        Project("trunk_w", "Extend trunk to west node", 6, salvage=3, prereqs=("drain_west",)),
        Project("cistern", "Activate the Cistern Works", 6, salvage=3, prereqs=("drain_west",), due_day=3),
        Project("pump_room", "Activate the Pump Room", 6, salvage=2, prereqs=("trunk_w",)),
        Project("west_bunks", "Build west-bay bunks", 5, salvage=2, prereqs=("drain_west",), due_day=5),
    ]
    projects = P + (east if route == "east" or both_wings else []) \
                 + (west if route == "west" or both_wings else [])
    if late_second_wing:  # optional Day-5+ opening of the other wing, +25% cost
        other = west if route == "east" else east
        for p in other[:2]:
            projects.append(Project("late_" + p.pid, "LATE " + p.label,
                                    round(p.wu * 1.25, 1), salvage=max(p.salvage, 0),
                                    mandatory=False, earliest_day=5))
    return {p.pid: p for p in projects}


BEDS = {"east": "sleeper", "west": "west_bunks"}
MODULE_HOST = {"east": "canteen", "west": "cistern"}

PLAN = {
    "east": ["gate_repair", "purifier", "survey_east", "survey_west", "survey_lift",
             "flywheel_stab", "clear_east", "seal", "storm_prep", "sleeper",
             "reinforce_e", "trunk_e", "storm_repair", "lift_repair", "berth",
             "canteen", "splice", "lp_upgrade", "aid_car", "fitters", "module",
             "staging", "cold_store", "late_drain_west", "late_reinforce_w"],
    "west": ["gate_repair", "purifier", "survey_west", "survey_east", "survey_lift",
             "flywheel_stab", "drain_west", "seal", "storm_prep", "cistern",
             "reinforce_w", "trunk_w", "storm_repair", "west_bunks", "pump_room",
             "berth", "lift_repair", "splice", "lp_upgrade", "fitters",
             "module", "staging", "cold_store", "late_clear_east", "late_reinforce_e"],
}

# Milestones: (name, ids-or-@virtual, hard?)
MILESTONES = [
    ("Day-1 gate repair", ["gate_repair"], True),
    ("Two surveys done", ["survey_east", "survey_west"], True),
    ("Section reclaimed pre-storm", ["@breakthrough"], True),
    ("Seal installed pre-storm", ["seal"], True),
    ("Storm prepped (soft: authored unprepped branch)", ["storm_prep"], False),
    ("Storm repair", ["storm_repair"], True),
    ("Three rooms built/activated", ["@rooms3"], True),
    ("Upgrade complete", ["lp_upgrade"], True),
    ("Module expansion", ["module"], True),
    ("Trunk extension by due day", ["@trunk"], True),
    ("Repurpose (Camp->Staging)", ["staging"], True),
    ("Juna's berth by Day 6 (soft: authored turn-away)", ["berth"], False),
    ("Splice by Day 6", ["splice"], True),
]


@dataclass
class DayLog:
    day: int
    gross: float = 0
    essential: float = 0
    overhead: float = 0
    available: float = 0
    spent: float = 0
    worked: list = field(default_factory=list)
    notes: list = field(default_factory=list)


def session_minutes(day, night_mode, run_tonight):
    decisions = {1: 8, 4: 12, 7: 10}.get(day, 11)
    base = 6.5 + (1.5 if day == 1 else 0.0) + 0.35 * decisions
    if day == 7:
        return base + 3.0          # the relay scene, choice, epilogue
    if not run_tonight:
        return base + 0.25         # quiet-shift transition
    return base + (4.5 if night_mode == "active" else 1.2)


def simulate(route="east", scenario="competent", night_mode="delegated",
             both_wings=False, late_second_wing=False, efficiency=EFFICIENCY,
             absent=("Imka", 5), verbose=True):
    projects = build_projects(route, both_wings, late_second_wing)
    plan = [p for p in PLAN[route] if p in projects]
    if both_wings:
        seen = set(plan)
        for pid in PLAN["west" if route == "east" else "east"]:
            if pid in projects and pid not in seen:
                plan.append(pid)
                seen.add(pid)

    salvage = START_SALVAGE
    items = set()
    logs = []
    minutes = 0.0
    active_minutes = 0.0
    beds_pid, host_pid = BEDS[route], MODULE_HOST[route]
    cistern_online = False
    pending_runs = dict(RUN_NIGHTS)
    run_schedule = {}
    prev_run_night = False

    def resolved(prereqs):
        for pr in prereqs:
            pid = beds_pid if pr == "beds" else host_pid if pr == "module_host" else pr
            if pid in projects and not projects[pid].done:
                return False
        return True

    for day in range(1, 8):
        log = DayLog(day)
        cap = {r: BASE_WU for r in RESIDENTS}

        if prev_run_night:
            cap["Teo"] = max(0.0, cap["Teo"] - RUNNER_NEXT_DAY_PENALTY)
            log.notes.append("Teo slow after last night's run (-%.0f WU)" % RUNNER_NEXT_DAY_PENALTY)
        if scenario == "absence" and day == absent[1]:
            cap[absent[0]] = 0.0
            log.notes.append("%s unavailable all day (absence scenario)" % absent[0])
        if day == 3:
            cap["Teo"] = max(0.0, cap["Teo"] - 2.0)
            log.notes.append("Teo minor injury (event 19): -2 WU, triage booked")

        gross = sum(cap.values()) * efficiency
        # human-ledger pricing (D-042): rest quality and triage venue
        if route == "west" and not projects["west_bunks"].done:
            gross -= ROUGH_SLEEP_MALUS
            log.notes.append("Rough sleeping at the Camp (-%.1f WU)" % ROUGH_SLEEP_MALUS)
        if route == "east" and day >= 4 and projects["sleeper"].done:
            gross += REST_BONUS_EAST
            log.notes.append("Sleeper Car rest bonus (+%.2f WU)" % REST_BONUS_EAST)
        log.gross = gross

        water = WATER_DUTY_CISTERN if cistern_online else WATER_DUTY_TANK
        cleaning = 0.0 if scenario == "neglect" else CLEANING_WU
        essential = MEAL_COOK_WU + cleaning + water
        if scenario == "neglect" and day >= 3:
            essential += NEGLECT_CONSEQUENCE_WU
            log.notes.append("Neglected essentials: accidents/illness (+%.0f WU)" % NEGLECT_CONSEQUENCE_WU)
        if day == 3:
            essential += TRIAGE_WU
            aid = projects.get("aid_car")
            if aid is None or not aid.done:
                essential += BENCH_TRIAGE_EXTRA
                log.notes.append("Bench triage (no Aid Car yet): +%.0f WU (Ash's penalty)" % BENCH_TRIAGE_EXTRA)
        log.essential = essential

        overhead = 0.0
        if day == 1:
            overhead += DAY1_ONBOARDING_LOSS
        if day == 4:
            prepped = projects["storm_prep"].done
            cost = STORM_EMERGENCY_WU if prepped else STORM_EMERGENCY_WU_UNPREPPED
            overhead += cost
            if not prepped:
                salvage = max(0, salvage - STORM_DAMAGE_SALVAGE_UNPREPPED)
                log.notes.append("UNPREPPED storm: +%.0f WU and -%d salvage damage"
                                 % (cost, STORM_DAMAGE_SALVAGE_UNPREPPED))
            else:
                log.notes.append("Sealed storm day: emergency workload %.0f WU (prepped)" % cost)
        if day == 5 and route == "west":
            overhead -= STORM_RECOVERY_REFUND_W
            log.notes.append("West storm-recovery refund (+%.0f WU back)" % STORM_RECOVERY_REFUND_W)
        if day in (2, 6):
            overhead += EVENT_FRICTION_WU / 2.0
        if scenario == "mistake" and day == 2 and route == "east":
            overhead += MISTAKE_EXTRA_WU
            log.notes.append("MISTAKE: early Cold Store + re-sited beds (+%.0f WU)" % MISTAKE_EXTRA_WU)
        if scenario == "mistake" and day == 4 and route == "west":
            overhead += MISTAKE_STORM_EXTRA
            log.notes.append("MISTAKE: seal on wrong bulkhead (+%.0f WU storm damage)" % MISTAKE_STORM_EXTRA)
        if scenario == "interrupted" and day == 3:
            overhead += INTERRUPT_REDO_WU
            log.notes.append("Interrupted project: %.0f WU of staged work redone" % INTERRUPT_REDO_WU)
        log.overhead = overhead

        pool = max(0.0, gross - essential - overhead)
        log.available = pool

        order = plan
        if scenario == "prep_last":
            order = [p for p in plan if p != "storm_prep"] + ["storm_prep"]

        active_today = 0
        for pid in order:
            if pool <= 0:
                break
            p = projects.get(pid)
            if p is None or p.done or not resolved(p.prereqs):
                continue
            if day < p.earliest_day or (day == 1 and pid not in DAY1_ORDERABLE):
                continue
            is_short = p.wu <= SHORT_INSTALL_WU
            if not is_short and active_today >= MAX_CONCURRENT:
                continue
            if p.needs_item and p.needs_item not in items:
                continue
            if p.salvage > 0 and p.progress == 0:
                if salvage < p.salvage:
                    continue
                salvage -= p.salvage
            alloc = min(DAILY_PROJECT_CAP, p.wu - p.progress, pool)
            p.progress += alloc
            pool -= alloc
            log.spent += alloc
            if not is_short:
                active_today += 1
            if p.done:
                p.done_day = day
                if p.salvage < 0:
                    salvage += -p.salvage
                log.worked.append("%s DONE (day %d)" % (p.label, day))
                if route == "west" and not cistern_online \
                        and projects["cistern"].done and projects["pump_room"].done:
                    cistern_online = True
                    log.notes.append("Cistern online: water duty 3 -> 1 WU/day from tomorrow")
            else:
                log.worked.append("%s %.1f/%.0f" % (p.label, p.progress, p.wu))

        # -- nightrun (needs an able runner tonight) -------------------------
        run_tonight = False
        if day in pending_runs and day != 4:
            runner_ok = cap["Teo"] > 0.0 or \
                (day >= 6 and projects["berth"].done and projects["berth"].done_day <= 6)
            if runner_ok:
                label, granted, dawn_salvage = pending_runs.pop(day)
                items.update(granted)
                salvage += dawn_salvage
                run_schedule[day] = label
                run_tonight = True
                log.notes.append("Nightrun: %s (%s)" % (label, night_mode))
            else:
                run = pending_runs.pop(day)
                pending_runs[day + 1] = run
                log.notes.append("No able runner tonight — %s shifts to night %d"
                                 % (run[0], day + 1))
        prev_run_night = run_tonight

        minutes += session_minutes(day, night_mode, run_tonight)
        if run_tonight and night_mode == "active":
            active_minutes += 4.5
        if day == 6 and projects["berth"].done and projects["berth"].done_day <= 6:
            log.notes.append("Juna settled: +%.0f WU uncounted Day-7 buffer available" % JUNA_BUFFER_WU)
        logs.append(log)

    breakthrough = projects["clear_east" if route == "east" else "drain_west"]
    rooms = [projects[p] for p in (("sleeper", "canteen", "aid_car") if route == "east"
                                   else ("cistern", "pump_room", "fitters"))]
    trunk = projects["trunk_e" if route == "east" else "trunk_w"]

    missed_hard, missed_soft = [], []
    for name, pids, hard in MILESTONES:
        ok = True
        for pid in pids:
            if pid == "@breakthrough":
                ok = breakthrough.done and breakthrough.done_day <= 3
            elif pid == "@rooms3":
                ok = all(r.done for r in rooms)          # week-end requirement
            elif pid == "@trunk":
                ok = trunk.done                          # week-end requirement
            else:
                p = projects[pid]
                ok = p.done and (p.due_day == 0 or p.done_day <= p.due_day)
            if not ok:
                break
        if not ok:
            (missed_hard if hard else missed_soft).append(name)

    if both_wings:
        required = sum(p.wu for p in projects.values() if p.done)
    else:
        required = sum(p.wu for p in projects.values() if p.mandatory)
    supply = sum(l.available for l in logs)
    margin = (supply - required) / required if required else 0.0

    out = ["=" * 72,
           "SIGNAL 45 slice feasibility  route=%s scenario=%s night=%s eff=%.3f%s%s"
           % (route, scenario, night_mode, efficiency,
              " [BOTH-WINGS STRESS]" if both_wings else "",
              " [+late second wing]" if late_second_wing else ""),
           "-" * 72]
    for l in logs:
        out.append("Day %d: gross %5.1f | essential %4.1f | overhead %+5.1f | "
                   "pool %5.1f | spent %5.1f"
                   % (l.day, l.gross, l.essential, l.overhead, l.available, l.spent))
        out += ["        - " + w for w in l.worked]
        out += ["        ! " + n for n in l.notes]
    out.append("-" * 72)
    out.append("Project WU required (mandatory bill): %6.1f" % required)
    out.append("Project WU available (pool total)   : %6.1f" % supply)
    out.append("Capacity margin                     : %+6.1f%%" % (margin * 100))
    out.append("Session time, 7 days: %5.1f min (%s; active-run share %4.1f%%)"
               % (minutes, night_mode, 100.0 * active_minutes / minutes))
    done_days = {p.pid: p.done_day for p in projects.values() if p.done}
    out.append("Completed: " + ", ".join("%s:d%d" % (k, v) for k, v in sorted(done_days.items())))
    beat_targets = {"trunk_e": 4, "trunk_w": 4, "sleeper": 3, "cistern": 3,
                    "west_bunks": 5, "pump_room": 5, "storm_prep": 3}
    drift = ["%s d%d (target d%d)" % (pid, projects[pid].done_day, t)
             for pid, t in beat_targets.items()
             if pid in projects and projects[pid].done and projects[pid].done_day > t]
    late = ["%s NOT DONE (target d%d)" % (pid, t) for pid, t in beat_targets.items()
            if pid in projects and not projects[pid].done]
    if drift or late:
        out.append("Beat drift (dramaturgy targets, non-fatal): " + "; ".join(drift + late))
    if missed_hard:
        out.append("MISSED HARD MILESTONES: " + "; ".join(missed_hard))
        out.append("Recovery guidance: drop discretionary work (Cold Store, late second "
                   "wing), fire the R-11 valve once (materials only), draw Juna's Day-7 "
                   "buffer, or shift Aid/Canteen furnishing to Day 7.")
    if missed_soft:
        out.append("Missed soft milestones (authored branches absorb): " + "; ".join(missed_soft))
    if not missed_hard and not missed_soft:
        out.append("ALL MILESTONES MET (hard and soft).")
    text = "\n".join(out)
    if verbose:
        print(text)
    return {"missed": missed_hard, "missed_soft": missed_soft, "margin": margin,
            "minutes": minutes, "active_minutes": active_minutes,
            "required": required, "supply": supply, "report": text,
            "done_days": done_days, "runs": run_schedule}


REQUIRED_RUNS = [
    dict(route="east", scenario="competent"),
    dict(route="west", scenario="competent"),
    dict(route="east", scenario="mistake"),
    dict(route="west", scenario="mistake"),
    dict(route="east", scenario="absence"),          # sweep covers the worst cell
    dict(route="east", scenario="interrupted"),
    dict(route="west", scenario="competent", night_mode="delegated"),
    dict(route="west", scenario="competent", night_mode="active"),
]


def absence_sweep(verbose=True):
    """Every resident x day 2..6 x both routes; returns the worst cell."""
    worst = None
    for route in ("east", "west"):
        for who in RESIDENTS:
            for day in range(2, 7):
                r = simulate(route=route, scenario="absence", absent=(who, day), verbose=False)
                key = (len(r["missed"]), len(r["missed_soft"]), -r["margin"])
                if worst is None or key > worst[0]:
                    worst = (key, route, who, day, r)
    _, route, who, day, r = worst
    if verbose:
        print("ABSENCE SWEEP worst cell: %s absent Day %d on %s -> hard misses: %s | "
              "soft misses: %s | margin %+.1f%%"
              % (who, day, route, r["missed"] or "none",
                 r["missed_soft"] or "none", r["margin"] * 100))
    return route, who, day, r


def efficiency_sweep(verbose=True):
    rows = []
    for eff in (0.85, 0.825, 0.80, 0.775):
        for route in ("east", "west"):
            r = simulate(route=route, scenario="competent", efficiency=eff, verbose=False)
            rows.append((eff, route, r["margin"], r["missed"], r["missed_soft"]))
    if verbose:
        print("EFFICIENCY SENSITIVITY:")
        for eff, route, margin, hard, soft in rows:
            print("  eff=%.3f %-4s margin %+6.1f%%  hard-miss: %s  soft-miss: %s"
                  % (eff, route, margin * 100, hard or "none", soft or "none"))
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--route", choices=["east", "west"], default="east")
    ap.add_argument("--scenario",
                    choices=["competent", "mistake", "absence", "interrupted",
                             "neglect", "prep_last"],
                    default="competent")
    ap.add_argument("--night", choices=["delegated", "active"], default="delegated")
    ap.add_argument("--both-wings", action="store_true")
    ap.add_argument("--late-second-wing", action="store_true")
    ap.add_argument("--efficiency", type=float, default=EFFICIENCY)
    ap.add_argument("--absent-who", choices=RESIDENTS, default="Imka")
    ap.add_argument("--absent-day", type=int, default=5)
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args(argv)

    if args.all:
        ok = True
        for cfg in REQUIRED_RUNS:
            r = simulate(**cfg)
            print()
            if r["missed"]:
                ok = False
            if cfg["scenario"] == "competent" and r["margin"] < 0.15:
                print("!! competent margin below 15%%: %.1f%%" % (r["margin"] * 100))
                ok = False
        stress = simulate(route="east", scenario="competent", both_wings=True)
        print()
        second_bt = stress["done_days"].get("drain_west", 0)
        if second_bt and second_bt <= 3:
            print("!! exclusivity broken: second wing opened pre-storm (day %d)" % second_bt)
            ok = False
        else:
            print("Exclusivity holds: second wing not opened pre-storm "
                  "(drain_west %s)" % ("day %d" % second_bt if second_bt else "never started"))
        route, who, day, worst = absence_sweep()
        if worst["missed"]:
            print("!! absence sweep breaks a HARD milestone (%s day %d, %s)" % (who, day, route))
            ok = False
        print()
        efficiency_sweep()
        print()
        for extra in (dict(route="east", scenario="neglect"),
                      dict(route="east", scenario="prep_last"),
                      dict(route="west", scenario="competent", late_second_wing=True)):
            r = simulate(verbose=False, **extra)
            print("INFO %-58s margin %+6.1f%% hard-miss: %s soft-miss: %s"
                  % (str(sorted(extra.items())), r["margin"] * 100,
                     r["missed"] or "none", r["missed_soft"] or "none"))
        return 0 if ok else 1

    r = simulate(route=args.route, scenario=args.scenario, night_mode=args.night,
                 both_wings=args.both_wings, late_second_wing=args.late_second_wing,
                 efficiency=args.efficiency, absent=(args.absent_who, args.absent_day))
    if args.both_wings:
        return 0 if r["missed"] else 1
    return 1 if r["missed"] else 0


if __name__ == "__main__":
    sys.exit(main())
