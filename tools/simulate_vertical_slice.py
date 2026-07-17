#!/usr/bin/env python3
"""SIGNAL 45 — vertical-slice feasibility model ("The First Count", Days 1-7).

Engine-independent, deterministic labor/materials/schedule simulation of the
seven-day slice. It answers: do the required building, survival, and radio
beats fit the four residents' work capacity on BOTH routes, with margin,
under disruption?

Units:
  1 WU (work unit) ~= 45 simulated minutes of one resident's focused work.
  Base capacity: 7.5 WU per resident per day, x0.85 global inefficiency
  (travel, task switching, imperfect assignment).

This is a planning model, not the game: it deliberately ignores moment-to-
moment ordering inside a day and models days as labor pools spent against a
priority-ordered project plan with prerequisites, materials, and due dates.

Usage:
  python3 tools/simulate_vertical_slice.py --route east --scenario competent
  python3 tools/simulate_vertical_slice.py --all        # the 8 required runs
Exit status: non-zero if any mandatory milestone is impossible in a scenario
that is required to pass (competent runs must pass with >=15% margin;
disruption runs must still meet every mandatory milestone).
"""

import argparse
import sys
from dataclasses import dataclass, field, replace

EFFICIENCY = 0.85
BASE_WU = 7.5          # per resident per day, before efficiency
DAILY_PROJECT_CAP = 12.0   # max useful WU one project absorbs per day (~2 workers)
MAX_CONCURRENT = 3     # focus cap: projects worked in parallel per day
DAY1_ONBOARDING_LOSS = 5.0  # slower first day: guided pace, surveys, no rush
STORM_EMERGENCY_WU = 4.0    # Day 4 sealed-storm emergency workload (with prep)
STORM_EMERGENCY_WU_UNPREPPED = 8.0
RUNNER_NEXT_DAY_PENALTY = 3.0
TRIAGE_WU = 2.0             # Depot 9 aftermath (event 19, minor injury path)
EVENT_FRICTION_WU = 4.0     # arbitration/scenes labor lost across the week
MISTAKE_EXTRA_WU = 8.0      # one significant mistake: wrong build + re-site
MISTAKE_STORM_EXTRA = 7.0   # west-mistake variant: wrong seal bulkhead
INTERRUPT_REDO_WU = 3.0     # interrupted project: lost staged progress

MEAL_COOK_WU = 2.0
CLEANING_WU = 2.0
WATER_DUTY_TANK = 3.0       # hauling/purifying from the emergency tank
WATER_DUTY_CISTERN = 1.0    # once Cistern Works + Pump Room are online

START_SALVAGE = 12

# ---------------------------------------------------------------------------


@dataclass
class Project:
    pid: str
    label: str
    wu: float
    salvage: int = 0            # cost (negative = yields on completion)
    prereqs: tuple = ()
    needs_item: str = ""        # 'wire' / 'tools' from nightruns
    due_day: int = 0            # 0 = no deadline; else must finish by end of day N
    mandatory: bool = True
    done_day: int = field(default=0, compare=False)
    progress: float = field(default=0.0, compare=False)

    @property
    def done(self):
        return self.progress >= self.wu - 1e-9


def shared_projects():
    return [
        Project("survey_east", "Survey east rubble", 2, due_day=2),
        Project("survey_west", "Survey west flood", 2, due_day=2),
        Project("survey_lift", "Survey freight lift", 1, due_day=4),
        Project("seal", "Install Level-1 seal (chosen bulkhead)", 5, salvage=3, due_day=3),
        Project("storm_prep", "Pre-stage seals & intake covers", 3, due_day=3),
        Project("storm_repair", "Scrubber Gate intake repair (storm)", 6, due_day=5),
        Project("lp_upgrade", "Listening Post: improvised -> wired", 4, salvage=2, due_day=7),
        Project("splice", "Antenna wire splice", 3, needs_item="wire", due_day=6),
        Project("lift_repair", "Free the freight lift", 5, salvage=2, needs_item="tools", due_day=7),
        Project("fitters", "Activate the Fitters' Shop", 4, salvage=2, prereqs=("lift_repair",), due_day=7),
        Project("staging", "Repurpose Camp -> Staging Room", 3, prereqs=("beds",), due_day=7),
        Project("berth", "Prepare Juna's berth", 3, prereqs=("beds",), due_day=6),
        Project("module", "Module expansion (pantry/filtration)", 4, salvage=2, prereqs=("module_host",), due_day=7),
    ]


