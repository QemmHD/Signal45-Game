#!/usr/bin/env python3
"""Automated checks for the SIGNAL 45 spatial model (Prompt 4, D-046).

Every test asserts an actual computed outcome. Tests that execute a design rule
(the reservation arithmetic) execute it as arithmetic — none compares an object
to its own unchanged copy, and none can pass vacuously. Structural consistency
only: none of this proves the building system is fun.

Run:  python3 tools/test_spatial_model.py
"""

import copy
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import spatial_model as sp
import validate_station_layouts as vsl


def lay(name):
    return sp.load_layout(name)


class Coordinates(unittest.TestCase):
    def test_sections_and_fixed_cells_are_in_grid(self):
        st = sp.Station()
        for sid, sec in st.sections.items():
            w, h = sec["grid"]
            self.assertGreater(w * h, 0)
            for c in st._fixed[sid]:
                self.assertTrue(st.in_grid(sid, c),
                                "%s fixed cell %s outside its grid" % (sid, str(c)))

    def test_bay_arithmetic(self):
        st = sp.Station()
        for sid, sec in st.sections.items():
            self.assertLessEqual(sec["bays"] * sp.SECTIONS["bay_cells"], sec["grid"][0] + 3,
                                 "%s claims more bays than its grid holds" % sid)

    def test_rotation_math(self):
        w, h, cells = sp.rotate_footprint(2, 1, [(0, 1), (1, 1)], 90)
        self.assertEqual((w, h), (1, 2))
        self.assertEqual(len(cells), 2)
        w2, h2, cells2 = sp.rotate_footprint(2, 1, [(0, 1), (1, 1)], 180)
        self.assertEqual((w2, h2), (2, 1))
        self.assertNotEqual(cells2, [(0, 1), (1, 1)], "180-degree rotation must flip sides")


