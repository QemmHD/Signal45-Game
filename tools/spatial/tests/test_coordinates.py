from __future__ import annotations

import unittest

from tools.spatial.coordinates import (
    CoordinateError, bounds_for_cells, footprint_cells, global_to_section_local,
    logical_to_world, section_local_to_global, validate_address, world_to_nearest_cell,
)
from tools.spatial.tests.helpers import DATA


class CoordinateTests(unittest.TestCase):
    def test_coordinate_schema_accepts_valid_integer_address(self) -> None:
        address = {"section_id": "central_platform", "level": 0, "x": 4, "lane": 1}
        self.assertEqual(validate_address(DATA.station, address), address)

    def test_invalid_section_level_and_lane_fail_independently(self) -> None:
        bad = [
            {"section_id": "missing", "level": 0, "x": 0, "lane": 0},
            {"section_id": "central_platform", "level": 9, "x": 0, "lane": 0},
            {"section_id": "central_platform", "level": 0, "x": 0, "lane": 9},
        ]
        for address in bad:
            with self.subTest(address=address), self.assertRaises(CoordinateError):
                validate_address(DATA.station, address)

    def test_local_global_conversion_roundtrips(self) -> None:
        address = {"section_id": "east_staff_wing", "level": 0, "x": 3, "lane": 1}
        global_cell = section_local_to_global(DATA.station, address)
        self.assertEqual(global_to_section_local(DATA.station, "east_staff_wing", global_cell), address)

    def test_logical_world_conversion_roundtrips_to_nearest_cell(self) -> None:
        address = {"section_id": "west_pump_gallery", "level": 0, "x": 3, "lane": 1}
        world = logical_to_world(DATA.station, address)
        self.assertEqual(world_to_nearest_cell(DATA.station, "west_pump_gallery", world), address)

    def test_rotated_footprint_swaps_width_and_depth(self) -> None:
        anchor = {"section_id": "central_platform", "level": 0, "x": 10, "lane": 0}
        normal = footprint_cells(DATA.station, anchor, {"width": 2, "depth": 1}, 0)
        rotated = footprint_cells(DATA.station, anchor, {"width": 2, "depth": 1}, 90)
        self.assertEqual(len({cell[2] for cell in normal}), 2)
        self.assertEqual(len({cell[3] for cell in rotated}), 2)

    def test_noncardinal_rotation_fails(self) -> None:
        with self.assertRaises(CoordinateError):
            footprint_cells(DATA.station, {"section_id": "central_platform", "level": 0, "x": 10, "lane": 0}, {"width": 1, "depth": 1}, 45)

    def test_camera_bounds_are_derived_from_cells(self) -> None:
        bounds = bounds_for_cells(DATA.station, {("central_platform", 0, 0, 0), ("east_staff_wing", 0, 9, 1)})
        self.assertEqual(bounds["min_x"], 10)
        self.assertEqual(bounds["max_x"], 33)


if __name__ == "__main__":
    unittest.main()