def east_projects():
    return [
        Project("clear_east", "Clear east rubble (staged)", 14, salvage=-8, due_day=3),
        Project("reinforce_e", "Reinforce east bays", 4, salvage=3, prereqs=("clear_east",), due_day=3),
        Project("trunk_e", "Extend trunk to east node", 6, salvage=4, prereqs=("reinforce_e",), due_day=4),
        Project("sleeper", "Convert railcar -> Sleeper Car", 8, salvage=4, prereqs=("clear_east",), due_day=3),
        Project("canteen", "Convert kiosk row -> Canteen", 7, salvage=4, prereqs=("trunk_e",), due_day=7),
        Project("aid_car", "Convert railcar -> Aid Car", 7, salvage=4, prereqs=("trunk_e",), due_day=7),
    ]


def west_projects():
    return [
        Project("drain_west", "Drain west gallery (pump rig)", 14, salvage=-6, due_day=3),
        Project("reinforce_w", "Reinforce west bays", 4, salvage=3, prereqs=("drain_west",), due_day=3),
        Project("trunk_w", "Extend trunk to west node", 6, salvage=4, prereqs=("reinforce_w",), due_day=4),
        Project("cistern", "Activate the Cistern Works", 8, salvage=4, prereqs=("drain_west",), due_day=3),
        Project("pump_room", "Activate the Pump Room", 6, salvage=3, prereqs=("trunk_w",), due_day=5),
        Project("west_bunks", "Build west-bay bunks", 6, salvage=3, prereqs=("drain_west",), due_day=5),
    ]


# Which project satisfies the 'beds' / 'module_host' virtual prereqs per route.
BEDS = {"east": "sleeper", "west": "west_bunks"}
MODULE_HOST = {"east": "canteen", "west": "cistern"}

# Priority order per route (competent play). Earlier = allocated first.
PLAN = {
    "east": ["survey_east", "survey_west", "clear_east", "seal", "sleeper",
             "reinforce_e", "storm_prep", "survey_lift", "trunk_e",
             "storm_repair", "lift_repair", "canteen", "berth", "splice",
             "lp_upgrade", "aid_car", "fitters", "module", "staging"],
    "west": ["survey_west", "survey_east", "drain_west", "seal", "cistern",
             "reinforce_w", "storm_prep", "survey_lift", "trunk_w",
             "storm_repair", "lift_repair", "pump_room", "west_bunks", "berth",
             "splice", "lp_upgrade", "fitters", "module", "staging"],
}

# Mandatory 07-section-21 milestones -> project ids (route-resolved).
MILESTONES = [
    ("Two surveys done", ["survey_east", "survey_west"]),
    ("Section reclaimed pre-storm", ["@breakthrough"]),
    ("Seal installed pre-storm", ["seal"]),
    ("Storm repair", ["storm_repair"]),
    ("Three rooms built/activated", ["@rooms3"]),
    ("Upgrade complete", ["lp_upgrade"]),
    ("Module expansion", ["module"]),
    ("Trunk extension", ["@trunk"]),
    ("Repurpose (Camp->Staging)", ["staging"]),
    ("Juna's berth by Day 6", ["berth"]),
    ("Splice by Day 6", ["splice"]),
]

NIGHTRUNS = {  # night -> (label, items granted at next dawn, salvage at dawn)
    2: ("Depot 9 (wire + tools)", ("wire", "tools"), 7),
    3: ("Marrow Street Clinic (meds)", (), 0),
    5: ("Fenwick Arcade (food/water/salvage)", (), 5),
}


@dataclass
class DayLog:
    day: int
    gross: float = 0.0
    essential: float = 0.0
    overhead: float = 0.0
    available: float = 0.0
    spent: float = 0.0
    worked: list = field(default_factory=list)
    notes: list = field(default_factory=list)


def session_minutes(day, night_mode, decisions):
    base = 6.5 + (1.5 if day == 1 else 0.0)
    night = 0.0 if day == 4 else (4.5 if night_mode == "active" else 1.2)
    return base + 0.35 * decisions + night