class Placement(unittest.TestCase):
    def test_place_bed_in_valid_rest_area(self):
        l = lay("east_day7")
        bed = {"id": "t_bed", "type": "bedroll", "room": "sleeper_car", "pos": [8, 2], "rot": 0}
        self.assertTrue(l.place_object(bed))

    def test_reject_bed_blocking_only_door(self):
        # a bed dropped across the signal box's only entrance (the ladder head)
        l = lay("east_day7")
        bad = {"id": "t_block", "type": "bunk_bed", "room": None,
               "section": "signal_box", "pos": [0, 0], "rot": 0}   # covers the ladder cell (0,1)
        with self.assertRaises(sp.ValidationError) as cm:
            l.place_object(bad)
        self.assertIn("stair/lift/portal", str(cm.exception))

    def test_enclosure_at_distance_strands_and_is_refused(self):
        # three legal-looking placements must NOT combine into a silent pocket:
        # reachability, not cell coverage, is the strand criterion (D-048)
        l = lay("east_day7")
        b1 = {"id": "t_p1", "type": "barricade", "room": None,
              "section": "east_concourse", "pos": [13, 1], "rot": 0}
        l.place_object(b1)
        b2 = {"id": "t_p2", "type": "barricade", "room": None,
              "section": "east_concourse", "pos": [13, 3], "rot": 0}
        with self.assertRaises(sp.ValidationError) as cm:
            l.place_object(b2)   # would seal the Cold Store pocket at distance
        self.assertIn("strand", str(cm.exception))

    def test_reject_furniture_stranding_existing_equipment(self):
        # sealing both working cells of the equipment locker's shelf darkens it —
        # refused before confirm (furniture cannot silently disable a room)
        l = lay("east_day7")
        b1 = {"id": "t_b1", "type": "barricade", "room": None,
              "section": "deep_service", "pos": [9, 2], "rot": 0}
        l.place_object(b1)
        b2 = {"id": "t_b2", "type": "barricade", "room": None,
              "section": "deep_service", "pos": [10, 2], "rot": 0}
        with self.assertRaises(sp.ValidationError) as cm:
            l.place_object(b2)
        self.assertIn("strand", str(cm.exception))

    def test_corridor_severance_refused_even_at_one_cell(self):
        # the deep-service corridor's one crossing cell: blocking it severs the
        # whole right half — the guard must refuse the FIRST placement
        l = lay("east_day7")
        b1 = {"id": "t_sever", "type": "barricade", "room": None,
              "section": "deep_service", "pos": [1, 2], "rot": 0}
        with self.assertRaises(sp.ValidationError):
            l.place_object(b1)

    def test_workstation_with_clear_interaction(self):
        l = lay("day1")
        wb = {"id": "t_wb", "type": "workbench", "room": None,
              "section": "scrubber_gate", "pos": [3, 0], "rot": 0}
        self.assertTrue(l.place_object(wb))

    def test_reject_workstation_against_blocked_side(self):
        l = lay("day1")
        # bench with its working side against the track bed: no clear interaction
        wb = {"id": "t_wb2", "type": "workbench", "room": None,
              "section": "central_platform", "pos": [2, 2], "rot": 0}
        with self.assertRaises(sp.ValidationError) as cm:
            l.place_object(wb)
        self.assertIn("interaction", str(cm.exception))

    def test_reject_on_structural_obstacle(self):
        l = lay("day1")
        bad = {"id": "t_col", "type": "supply_crate", "room": None,
              "section": "central_platform", "pos": [3, 0], "rot": 0}   # column cell
        with self.assertRaises(sp.ValidationError) as cm:
            l.place_object(bad)
        self.assertIn("fixed architecture", str(cm.exception))

    def test_reject_outside_buildable_area(self):
        l = lay("day1")
        room = {"id": "t_room", "family": "storage", "form": "permanent",
                "section": "central_platform", "rect": {"x": 0, "y": 3, "w": 2, "h": 1}}
        l.rooms[room["id"]] = room
        with self.assertRaises(sp.ValidationError):
            l.validate_room(room)   # track bed is not buildable

    def test_reject_object_overlap(self):
        l = lay("day1")
        dup = {"id": "t_dup", "type": "supply_crate", "room": "supply_zone", "pos": [12, 1], "rot": 0}
        with self.assertRaises(sp.ValidationError) as cm:
            l.place_object(dup)
        self.assertIn("occupied", str(cm.exception))

    def test_reject_blocking_a_stair_cell(self):
        l = lay("day1")
        bad = {"id": "t_stair", "type": "barricade", "room": None,
              "section": "central_platform", "pos": [8, 0], "rot": 0}   # gate stair cell
        with self.assertRaises(sp.ValidationError) as cm:
            l.place_object(bad)
        self.assertIn("stair/lift/portal", str(cm.exception))

    def test_rotate_nonsquare_object_changes_cells(self):
        l = lay("east_day7")
        t0 = {"id": "t_rot", "type": "canteen_table", "room": None,
              "section": "east_concourse", "pos": [1, 0], "rot": 0}
        t90 = dict(t0, rot=90)
        self.assertNotEqual(l.object_cells(t0), l.object_cells(t90))
        self.assertEqual(len(l.object_cells(t90)), 2)

    def test_move_object_and_failed_move_restores(self):
        l = lay("day1")
        self.assertTrue(l.move_object("crate_1", [14, 1]))
        self.assertEqual(l.objects["crate_1"]["pos"], [14, 1])
        with self.assertRaises(sp.ValidationError):
            l.move_object("crate_1", [3, 0])   # onto a column
        self.assertEqual(l.objects["crate_1"]["pos"], [14, 1], "failed move must restore")

    def test_store_object(self):
        l = lay("day1")
        o = l.store_object("crate_2")
        self.assertTrue(o["stored"])
        self.assertNotIn("crate_2", l.objects)

    def test_equipment_room_compatibility(self):
        l = lay("west_day7")
        bad = {"id": "t_cot", "type": "med_cot", "room": "cold_store", "pos": [14, 1], "rot": 0}
        with self.assertRaises(sp.ValidationError) as cm:
            l.place_object(bad)
        self.assertIn("does not belong", str(cm.exception))


