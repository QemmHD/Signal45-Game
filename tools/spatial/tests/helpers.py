from __future__ import annotations

import copy
from typing import Any

from tools.spatial.model import load_spatial_data


DATA = load_spatial_data()


def room_probe(family: str = "rest", x_start: int = 10, x_end: int = 11) -> dict[str, Any]:
    return {
        "instance_id": f"probe_{family}", "physical_area_id": f"probe_{family}",
        "family_id": family, "form": "temporary", "section_id": "central_platform",
        "footprint": {"level": 0, "x_start": x_start, "x_end": x_end, "lanes": [0]},
        "state": "operational", "counts_as_area": True, "temporary_zone": False,
        "essential": False,
    }


def layout_with_room(family: str = "rest") -> tuple[dict[str, Any], dict[str, Any]]:
    layout = copy.deepcopy(DATA.layout("day1"))
    room = room_probe(family)
    layout["rooms"].append(room)
    return layout, room


def object_probe(object_id: str, room: dict[str, Any], x: int = 10, rotation: int = 0) -> dict[str, Any]:
    return {
        "instance_id": f"probe_{object_id}", "object_id": object_id,
        "section_id": room["section_id"],
        "anchor": {"section_id": room["section_id"], "level": 0, "x": x, "lane": 0},
        "rotation": rotation, "state": "operational",
        "room_instance_id": room["instance_id"], "utility_connection": "central_air_node",
    }