def simulate(route="east", scenario="competent", night_mode="delegated",
             both_wings=False, verbose=True):
    projects = {p.pid: p for p in shared_projects() +
                (east_projects() if route == "east" or both_wings else []) +
                (west_projects() if route == "west" or both_wings else [])}
    plan = list(PLAN[route])
    if both_wings:  # exclusivity stress test: try to open BOTH wings pre-storm
        other = "west" if route == "east" else "east"
        merged, seen = [], set()
        for pid in PLAN[route][:8] + PLAN[other][:8] + PLAN[route] + PLAN[other]:
            if pid not in seen:
                seen.add(pid)
                merged.append(pid)
        plan = merged

    salvage = START_SALVAGE
    items = set()
    logs = []
    total_minutes = 0.0
    beds_pid = BEDS[route]
    host_pid = MODULE_HOST[route]
    cistern_online = False
    fail_notes = []

    def resolved(prereqs):
        for pr in prereqs:
            pid = beds_pid if pr == "beds" else host_pid if pr == "module_host" else pr
            if pid in projects and not projects[pid].done:
                return False
        return True

    for day in range(1, 8):
        log = DayLog(day)
        residents = {"Imka": BASE_WU, "Ash": BASE_WU, "Teo": BASE_WU, "Maren": BASE_WU}

        # -- disruptions ----------------------------------------------------
        if day - 1 in NIGHTRUNS and (day - 1) != 4:
            residents["Teo"] = max(0.0, residents["Teo"] - RUNNER_NEXT_DAY_PENALTY)
            log.notes.append("Teo slow after last night's run (-%.0f WU)" % RUNNER_NEXT_DAY_PENALTY)
        if scenario == "absence" and day == 5:
            residents["Imka"] = 0.0
            log.notes.append("Imka unavailable all day (overwork collapse scenario)")
        if day == 3:  # event 19: minor injury from Depot 9 aftermath
            residents["Teo"] = max(0.0, residents["Teo"] - 2.0)
            log.notes.append("Teo minor injury (event 19): -2 WU, triage booked")

        gross = sum(residents.values()) * EFFICIENCY
        log.gross = gross

        # -- essential survival workload -----------------------------------
        water = WATER_DUTY_CISTERN if cistern_online else WATER_DUTY_TANK
        essential = MEAL_COOK_WU + CLEANING_WU + water
        if day == 3:
            essential += TRIAGE_WU
        log.essential = essential

        overhead = 0.0
        if day == 1:
            overhead += DAY1_ONBOARDING_LOSS
        if day == 4:
            prepped = projects["storm_prep"].done
            overhead += STORM_EMERGENCY_WU if prepped else STORM_EMERGENCY_WU_UNPREPPED
            log.notes.append("Sealed storm day: emergency workload %.0f WU (%s)" %
                             (STORM_EMERGENCY_WU if prepped else STORM_EMERGENCY_WU_UNPREPPED,
                              "prepped" if prepped else "UNPREPPED"))
        if day in (2, 6):
            overhead += EVENT_FRICTION_WU / 2.0   # scenes/arbitration spread over two days
        if scenario == "mistake" and day == 2:
            overhead += MISTAKE_EXTRA_WU if route == "east" else 0.0
            if route == "east":
                log.notes.append("MISTAKE: early Cold Store + re-sited beds (+%.0f WU)" % MISTAKE_EXTRA_WU)
        if scenario == "mistake" and route == "west" and day == 4:
            overhead += MISTAKE_STORM_EXTRA
            log.notes.append("MISTAKE: seal on wrong bulkhead (+%.0f WU storm damage)" % MISTAKE_STORM_EXTRA)
        if scenario == "interrupted" and day == 3:
            overhead += INTERRUPT_REDO_WU
            log.notes.append("Interrupted project: %.0f WU of staged work redone" % INTERRUPT_REDO_WU)
        log.overhead = overhead

        pool = max(0.0, gross - essential - overhead)
        log.available = pool

        # -- allocate to plan ----------------------------------------------
        # Short installation tasks (<=3 WU) do not consume a concurrency slot:
        # they are the work-order model's "short install" class, not projects.
        active_today = 0
        for pid in plan:
            if pool <= 0:
                break
            p = projects.get(pid)
            if p is None or p.done or not resolved(p.prereqs):
                continue
            is_short = p.wu <= 3.0
            if not is_short and active_today >= MAX_CONCURRENT:
                continue
            if p.needs_item and p.needs_item not in items:
                continue
            if p.salvage > 0 and p.progress == 0 and salvage < p.salvage:
                continue  # can't reserve materials yet
            if p.salvage > 0 and p.progress == 0:
                salvage -= p.salvage  # reserve on start
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
                if pid in ("cistern", "pump_room") and \
                        projects.get("cistern", p).done and projects.get("pump_room", p).done:
                    cistern_online = True
                    log.notes.append("Cistern online: water duty drops to %.0f WU/day" % WATER_DUTY_CISTERN)
            else:
                log.worked.append("%s %.0f/%.0f" % (p.label, p.progress, p.wu))

        # -- nightrun -------------------------------------------------------
        if day in NIGHTRUNS and day != 4:
            label, granted, dawn_salvage = NIGHTRUNS[day]
            log.notes.append("Nightrun: %s (%s)" % (label, night_mode))
            items.update(granted)
            salvage += dawn_salvage

        decisions = 8 if day == 1 else 11
        total_minutes += session_minutes(day, night_mode, decisions)
        logs.append(log)

    # -- milestones ---------------------------------------------------------
    breakthrough = projects["clear_east"] if route == "east" else projects["drain_west"]
    rooms = [projects[p] for p in
             (("sleeper", "canteen", "aid_car") if route == "east"
              else ("cistern", "pump_room", "fitters"))]
    trunk = projects["trunk_e" if route == "east" else "trunk_w"]

    missed = []
    for name, pids in MILESTONES:
        for pid in pids:
            if pid == "@breakthrough":
                ok = breakthrough.done and breakthrough.done_day <= 3
            elif pid == "@rooms3":
                ok = all(r.done for r in rooms)
            elif pid == "@trunk":
                ok = trunk.done
            else:
                p = projects[pid]
                ok = p.done and (p.due_day == 0 or p.done_day <= p.due_day)
            if not ok:
                missed.append(name)
                break

    required = sum(p.wu for p in projects.values()
                   if p.done or (p.mandatory and not both_wings))
    spent = sum(l.spent for l in logs)
    supply = sum(l.available for l in logs)
    margin = (supply - required) / required if required else 0.0

    # -- report -------------------------------------------------------------
    out = []
    out.append("=" * 72)
    out.append("SIGNAL 45 slice feasibility  route=%s scenario=%s night=%s%s"
               % (route, scenario, night_mode, " [BOTH-WINGS STRESS]" if both_wings else ""))
    out.append("-" * 72)
    for l in logs:
        out.append("Day %d: gross %5.1f | essential %4.1f | overhead %4.1f | "
                   "project pool %5.1f | spent %5.1f"
                   % (l.day, l.gross, l.essential, l.overhead, l.available, l.spent))
        for w in l.worked:
            out.append("        - " + w)
        for n in l.notes:
            out.append("        ! " + n)
    out.append("-" * 72)
    out.append("Project WU required (plan): %6.1f" % required)
    out.append("Project WU available     : %6.1f" % supply)
    out.append("Capacity margin          : %+6.1f%%" % (margin * 100))
    out.append("Session time, 7 days     : %5.1f min (%s nights)" % (total_minutes, night_mode))
    done_days = {p.pid: p.done_day for p in projects.values() if p.done}
    out.append("Completed: " + ", ".join("%s:d%d" % (k, v) for k, v in sorted(done_days.items())))
    if missed:
        out.append("MISSED MILESTONES: " + "; ".join(missed))
        out.append("Recovery guidance: drop optional work (Cold Store, second-wing "
                   "opening), fire the R-11 valve once, or shift Aid/Canteen "
                   "furnishing to Day 7 — mandatory beats keep priority.")
    else:
        out.append("ALL MANDATORY MILESTONES MET.")
    text = "\n".join(out)
    if verbose:
        print(text)
    return {"missed": missed, "margin": margin, "minutes": total_minutes,
            "required": required, "supply": supply, "report": text,
            "done_days": done_days}


