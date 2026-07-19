from __future__ import annotations

import unittest

from tools.spatial.model import derive_functional_area_count, derive_room_families
from tools.spatial.tests.helpers import DATA
from tools.spatial.travel import calculate_travel_metrics
from tools.spatial.validate_layouts import run_validation


class AuthoritativeLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = run_validation()

    def test_all_machine_readable_layouts_validate(self) -> None:
        self.assertTrue(self.report["valid"], self.report["errors"])
        self.assertEqual(set(self.report["layouts"]), {"day1", "east_day7", "east_day7_alternate", "west_day7", "west_day7_alternate", "poor_valid"})

    def test_derived_area_counts_are_four_ten_ten(self) -> None:
        self.assertEqual(derive_functional_area_count(DATA.layout("day1")), 4)
        self.assertEqual(derive_functional_area_count(DATA.layout("east_day7")), 10)
        self.assertEqual(derive_functional_area_count(DATA.layout("west_day7")), 10)

    def test_temporary_medical_zone_does_not_add_area(self) -> None:
        day1 = DATA.layout("day1")
        self.assertFalse(any(room["family_id"] == "medical" and room.get("counts_as_area") for room in day1["rooms"]))
        self.assertEqual(derive_functional_area_count(day1), 4)

    def test_day_seven_layouts_use_exactly_seven_families(self) -> None:
        for layout_id in ["east_day7", "east_day7_alternate", "west_day7", "west_day7_alternate", "poor_valid"]:
            with self.subTest(layout=layout_id):
                self.assertEqual(len(derive_room_families(DATA.layout(layout_id))), 7)

    def test_alternates_change_functional_room_placement(self) -> None:
        east = {room["instance_id"]: room["footprint"] for room in DATA.layout("east_day7")["rooms"]}
        east_alt = {room["instance_id"]: room["footprint"] for room in DATA.layout("east_day7_alternate")["rooms"]}
        west = {room["instance_id"]: room["footprint"] for room in DATA.layout("west_day7")["rooms"]}
        west_alt = {room["instance_id"]: room["footprint"] for room in DATA.layout("west_day7_alternate")["rooms"]}
        self.assertNotEqual(east, east_alt)
        self.assertNotEqual(west, west_alt)

    def test_poor_valid_layout_is_valid_but_has_worse_factor(self) -> None:
        canonical = calculate_travel_metrics(DATA, DATA.layout("east_day7"))
        poor = calculate_travel_metrics(DATA, DATA.layout("poor_valid"))
        self.assertTrue(self.report["layouts"]["poor_valid"]["valid"])
        self.assertGreater(poor["coordinate_travel_factor"], canonical["coordinate_travel_factor"])
        self.assertGreater(poor["coordinate_hauling_factor"], canonical["coordinate_hauling_factor"])

    def test_route_identity_uses_multiple_physical_metrics(self) -> None:
        east = calculate_travel_metrics(DATA, DATA.layout("east_day7"))
        west = calculate_travel_metrics(DATA, DATA.layout("west_day7"))
        self.assertLess(west["pump_service_path"], east["pump_service_path"])
        self.assertLess(west["water_isolation_path"], east["water_isolation_path"])
        self.assertLess(west["materials_delivery_path"], east["materials_delivery_path"])
        self.assertLess(east["rest_to_work_path"], west["rest_to_work_path"])
        self.assertGreater(east["gate_to_medical_path"], west["gate_to_medical_path"])

    def test_day_five_paths_fit_declared_proxy_budget(self) -> None:
        for layout_id in ["east_day7", "west_day7"]:
            layout = DATA.layout(layout_id); metrics = calculate_travel_metrics(DATA, layout)
            self.assertLessEqual(metrics["day5_max_response_path"], layout["day5_response_budget"])

    def test_future_vertical_route_is_visible_but_not_functional_area(self) -> None:
        for layout_id in ["day1", "east_day7", "west_day7"]:
            layout = DATA.layout(layout_id)
            self.assertEqual(layout["portal_states"]["east_vertical_link"], "sealed")
            self.assertNotIn("vertical_shaft", {room["section_id"] for room in layout["rooms"] if room.get("counts_as_area")})

    def test_hope_anchors_are_physical_earned_and_nonresource(self) -> None:
        for layout_id in ["east_day7", "west_day7"]:
            layout = DATA.layout(layout_id)
            tiers = {anchor["tier"] for anchor in layout["hope_anchors"]}
            self.assertTrue({"minimal", "full"} <= tiers)
            self.assertTrue(all(not anchor["grants_stock"] and not anchor["clears_consequences"] for anchor in layout["hope_anchors"]))

    def test_rendering_is_explicitly_non_authoritative(self) -> None:
        self.assertFalse(DATA.station["metadata"]["rendering_is_authoritative"])
        self.assertIn("world_transform", DATA.station["coordinate_contract"]["derived_not_persisted"])


if __name__ == "__main__":
    unittest.main()
