from __future__ import annotations

import copy
import unittest

from tools.spatial.tests.helpers import DATA
from tools.spatial.utilities import (
    charge_backup_available, consumer_status, node_connected_to_source,
    preview_isolation, restore_platform_lighting, service_access,
    shed_platform_lighting, validate_platform_lighting,
)


class UtilityTopologyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.east = copy.deepcopy(DATA.layout("east_day7"))
        self.west = copy.deepcopy(DATA.layout("west_day7"))

    def test_platform_lighting_exists_exactly_once(self) -> None:
        self.assertEqual(validate_platform_lighting(self.east), [])
        self.east["utility_consumers"].append(copy.deepcopy(next(item for item in self.east["utility_consumers"] if item["consumer_id"] == "platform_lighting")))
        self.assertTrue(validate_platform_lighting(self.east))

    def test_lighting_upgrade_uses_same_circuit(self) -> None:
        alternate = copy.deepcopy(DATA.layout("east_day7_alternate"))
        upgrades = [item for item in alternate["modules"] if item["module_id"] == "platform_lighting_upgrade"]
        self.assertEqual(len(upgrades), 1)
        self.assertEqual(len([item for item in alternate["utility_consumers"] if item["consumer_id"] == "platform_lighting"]), 1)
        self.assertEqual(validate_platform_lighting(alternate), [])

    def test_platform_lighting_sheds_and_restores(self) -> None:
        self.assertTrue(shed_platform_lighting(self.east)["changed"])
        lamp = next(item for item in self.east["objects"] if item["instance_id"] == "platform_work_lamp")
        self.assertEqual(lamp["state"], "dimmed")
        self.assertFalse(restore_platform_lighting(self.east, 0.1)["changed"])
        self.assertTrue(restore_platform_lighting(self.east, 1.0)["changed"])
        self.assertEqual(lamp["state"], "operational")

    def test_disconnected_branch_rejects_consumer(self) -> None:
        next(item for item in self.east["utility_branches"] if item["branch_id"] == "central_power_main")["live"] = False
        status = consumer_status(self.east, "platform_lighting")
        self.assertFalse(status["connected"])
        self.assertEqual(status["reason"], "disconnected_branch")

    def test_charge_backup_requires_live_connection_and_compatible_node(self) -> None:
        self.assertTrue(charge_backup_available(self.east, "platform_lighting"))
        self.assertFalse(charge_backup_available(self.east, "east_clean_water"))
        next(item for item in self.east["utility_branches"] if item["branch_id"] == "central_power_main")["isolated"] = True
        self.assertFalse(charge_backup_available(self.east, "platform_lighting"))

    def test_every_utility_node_has_service_access(self) -> None:
        for layout in (self.east, self.west):
            for node in layout["utility_nodes"]:
                with self.subTest(layout=layout["layout_id"], node=node["node_id"]):
                    self.assertTrue(service_access(DATA, layout, node["node_id"])["reachable"])

    def test_isolation_preview_names_rooms_residents_and_recovery(self) -> None:
        preview = preview_isolation(self.east, "east_air_branch")
        self.assertTrue(preview["rooms_affected"])
        self.assertIn("recovery_method", preview)
        water = preview_isolation(self.west, "west_pump_to_treatment")
        self.assertIn("west_water_treatment", water["rooms_affected"])

    def test_power_air_water_and_structure_sources_connect(self) -> None:
        probes = [
            (self.east, "Power", "east_power_bus"),
            (self.east, "Air", "east_air_node"),
            (self.west, "Water", "west_treatment"),
            (self.west, "Structure", "west_support_zone"),
        ]
        for layout, utility, node in probes:
            with self.subTest(utility=utility, node=node):
                self.assertTrue(node_connected_to_source(layout, utility, node))


if __name__ == "__main__":
    unittest.main()
