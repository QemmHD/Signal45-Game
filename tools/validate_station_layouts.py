#!/usr/bin/env python3
"""SIGNAL 45 — station-layout validator (Prompt 4, D-046).

Runs the full structural-consistency battery over the three slice layouts
(day1, east_day7, west_day7). Proves placement, access, navigation, evacuation,
utility connection, and route requirements are consistent — it does NOT prove
the layouts are fun to build or inhabit (playable-prototype question).

Run:  python3 tools/validate_station_layouts.py            (exit 0 = all pass)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import spatial_model as sp
from spatial_model import (Layout, ValidationError, load_layout, utility_headroom,
                           OBJECTS, FAMILIES, _load)


def check(desc, fn, failures):
    try:
        fn()
        print("  ok   %s" % desc)
    except (ValidationError, AssertionError) as e:
        failures.append("%s: %s" % (desc, e))
        print("  FAIL %s -> %s" % (desc, e))


def validate(name, failures):
    print("== %s ==" % name)
    lay = load_layout(name)
    d = lay.d

    for r in lay.rooms.values():
        check("room %s valid" % r["id"], lambda r=r: lay.validate_room(r), failures)
    for o in lay.objects.values():
        check("object %s valid" % o["id"], lambda o=o: lay.validate_object(o), failures)

    def _reach():
        for fac in d["essential_facilities"]:
            assert lay.reachable_from_muster(fac), "essential facility unreachable: %s" % fac
    check("all essential facilities reachable from muster", _reach, failures)

    def _evac():
        for r in lay.rooms.values():
            if r.get("module_of"):
                continue
            length, alts, spof = lay.emergency_path(r["id"])
            assert length is not None, "no emergency path from %s" % r["id"]
    check("every room has an emergency path to a safe area", _evac, failures)

    def _areas():
        derived = {r["area"] for r in lay.rooms.values()}
        assert derived == set(d["areas"]), \
            "authored area list drifts from the rooms' own area labels: %s vs %s" % (
                sorted(set(d["areas"]) ^ derived), sorted(derived))
        n = len(derived)
        if d["day"] == 1:
            assert n == 4, "Day 1 must show exactly 4 functional areas (got %d)" % n
        else:
            assert 8 <= n <= 10, "Day 7 must show 8-10 functional areas (got %d)" % n
    check("functional-area count (derived from rooms, not the display list)", _areas, failures)

    def _comfort():
        lamps = [o for o in lay.objects.values() if o["type"] == "comfort_lamp"]
        assert lamps, "no platform comfort lighting placed"
        util = _load("utilities.json")
        assert util["power"]["tier_of"]["comfort_lighting"] == "optional"
    check("platform comfort lighting present and Optional-tier", _comfort, failures)

    def _headroom():
        head = utility_headroom(lay)
        shed = sp.sheddable_load(lay)
        assert head + shed >= 0, \
            "essential+critical demand exceeds generation even with every sheddable load dark " \
            "(headroom %d, sheddable %d)" % (head, shed)
    check("utility headroom: essential demand fits generation (sheddable loads may go dark)",
          _headroom, failures)

    if d["day"] == 7:
        def _juna():
            jb = d["juna_berth"]
            assert jb, "Day 7 must state Juna's berth"
            obj = lay.objects[jb["object"]]
            assert obj["room"] == jb["room"]
            assert OBJECTS["objects"][obj["type"]]["family"] == "rest_point"
            assert lay.reachable_from_muster(jb["room"])
        check("Juna berth prepared and reachable", _juna, failures)

        day1 = load_layout("day1")

        def _repurpose():
            reps = [r for r in lay.rooms.values() if r.get("repurposed_from")]
            assert reps, "no repurposed area on Day 7"
            for r in reps:
                assert r["repurposed_from"] in day1.rooms, \
                    "repurposed_from '%s' names no Day-1 room" % r["repurposed_from"]
                assert day1.rooms[r["repurposed_from"]]["family"] != r["family"], \
                    "repurpose %s did not change family vs Day 1" % r["id"]
        check("repurposed area is a real Day-1 room with a changed family", _repurpose, failures)

        def _upgrade():
            ups = [r for r in lay.rooms.values() if r.get("upgrade")]
            assert ups, "no upgraded facility"
            for r in ups:
                if r["id"] in day1.rooms:
                    assert not day1.rooms[r["id"]].get("upgrade"), \
                        "%s was already upgraded on Day 1" % r["id"]
        check("upgraded facility is genuinely new since Day 1", _upgrade, failures)

        def _seal():
            seal = d.get("seal_bulkhead")
            assert seal and seal.get("portal") in d["portal_states"], \
                "Day 7 must record the Level-1 seal on a real portal (the isolation decision)"
        check("Level-1 seal recorded on a real portal", _seal, failures)

        def _medical():
            med = [r for r in lay.rooms.values() if r["family"] == "medical"]
            assert med, "no medical venue — both routes must hold one (07 S12, D-039)"
            bench_or_cot = any(sp.OBJECTS["objects"][o["type"]]["family"] in ("workstation", "rest_point")
                               and o.get("room") in {m["id"] for m in med}
                               for o in lay.objects.values())
            assert bench_or_cot, "the medical venue holds no treatment equipment"
        check("medical venue exists with treatment equipment (both routes)", _medical, failures)

        def _module():
            assert any(r.get("module_of") for r in lay.rooms.values()), "no attached module"
        check("at least one module", _module, failures)

        def _trunk():
            live = [t for t, s in d["trunk_states"].items() if s == "live"]
            assert len(live) >= 2, "no utility extension beyond the core trunk"
        check("utility trunk extended", _trunk, failures)

        def _route():
            opened = [p for p, s in d["portal_states"].items() if s == "open"]
            lifts = [l for l, s in d["link_states"].items()
                     if l == "freight_lift" and s == "operational"]
            assert opened or lifts, "no new route opened by Day 7"
        check("new route exists", _route, failures)

        if d["route"] == "east":
            def _east():
                fams = {r["family"] for r in lay.rooms.values()}
                assert {"rest", "medical", "food"} <= fams
                assert any(r["id"] == "aid_car" for r in lay.rooms.values()), \
                    "east must build real triage (the Aid Car)"
            check("east-route requirements (comfort first)", _east, failures)
        if d["route"] == "west":
            def _west():
                specs = {r.get("specialization") for r in lay.rooms.values()}
                assert "water" in specs, "west must hold the water infrastructure"
                ids = {r["id"] for r in lay.rooms.values()}
                assert {"cistern_works", "pump_room"} <= ids
            check("west-route requirements (water first)", _west, failures)

    def _families():
        used = {r["family"] for r in lay.rooms.values()}
        assert used <= set(FAMILIES["slice_families"]), "unknown family in layout"
        assert len(set(FAMILIES["slice_families"])) <= 8, "slice family count exceeds 8"
    check("room families within the slice set", _families, failures)

    def _save():
        d2 = Layout.from_dict(lay.to_dict()).to_dict()
        assert d2 == lay.to_dict(), "layout save/reload round-trip diverged"
    check("save/reload round-trip identical", _save, failures)

    m = lay.metrics()
    print("  metrics: avg_path=%s longest_essential=%s entrance->medical=%s storage->workshop=%s"
          % (m["avg_path"], m["longest_essential"], m["entrance_to_medical"],
             m["storage_to_workshop"]))
    print("  noise_distance(rest)=%s backed_up=%s spof=%s"
          % (m["noise_distance_rest"], m["backed_up_rooms"], sorted(m["spof_edges"])))
    print()


def main():
    failures = []
    for name in ("day1", "east_day7", "west_day7"):
        validate(name, failures)
    if failures:
        print("VALIDATION FAILED (%d):" % len(failures))
        for f in failures:
            print("  - " + f)
        return 1
    print("ALL LAYOUTS VALID (structural consistency only — feel is a prototype question)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