class RoomsAndModules(unittest.TestCase):
    def test_repurpose_room_stores_incompatible_equipment(self):
        l = lay("day1")
        displaced = l.repurpose_room("camp", "operations", "staging")
        self.assertEqual(l.rooms["camp"]["family"], "operations")
        self.assertEqual(l.rooms["camp"]["repurposed_from"], "rest")
        self.assertTrue(displaced, "bedrolls must be displaced-and-stored, not destroyed")
        for oid in displaced:
            self.assertNotIn(oid, l.objects, "stored equipment must leave the floor")
        # the layout stays fully navigable after the verb (no corrupt state)
        for fac in l.d["essential_facilities"]:
            self.assertTrue(l.reachable_from_muster(fac))

    def test_repurpose_validates_before_committing(self):
        l = lay("west_day7")
        before = json.dumps(l.to_dict(), sort_keys=True)
        with self.assertRaises(sp.ValidationError):
            # the 1x2 feature-built Cistern Works cannot become a Food room
            # (below the family minimum) — the verb must refuse BEFORE mutating
            l.repurpose_room("cistern_works", "food")
        self.assertEqual(json.dumps(l.to_dict(), sort_keys=True), before,
                         "a refused repurpose must leave the layout untouched")

    def test_attach_valid_module(self):
        l = lay("east_day7")
        self.assertTrue(l.validate_room(l.rooms["canteen_pantry"]))

    def test_reject_detached_module(self):
        l = lay("east_day7")
        bad = {"id": "t_mod", "family": "food", "form": "module", "module_of": "canteen",
               "section": "east_concourse", "rect": {"x": 0, "y": 0, "w": 2, "h": 1}}
        l.rooms[bad["id"]] = bad
        with self.assertRaises(sp.ValidationError) as cm:
            l.validate_room(bad)
        self.assertIn("touch its parent", str(cm.exception))

    def test_reject_room_without_utility_service(self):
        # a powered room in a dark-trunk section must be refused with a CONNECT hint
        l = lay("day1")
        room = {"id": "t_can", "family": "food", "form": "kiosk", "shell": "kiosk_row",
                "section": "east_concourse", "rect": {"x": 8, "y": 0, "w": 4, "h": 2}}
        l.rooms[room["id"]] = room
        with self.assertRaises(sp.ValidationError) as cm:
            l.validate_room(room)
        self.assertIn("trunk", str(cm.exception))

    def test_feature_built_needs_its_anchor(self):
        l = lay("day1")
        bad = {"id": "t_feat", "family": "utility", "specialization": "water",
               "form": "feature_built", "feature": "cistern_main",
               "section": "west_gallery", "rect": {"x": 10, "y": 0, "w": 2, "h": 2}}
        l.rooms[bad["id"]] = bad
        with self.assertRaises(sp.ValidationError) as cm:
            l.validate_room(bad)
        self.assertIn("anchor", str(cm.exception))