REQUIRED_RUNS = [
    dict(route="east", scenario="competent"),
    dict(route="west", scenario="competent"),
    dict(route="east", scenario="mistake"),
    dict(route="west", scenario="mistake"),
    dict(route="east", scenario="absence"),
    dict(route="east", scenario="interrupted"),
    dict(route="west", scenario="competent", night_mode="delegated"),
    dict(route="west", scenario="competent", night_mode="active"),
]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--route", choices=["east", "west"], default="east")
    ap.add_argument("--scenario", choices=["competent", "mistake", "absence", "interrupted"],
                    default="competent")
    ap.add_argument("--night", choices=["delegated", "active"], default="delegated")
    ap.add_argument("--both-wings", action="store_true",
                    help="stress test: attempt both wings pre-storm (should fail)")
    ap.add_argument("--all", action="store_true", help="run the 8 required scenarios")
    args = ap.parse_args(argv)

    if args.all:
        ok = True
        for cfg in REQUIRED_RUNS:
            r = simulate(**cfg)
            print()
            if r["missed"]:
                ok = False
            if cfg["scenario"] == "competent" and not cfg.get("both_wings") and r["margin"] < 0.15:
                print("!! competent margin below 15%% target: %.1f%%" % (r["margin"] * 100))
                ok = False
        stress = simulate(route="east", scenario="competent", both_wings=True)
        print()
        if not stress["missed"]:
            print("!! exclusivity broken: both wings completed pre-storm")
            ok = False
        return 0 if ok else 1

    r = simulate(route=args.route, scenario=args.scenario,
                 night_mode=args.night, both_wings=args.both_wings)
    if args.both_wings:
        return 0 if r["missed"] else 1
    return 1 if r["missed"] else 0


if __name__ == "__main__":
    sys.exit(main())
