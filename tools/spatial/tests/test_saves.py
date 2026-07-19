from __future__ import annotations

import copy
import json
import unittest

from tools.spatial.model import restore_layout_state, serialize_layout_state
from tools.spatial.placement import activate_blueprint, apply_construction_work, deliver_blueprint, new_blueprint, save_inactive_blueprint
from tools.spatial.tests.helpers import DATA
from tools.spatial.utilities import shed_platform_lighting


class SpatialSaveTests(unittest.TestCase):
    def setUp(self) -> None:
        self.layout = copy.deepcopy(DATA.layout("east_day7"))

    def roundtrip(self) -> dict:
        payload = serialize_layout_state(self.layout)
        restored = restore_layout_state(self.layout, payload)
        self.assertEqual(serialize_layout_state(restored), payload)
        return restored

    def test_layout_roundtrips_exact_logical_geometry(self) -> None:
        restored = self.roundtrip()
        self.assertEqual(restored["rooms"], self.layout["rooms"])
        self.assertEqual(restored["objects"], self.layout["objects"])

    def test_portal_state_roundtrips(self) -> None:
        self.layout["portal_states"]["central_east_primary"] = "isolated"
        self.assertEqual(self.roundtrip()["portal_states"]["central_east_primary"], "isolated")

    def test_utility_connection_and_isolation_roundtrip(self) -> None:
        branch = next(item for item in self.layout["utility_branches"] if item["branch_id"] == "east_air_branch")
        branch["isolated"] = True
        restored = self.roundtrip()
        self.assertTrue(next(item for item in restored["utility_branches"] if item["branch_id"] == "east_air_branch")["isolated"])

    def test_moved_object_roundtrips(self) -> None:
        cabinet = next(item for item in self.layout["objects"] if item["instance_id"] == "east_entry_cabinet")
        cabinet["anchor"]["x"] = 1
        restored = self.roundtrip()
        self.assertEqual(next(item for item in restored["objects"] if item["instance_id"] == "east_entry_cabinet")["anchor"]["x"], 1)

    def test_platform_lighting_shed_state_roundtrips(self) -> None:
        shed_platform_lighting(self.layout)
        restored = self.roundtrip()
        consumer = next(item for item in restored["utility_consumers"] if item["consumer_id"] == "platform_lighting")
        self.assertEqual(consumer["state"], "shed")

    def test_hope_anchor_roundtrips_without_stock_payload(self) -> None:
        restored = self.roundtrip()
        self.assertEqual(restored["hope_anchors"], self.layout["hope_anchors"])
        self.assertTrue(all("stock" not in anchor for anchor in restored["hope_anchors"]))

    def test_partial_blueprint_serialization_preserves_progress(self) -> None:
        blueprint = new_blueprint("probe", {("central_platform", 0, 10, 0)}, 4.0, 5.0)
        stocks = {"Materials": 10.0}; save_inactive_blueprint(blueprint); activate_blueprint(blueprint, stocks); deliver_blueprint(blueprint); apply_construction_work(blueprint, 2.5)
        self.layout["blueprints"].append(blueprint)
        restored = self.roundtrip()
        saved = next(item for item in restored["blueprints"] if item["project_id"] == "probe")
        self.assertEqual(saved["work_applied"], 2.5)
        self.assertIn("probe:delivery", saved["transactions"])

    def test_render_handles_and_path_caches_are_not_serialized(self) -> None:
        payload = json.loads(serialize_layout_state(self.layout))
        serialized = json.dumps(payload)
        self.assertNotIn("render_object", serialized)
        self.assertNotIn("path_cache", serialized)
        self.assertNotIn("animation_handle", serialized)


if __name__ == "__main__":
    unittest.main()