class RestrictionsAndSockets(unittest.TestCase):
    def test_module_of_module_rejected(self):
        l = lay("east_day7")
        bad = {"id": "t_chain", "family": "food", "form": "module", "module_of": "canteen_pantry",
               "section": "east_concourse", "rect": {"x": 12, "y": 1, "w": 1, "h": 1}}
        l.rooms[bad["id"]] = bad
        with self.assertRaises(sp.ValidationError) as cm:
            l.validate_room(bad)
        self.assertIn("not another module", str(cm.exception))

    def test_storage_sockets_enforced(self):
        l = lay("east_day7")
        extra = {"id": "t_shelf", "type": "storage_shelf", "room": "aid_car", "pos": [3, 3], "rot": 0}
        with self.assertRaises(sp.ValidationError) as cm:
            l.place_object(extra)   # the cabinet already fills medical's one storage socket
        self.assertIn("storage sockets full", str(cm.exception))

    def test_blocking_object_rejected_on_circulation(self):
        l = lay("day1")
        bad = {"id": "t_shelf2", "type": "storage_shelf", "room": None,
               "section": "scrubber_gate", "pos": [1, 1], "rot": 0}   # the decon channel
        with self.assertRaises(sp.ValidationError) as cm:
            l.place_object(bad)
        self.assertIn("buildable", str(cm.exception))

    def test_door_panel_only_in_portal_or_gap(self):
        l = lay("east_day7")
        bad = {"id": "t_door", "type": "door_panel", "room": None,
               "section": "east_concourse", "pos": [2, 1], "rot": 0}
        with self.assertRaises(sp.ValidationError) as cm:
            l.place_object(bad)
        self.assertIn("portal or a partition gap", str(cm.exception))

    def test_partition_is_interior_only(self):
        l = lay("day1")
        bad = {"id": "t_part", "type": "partition", "room": None,
               "section": "central_platform", "pos": [12, 0], "rot": 0}
        with self.assertRaises(sp.ValidationError) as cm:
            l.place_object(bad)
        self.assertIn("interior-only", str(cm.exception))

    def test_purifier_needs_its_tank(self):
        l = lay("day1")
        bad = {"id": "t_pur", "type": "purifier_unit", "room": None,
               "section": "central_platform", "pos": [12, 0], "rot": 0}
        with self.assertRaises(sp.ValidationError) as cm:
            l.place_object(bad)
        self.assertIn("tank", str(cm.exception))

    def test_story_objects_can_never_be_removed(self):
        l = lay("day1")
        with self.assertRaises(sp.ValidationError) as cm:
            l.store_object("timetable_board")
        self.assertIn("story", str(cm.exception))

    def test_powered_object_needs_live_trunk(self):
        l = lay("day1")
        bad = {"id": "t_hot", "type": "hotplate_counter", "room": None,
               "section": "east_concourse", "pos": [1, 0], "rot": 0}
        with self.assertRaises(sp.ValidationError) as cm:
            l.place_object(bad)
        self.assertIn("dark", str(cm.exception))

    def test_close_door_warns_of_severance_and_reopens(self):
        l = lay("east_day7")
        cut = l.close_door("east_portal")
        self.assertIn("sleeper_car", cut)   # the warn-before channel for state changes
        l.open_door("east_portal")
        self.assertTrue(l.reachable_from_muster("sleeper_car"))

    def test_shift_log_reveal_anchor_placed_both_routes(self):
        for name in ("east_day7", "west_day7"):
            l = lay(name)
            self.assertIn("shift_log_1", l.objects, name)
            self.assertEqual(l.object_section(l.objects["shift_log_1"]), "deep_service")

    def test_junas_corner_keeps_its_lamp(self):
        l = lay("west_day7")
        lamp = l.objects["comfort_lamp_2"]
        bunk_cells = {tuple(c) for c in l.object_cells(l.objects["bunk_w3"])}
        lc = tuple(lamp["pos"])
        near = any(abs(lc[0] - b[0]) + abs(lc[1] - b[1]) <= 1 for b in bunk_cells)
        self.assertTrue(near, "the candle line's anchor must sit beside Juna's bunk")

    def test_medical_venue_on_both_routes(self):
        for name in ("day1", "east_day7", "west_day7"):
            l = lay(name)
            med = [r for r in l.rooms.values() if r["family"] == "medical"]
            self.assertTrue(med, "%s has no medical venue" % name)

    def test_headroom_honest_bounds(self):
        d1, e7 = lay("day1"), lay("east_day7")
        self.assertGreaterEqual(sp.utility_headroom(d1) + sp.sheddable_load(d1), 0)
        self.assertGreaterEqual(sp.utility_headroom(e7), 0)


