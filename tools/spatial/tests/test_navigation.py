from __future__ import annotations

import copy
import unittest

from tools.spatial.navigation import find_path
from tools.spatial.tests.helpers import DATA


class NavigationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.day1 = copy.deepcopy(DATA.layout("day1"))
        self.east = copy.deepcopy(DATA.layout("east_day7"))
        self.west = copy.deepcopy(DATA.layout("west_day7"))

    def test_all_seven_path_classes_find_valid_west_route(self) -> None:
        start = {"section_id": "main_gate", "level": 0, "x": 0, "lane": 1}
        end = {"section_id": "west_pump_gallery", "level": 0, "x": 3, "lane": 1}
        for path_class in DATA.station["path_classes"]:
            with self.subTest(path_class=path_class):
                result = find_path(DATA, self.west, start, end, path_class)
                self.assertTrue(result.found, result.failure_reason)
                self.assertGreater(result.cost, 0)

    def test_patient_carry_rejects_narrow_east_service_door(self) -> None:
        altered = copy.deepcopy(self.east)
        altered["portal_states"]["central_east_primary"] = "isolated"
        result = find_path(DATA, altered, altered["safety_checks"]["main_gate"], altered["safety_checks"]["primary_medical"], "patient_carry")
        self.assertFalse(result.found)

    def test_closed_portal_prevents_unreclaimed_west_access(self) -> None:
        result = find_path(DATA, self.day1, {"section_id": "main_gate", "level": 0, "x": 0, "lane": 1}, {"section_id": "west_pump_gallery", "level": 0, "x": 2, "lane": 1})
        self.assertFalse(result.found)
        self.assertIn(result.failure_reason, {"destination_not_walkable", "portal_closed_or_isolated"})

    def test_isolated_section_removes_paths(self) -> None:
        self.east["portal_states"]["central_east_primary"] = "isolated"
        self.east["portal_states"]["central_east_service"] = "isolated"
        result = find_path(DATA, self.east, self.east["safety_checks"]["safe_area"], self.east["safety_checks"]["primary_medical"])
        self.assertFalse(result.found)

    def test_hazard_is_avoided_when_alternate_lane_exists(self) -> None:
        self.day1["hazards"].append({"hazard_id": "probe", "state": "active", "path_severity": 1, "cells": [{"section_id": "main_gate", "level": 0, "x": 1, "lane": 0}]})
        result = find_path(DATA, self.day1, self.day1["safety_checks"]["main_gate"], self.day1["safety_checks"]["safe_area"])
        self.assertTrue(result.found)
        self.assertEqual(result.hazard_exposure, 0)

    def test_future_vertical_route_is_unavailable(self) -> None:
        result = find_path(DATA, self.east, {"section_id": "east_staff_wing", "level": 0, "x": 9, "lane": 1}, {"section_id": "vertical_shaft", "level": 1, "x": 2, "lane": 0})
        self.assertFalse(result.found)

    def test_portal_restoration_repaths_deterministically(self) -> None:
        restored = copy.deepcopy(self.day1)
        restored["section_states"]["west_pump_gallery"] = {"access": "operational", "discovered": True, "hazard": "none", "blocked_cells": []}
        restored["portal_states"]["west_gate_primary"] = "open"
        first = find_path(DATA, restored, {"section_id": "main_gate", "level": 0, "x": 0, "lane": 1}, {"section_id": "west_pump_gallery", "level": 0, "x": 2, "lane": 1})
        second = find_path(DATA, restored, {"section_id": "main_gate", "level": 0, "x": 0, "lane": 1}, {"section_id": "west_pump_gallery", "level": 0, "x": 2, "lane": 1})
        self.assertTrue(first.found)
        self.assertEqual(first.to_dict(), second.to_dict())

    def test_east_gate_stabilization_and_primary_medical_are_both_reachable(self) -> None:
        stabilization = find_path(DATA, self.east, self.east["safety_checks"]["main_gate"], self.east["safety_checks"]["gate_stabilization"], "patient_escort")
        primary = find_path(DATA, self.east, self.east["safety_checks"]["main_gate"], self.east["safety_checks"]["primary_medical"], "patient_carry")
        self.assertTrue(stabilization.found)
        self.assertTrue(primary.found)
        self.assertLess(stabilization.cost, primary.cost)

    def test_medical_fallback_remains_when_east_primary_route_is_blocked(self) -> None:
        self.east["portal_states"]["central_east_primary"] = "isolated"
        primary = find_path(DATA, self.east, self.east["safety_checks"]["main_gate"], self.east["safety_checks"]["primary_medical"], "patient_carry")
        fallback = find_path(DATA, self.east, self.east["safety_checks"]["main_gate"], self.east["safety_checks"]["gate_stabilization"], "patient_escort")
        self.assertFalse(primary.found)
        self.assertTrue(fallback.found)


if __name__ == "__main__":
    unittest.main()
