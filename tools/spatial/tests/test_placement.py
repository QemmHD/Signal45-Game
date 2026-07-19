from __future__ import annotations

import copy
import json
import unittest

from tools.spatial.model import room_cells
from tools.spatial.placement import (
    activate_blueprint, apply_construction_work, cancel_blueprint,
    complete_blueprint, deconstruct_once, deliver_blueprint, new_blueprint,
    repurpose_room, save_inactive_blueprint, validate_module,
    validate_object_placement, validate_portal_change, validate_room_placement, validate_severe_access,
)
from tools.spatial.tests.helpers import DATA, layout_with_room, object_probe, room_probe


class PlacementTests(unittest.TestCase):
    def setUp(self) -> None:
        self.day1 = copy.deepcopy(DATA.layout("day1"))

    def codes(self, result: dict) -> set[str]:
        return {item["code"] for item in result["reasons"]}

    def test_fixed_column_overlap_is_rejected(self) -> None:
        room = room_probe(x_start=3, x_end=3)
        self.assertIn("overlaps_fixed_architecture", self.codes(validate_room_placement(DATA, self.day1, room)))

    def test_track_edge_and_buildable_boundary_are_rejected(self) -> None:
        room = room_probe(); room["footprint"] = {"level": 0, "x_start": 10, "x_end": 10, "lanes": [2]}
        result = validate_room_placement(DATA, self.day1, room)
        self.assertIn("overlaps_fixed_architecture", self.codes(result))
        self.assertIn("outside_buildable_area", self.codes(result))

    def test_valid_room_and_room_overlap_differ(self) -> None:
        valid = room_probe()
        self.assertTrue(validate_room_placement(DATA, self.day1, valid)["valid"])
        layout = copy.deepcopy(self.day1); layout["rooms"].append(valid)
        other = room_probe("medical")
        self.assertIn("overlaps_room", self.codes(validate_room_placement(DATA, layout, other)))

    def test_object_overlap_is_rejected(self) -> None:
        layout, room = layout_with_room("rest")
        first = object_probe("bedroll", room); layout["objects"].append(first)
        second = object_probe("quiet_bunk", room)
        self.assertIn("overlaps_object", self.codes(validate_object_placement(DATA, layout, second)))

    def test_object_must_stay_inside_room(self) -> None:
        layout, room = layout_with_room("rest")
        result = validate_object_placement(DATA, layout, object_probe("bedroll", room, 12))
        self.assertFalse(result["valid"])

    def test_interaction_clearance_is_executed(self) -> None:
        layout, room = layout_with_room("rest")
        blocker = object_probe("temporary_barrier", room)
        blocker["anchor"]["lane"] = 1; blocker["room_instance_id"] = None
        layout["objects"].append(blocker)
        result = validate_object_placement(DATA, layout, object_probe("bedroll", room))
        self.assertIn("blocks_interaction_point", self.codes(result))

    def test_utility_requirement_requires_served_section(self) -> None:
        layout, room = layout_with_room("rest")
        layout["utility_nodes"] = [node for node in layout["utility_nodes"] if node["utility"] != "Air"]
        result = validate_object_placement(DATA, layout, object_probe("bedroll", room))
        self.assertIn("missing_utility_node", self.codes(result))

    def test_only_route_resident_essential_and_emergency_refusals(self) -> None:
        gate_block = {("main_gate", 0, 1, 0), ("main_gate", 0, 1, 1)}
        codes = self.codes(validate_severe_access(DATA, self.day1, gate_block))
        self.assertTrue({"blocks_only_route", "strands_essential_room", "blocks_emergency_path"} <= codes)
        resident_block = {("central_platform", 0, 7, 0), ("central_platform", 0, 7, 1)}
        self.assertIn("strands_resident", self.codes(validate_severe_access(DATA, self.day1, resident_block)))

    def test_portal_closure_previews_and_refuses_trapping(self) -> None:
        result = validate_portal_change(DATA, self.day1, "gate_central_primary", "isolated")
        self.assertFalse(result["valid"])
        self.assertIn("blocks_emergency_path", self.codes(result))
        self.assertTrue(result["preview"]["rooms_affected"])

    def test_sequential_legal_blockers_cannot_combine_to_strand_room(self) -> None:
        layout = copy.deepcopy(self.day1)
        first_cells = {("central_platform", 0, 7, 0)}
        self.assertTrue(validate_severe_access(DATA, layout, first_cells)["valid"])
        layout["objects"].append({
            "instance_id": "first_barrier", "object_id": "temporary_barrier",
            "section_id": "central_platform", "anchor": {"section_id": "central_platform", "level": 0, "x": 7, "lane": 0},
            "rotation": 0, "state": "operational", "room_instance_id": None, "utility_connection": None,
        })
        second_cells = {("central_platform", 0, 7, 1)}
        result = validate_severe_access(DATA, layout, second_cells)
        self.assertFalse(result["valid"])
        self.assertIn("strands_resident", self.codes(result))

    def test_blueprint_preview_and_saved_plan_spend_nothing(self) -> None:
        stocks = {"Materials": 10.0}
        blueprint = new_blueprint("probe", room_cells(DATA.station, room_probe()), 4.0, 5.0)
        self.assertEqual(stocks["Materials"], 10.0)
        save_inactive_blueprint(blueprint)
        self.assertEqual(blueprint["materials_reserved"], 0.0)

    def test_activation_and_delivery_are_idempotent(self) -> None:
        stocks = {"Materials": 10.0}; blueprint = new_blueprint("probe", set(), 4.0, 5.0)
        save_inactive_blueprint(blueprint)
        self.assertTrue(activate_blueprint(blueprint, stocks))
        self.assertFalse(activate_blueprint(blueprint, stocks))
        self.assertEqual(stocks["Materials"], 6.0)
        self.assertTrue(deliver_blueprint(blueprint))
        self.assertFalse(deliver_blueprint(blueprint))
        self.assertEqual(blueprint["materials_delivered"], 4.0)

    def test_partial_construction_persists_exactly(self) -> None:
        stocks = {"Materials": 10.0}; blueprint = new_blueprint("probe", set(), 4.0, 5.0)
        save_inactive_blueprint(blueprint); activate_blueprint(blueprint, stocks); deliver_blueprint(blueprint)
        self.assertEqual(apply_construction_work(blueprint, 2.25), 2.25)
        restored = json.loads(json.dumps(blueprint))
        self.assertEqual(restored["work_applied"], 2.25)

    def test_completion_grants_capability_once(self) -> None:
        stocks = {"Materials": 10.0}; blueprint = new_blueprint("probe", set(), 4.0, 5.0)
        save_inactive_blueprint(blueprint); activate_blueprint(blueprint, stocks); deliver_blueprint(blueprint); apply_construction_work(blueprint, 5.0)
        self.assertTrue(complete_blueprint(blueprint))
        self.assertFalse(complete_blueprint(blueprint))
        self.assertTrue(blueprint["capability_granted"])

    def test_cancellation_refunds_only_undelivered_value_once(self) -> None:
        stocks = {"Materials": 10.0}; blueprint = new_blueprint("probe", set(), 4.0, 5.0)
        save_inactive_blueprint(blueprint); activate_blueprint(blueprint, stocks)
        self.assertEqual(cancel_blueprint(blueprint, stocks, 1.0), 4.0)
        self.assertEqual(cancel_blueprint(blueprint, stocks, 1.0), 0.0)
        self.assertEqual(stocks["Materials"], 10.0)

    def test_deconstruction_has_bounded_single_salvage(self) -> None:
        state = {"instance_id": "probe", "state": "operational"}; stocks = {"Materials": 0.0}
        self.assertEqual(deconstruct_once(state, stocks, 10.0, 0.9), 7.5)
        self.assertEqual(deconstruct_once(state, stocks, 10.0, 0.9), 0.0)
        self.assertEqual(stocks["Materials"], 7.5)

    def test_repurpose_is_blocked_during_active_incident(self) -> None:
        room = copy.deepcopy(self.day1["rooms"][3])
        self.assertFalse(repurpose_room(room, "food", incident_active=True))
        self.assertTrue(repurpose_room(room, "food", incident_active=False))
        self.assertEqual(room["family_id"], "food")

    def test_module_requires_parent_and_enforces_capacity(self) -> None:
        module = {"instance_id": "upgrade", "module_id": "platform_lighting_upgrade", "parent_type": "object", "parent_instance_id": "platform_work_lamp", "socket_type": "lighting_upgrade", "state": "operational", "unique": True}
        self.assertTrue(validate_module(self.day1, module, DATA.objects)["valid"])
        self.day1["modules"].append(copy.deepcopy(module)); module["instance_id"] = "duplicate"
        self.assertFalse(validate_module(self.day1, module, DATA.objects)["valid"])
        module["parent_type"] = "module"
        self.assertFalse(validate_module(self.day1, module, DATA.objects)["valid"])


if __name__ == "__main__":
    unittest.main()