class Navigation(unittest.TestCase):
    def test_day1_essential_facilities_reachable(self):
        l = lay("day1")
        for fac in l.d["essential_facilities"]:
            self.assertTrue(l.reachable_from_muster(fac), fac)

    def test_day1_deep_service_unreachable_lift_jammed(self):
        l = lay("day1")
        self.assertIsNone(l.path(l.muster(), ("deep_service", (1, 0))),
                          "jammed lift must isolate the Deep Service Level")

    def test_lift_restoration_opens_the_level(self):
        l = lay("day1")
        l.d["link_states"]["freight_lift"] = "operational"
        self.assertIsNotNone(l.path(l.muster(), ("deep_service", (1, 0))))

    def test_day7_layouts_fully_navigable(self):
        for name in ("east_day7", "west_day7"):
            l = lay(name)
            for fac in l.d["essential_facilities"]:
                self.assertTrue(l.reachable_from_muster(fac), "%s: %s" % (name, fac))

    def test_emergency_paths_exist_everywhere(self):
        for name in ("east_day7", "west_day7"):
            l = lay(name)
            for r in l.rooms.values():
                if r.get("module_of"):
                    continue
                length, _, _ = l.emergency_path(r["id"])
                self.assertIsNotNone(length, "%s: %s has no emergency path" % (name, r["id"]))

    def test_hazard_closure_severs_and_recovery_restores(self):
        l = lay("east_day7")
        l.d["portal_states"]["east_portal"] = "closed"      # storm bulkhead sealed
        self.assertFalse(l.reachable_from_muster("sleeper_car"))
        l.d["portal_states"]["east_portal"] = "open"        # the recovery verb
        self.assertTrue(l.reachable_from_muster("sleeper_car"))

    def test_vertical_connection_both_day7(self):
        for name in ("east_day7", "west_day7"):
            l = lay(name)
            self.assertIsNotNone(l.path(l.muster(), ("deep_service", (1, 0))), name)

    def test_no_placement_may_sever_the_shelter(self):
        l = lay("east_day7")
        bad = {"id": "t_wall", "type": "barricade", "room": None,
              "section": "east_concourse", "pos": [0, 0], "rot": 0}
        # (0,1) is the portal cell (protected); (0,0) narrows the mouth — legal.
        l.place_object(bad)
        bad2 = {"id": "t_wall2", "type": "barricade", "room": None,
               "section": "east_concourse", "pos": [1, 1], "rot": 0}
        with self.assertRaises(sp.ValidationError) as cm:
            l.place_object(bad2)   # with (0,0) walled, (1,1) seals the whole east wing
        self.assertIn("cut off", str(cm.exception))

    def test_spof_metric_names_single_points_of_failure(self):
        # the slice shell is single-route by authored design (25 S4): the metric
        # must SAY so, not hide it — sleeper_car's only route is the east portal
        l = lay("east_day7")
        _, alts, spof = l.emergency_path("sleeper_car")
        self.assertIn("east_portal", spof)
        m = l.metrics()
        self.assertIsNotNone(m["avg_path"])
        self.assertIsNotNone(m["storage_to_workshop"])
        self.assertIn("flywheel_room", m["backed_up_rooms"],
                      "the battery bank must back up its room (the adjacency object)")

    def test_railcar_roles_embody_the_noise_travel_tradeoff(self):
        # the railcar-role decision (10 S15): the sleeper sits farther from the
        # noisy service side than the aid car — measurable, not asserted
        l = lay("east_day7")
        self.assertGreater(l.noise_distance("sleeper_car"), l.noise_distance("aid_car"))

    def test_railcar_roles_are_swappable(self):
        # the OTHER arrangement is equally legal — the decision is real freedom
        l = lay("east_day7")
        sc, ac = l.rooms["sleeper_car"], l.rooms["aid_car"]
        sc["rect"], ac["rect"] = ac["rect"], sc["rect"]
        sc["shell"], ac["shell"] = ac["shell"], sc["shell"]
        for oid, pos in (("bunk_e1", [0, 2]), ("bunk_e2", [2, 2]), ("bunk_e3", [4, 2]),
                         ("cot_e1", [7, 2]), ("cot_e2", [9, 2]), ("med_cabinet_1", [11, 2])):
            l.objects[oid]["pos"] = pos
        for r in (sc, ac):
            self.assertTrue(l.validate_room(r))
        for oid in ("bunk_e1", "bunk_e2", "bunk_e3", "cot_e1", "cot_e2", "med_cabinet_1"):
            self.assertTrue(l.validate_object(l.objects[oid]))
        self.assertTrue(l.reachable_from_muster("sleeper_car"))
        self.assertTrue(l.reachable_from_muster("aid_car"))


class BlueprintLedger(unittest.TestCase):
    def setUp(self):
        self.led = sp.MaterialsLedger(stock=12)

    def test_preview_never_spends(self):
        before = self.led.stock
        self.led.preview("p1", 6)
        self.assertEqual(self.led.stock, before)

    def test_saved_blueprint_reserves_nothing(self):
        self.led.save_blueprint("p1", 6)
        self.assertEqual(self.led.stock, 12)

    def test_activation_reserves(self):
        self.led.save_blueprint("p1", 6)
        self.led.activate("p1")
        self.assertEqual(self.led.stock, 6)
        self.assertEqual(self.led.projects["p1"]["reserved"], 6)

    def test_insufficient_materials_named(self):
        self.led.save_blueprint("p1", 99)
        with self.assertRaises(sp.ValidationError):
            self.led.activate("p1")

    def test_cancel_before_delivery_full_refund(self):
        self.led.save_blueprint("p1", 6)
        self.led.activate("p1")
        refund = self.led.cancel("p1")
        self.assertEqual(refund, 6)
        self.assertEqual(self.led.stock, 12)

    def test_cancel_after_partial_delivery_refunds_reserve_only(self):
        self.led.save_blueprint("p1", 6)
        self.led.activate("p1")
        self.led.deliver_stage("p1", 0.5)
        refund = self.led.cancel("p1")
        self.assertEqual(refund, 3)
        self.assertEqual(self.led.stock, 9, "consumed stages never refund — churn is a net loss")

    def test_deconstruct_returns_half_once(self):
        self.led.save_blueprint("p1", 6)
        self.led.activate("p1")
        self.led.deliver_stage("p1", 1.0)
        self.led.complete("p1")
        back = self.led.deconstruct("p1")
        self.assertEqual(back, 3)
        with self.assertRaises(sp.ValidationError):
            self.led.deconstruct("p1")   # once per component, ever

    def test_no_profit_loop_possible(self):
        # build -> complete -> deconstruct -> rebuild -> ... always loses materials
        start = self.led.stock
        self.led.save_blueprint("p1", 6)
        self.led.activate("p1")
        self.led.deliver_stage("p1", 1.0)
        self.led.complete("p1")
        self.led.deconstruct("p1")
        self.assertLess(self.led.stock, start)
        self.led.save_blueprint("p2", 6)
        self.led.activate("p2")
        self.led.cancel("p2")
        self.assertLess(self.led.stock, start, "cancel after deconstruct must not restore profit")

    def test_complete_requires_active_state(self):
        self.led.save_blueprint("p1", 6)
        with self.assertRaises(sp.ValidationError):
            self.led.complete("p1")          # a blueprint cannot 'complete' free
        self.led.activate("p1")
        self.led.cancel("p1")
        with self.assertRaises(sp.ValidationError):
            self.led.complete("p1")          # cancel -> complete -> deconstruct is dead

    def test_negative_stage_fraction_rejected(self):
        self.led.save_blueprint("p1", 6)
        self.led.activate("p1")
        with self.assertRaises(sp.ValidationError):
            self.led.deliver_stage("p1", -0.5)
        self.assertEqual(self.led.projects["p1"]["reserved"], 6)

    def test_duplicate_reservation_impossible(self):
        self.led.save_blueprint("p1", 6)
        self.led.activate("p1")
        with self.assertRaises(sp.ValidationError):
            self.led.activate("p1")

    def test_partial_construction_save_reload(self):
        self.led.save_blueprint("p1", 6)
        self.led.activate("p1")
        self.led.deliver_stage("p1", 0.5)
        blob = json.dumps({"stock": self.led.stock, "projects": self.led.projects}, sort_keys=True)
        restored = json.loads(blob)
        led2 = sp.MaterialsLedger(restored["stock"])
        led2.projects = restored["projects"]
        led2.cancel("p1")
        self.assertEqual(led2.stock, 9, "reloaded mid-project state must keep exact arithmetic")


class ComfortLightingAndRoutes(unittest.TestCase):
    def test_comfort_lighting_present_and_optional(self):
        for name in ("day1", "east_day7", "west_day7"):
            l = lay(name)
            lamps = [o for o in l.objects.values() if o["type"] == "comfort_lamp"]
            self.assertTrue(lamps, name)
        util = sp._load("utilities.json")
        self.assertEqual(util["power"]["tier_of"]["comfort_lighting"], "optional")
        self.assertEqual(sum(1 for k, v in util["power"]["tier_of"].items() if v == "optional"), 1,
                         "exactly ONE Optional-tier load in the slice (owner directive)")

    def test_juna_berth_both_routes(self):
        for name in ("east_day7", "west_day7"):
            l = lay(name)
            jb = l.d["juna_berth"]
            self.assertIsNotNone(jb, name)
            obj = l.objects[jb["object"]]
            self.assertEqual(sp.OBJECTS["objects"][obj["type"]]["family"], "rest_point")
            self.assertTrue(l.reachable_from_muster(jb["room"]))

    def test_east_and_west_day7_pass_full_battery(self):
        failures = []
        for name in ("day1", "east_day7", "west_day7"):
            vsl.validate(name, failures)
        self.assertEqual(failures, [], "layout battery failures: %s" % failures)

    def test_layout_save_reload_roundtrip_and_after_move(self):
        l = lay("west_day7")
        l.move_object("staging_crate", [6, 1])
        d = l.to_dict()
        l2 = sp.Layout.from_dict(json.loads(json.dumps(d)))
        self.assertEqual(l2.to_dict(), d)
        self.assertEqual(l2.objects["staging_crate"]["pos"], [6, 1])
        for fac in l2.d["essential_facilities"]:
            self.assertTrue(l2.reachable_from_muster(fac))


if __name__ == "__main__":
    unittest.main(verbosity=1)
