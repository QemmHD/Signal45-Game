"""Data loading, room/object expansion, and save-stable spatial state."""

from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from .coordinates import (
        cell_key,
        expand_cell_ranges,
        footprint_cells,
        offset_address,
        validate_address,
    )
except ImportError:  # Direct script execution.
    from coordinates import (
        cell_key,
        expand_cell_ranges,
        footprint_cells,
        offset_address,
        validate_address,
    )


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
LAYOUT_DIR = DATA_DIR / "layouts"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


@dataclass(frozen=True)
class SpatialData:
    station: dict[str, Any]
    room_families: dict[str, Any]
    objects: dict[str, Any]
    reclamation: dict[str, Any]
    layouts: dict[str, dict[str, Any]]

    def layout(self, layout_id: str) -> dict[str, Any]:
        return self.layouts[layout_id]


def load_spatial_data(data_dir: Path = DATA_DIR) -> SpatialData:
    layout_dir = data_dir / "layouts"
    raw_layouts = {
        path.stem: load_json(path)
        for path in sorted(layout_dir.glob("*.json"))
        if path.name != "scenarios.json"
    }
    layouts: dict[str, dict[str, Any]] = {}

    def materialize(layout_id: str, stack: tuple[str, ...] = ()) -> dict[str, Any]:
        if layout_id in layouts:
            return layouts[layout_id]
        if layout_id in stack:
            raise ValueError(f"layout inheritance cycle: {' -> '.join(stack + (layout_id,))}")
        raw = copy.deepcopy(raw_layouts[layout_id])
        base_id = raw.pop("extends", None)
        if not base_id:
            layouts[layout_id] = raw
            return raw
        result = copy.deepcopy(materialize(base_id, stack + (layout_id,)))
        for key, value in raw.pop("set", {}).items():
            result[key] = copy.deepcopy(value)
        for key, value in raw.pop("merge", {}).items():
            if not isinstance(result.get(key), dict) or not isinstance(value, dict):
                raise ValueError(f"layout merge field {key} must target dictionaries")
            result[key].update(copy.deepcopy(value))
        collection_ids = {
            "rooms": "instance_id",
            "objects": "instance_id",
            "modules": "instance_id",
            "utility_nodes": "node_id",
            "utility_branches": "branch_id",
            "utility_consumers": "consumer_id",
            "hazards": "hazard_id",
            "resident_locations": "resident_id",
            "hope_anchors": "anchor_id",
        }
        for collection, identifiers in raw.pop("remove", {}).items():
            key = collection_ids[collection]
            remove_ids = set(identifiers)
            result[collection] = [item for item in result.get(collection, []) if item[key] not in remove_ids]
        for collection, items in raw.pop("upsert", {}).items():
            key = collection_ids[collection]
            by_id = {item[key]: item for item in result.get(collection, [])}
            for item in items:
                by_id[item[key]] = copy.deepcopy(item)
            result[collection] = list(by_id.values())
        if raw:
            raise ValueError(f"unknown layout patch fields for {layout_id}: {sorted(raw)}")
        result["layout_id"] = layout_id
        layouts[layout_id] = result
        return result

    for layout_id in raw_layouts:
        materialize(layout_id)
    return SpatialData(
        station=load_json(data_dir / "station.json"),
        room_families=load_json(data_dir / "room_families.json"),
        objects=load_json(data_dir / "objects.json"),
        reclamation=load_json(data_dir / "reclamation.json"),
        layouts=layouts,
    )


def section_cells(
    station: dict[str, Any], section_id: str, field: str
) -> set[tuple[str, int, int, int]]:
    section = station["sections"][section_id]
    return expand_cell_ranges(section_id, section.get(field, []))


def all_section_cells(
    station: dict[str, Any], field: str
) -> set[tuple[str, int, int, int]]:
    cells: set[tuple[str, int, int, int]] = set()
    for section_id in station["sections"]:
        cells.update(section_cells(station, section_id, field))
    return cells


def fixed_architecture_cells(
    station: dict[str, Any], kind: str | None = None
) -> set[tuple[str, int, int, int]]:
    cells: set[tuple[str, int, int, int]] = set()
    for section_id, section in station["sections"].items():
        for feature in section["fixed_architecture"]:
            if kind is None or feature["kind"] == kind:
                cells.update(expand_cell_ranges(section_id, feature["cells"]))
    return cells


def room_cells(
    station: dict[str, Any], room: dict[str, Any]
) -> set[tuple[str, int, int, int]]:
    section_id = room["section_id"]
    footprint = room["footprint"]
    return expand_cell_ranges(
        section_id,
        [
            {
                "level": footprint.get("level", 0),
                "x_start": footprint["x_start"],
                "x_end": footprint["x_end"],
                "lanes": footprint["lanes"],
            }
        ],
    )


def room_by_id(layout: dict[str, Any], room_id: str) -> dict[str, Any]:
    return next(room for room in layout["rooms"] if room["instance_id"] == room_id)


def object_by_instance(layout: dict[str, Any], instance_id: str) -> dict[str, Any]:
    return next(item for item in layout["objects"] if item["instance_id"] == instance_id)


def object_cells(
    data: SpatialData, instance: dict[str, Any]
) -> set[tuple[str, int, int, int]]:
    definition = data.objects["objects"][instance["object_id"]]
    return footprint_cells(
        data.station,
        instance["anchor"],
        definition["footprint"],
        int(instance.get("rotation", 0)),
    )


def object_interaction_points(
    data: SpatialData, instance: dict[str, Any]
) -> list[dict[str, Any]]:
    definition = data.objects["objects"][instance["object_id"]]
    points: list[dict[str, Any]] = []
    for offset in definition["interaction_offsets"]:
        points.append(offset_address(data.station, instance["anchor"], offset))
    return points


def operational_rooms(layout: dict[str, Any]) -> list[dict[str, Any]]:
    active_states = {"operational", "upgraded", "repurposed", "impaired", "under_repair"}
    return [
        room
        for room in layout["rooms"]
        if room.get("counts_as_area", False) and room["state"] in active_states
    ]


def derive_functional_area_count(layout: dict[str, Any]) -> int:
    physical_ids = [room["physical_area_id"] for room in operational_rooms(layout)]
    if len(physical_ids) != len(set(physical_ids)):
        raise ValueError("one physical area is counted by more than one room instance")
    return len(physical_ids)


def derive_room_families(layout: dict[str, Any]) -> set[str]:
    return {room["family_id"] for room in operational_rooms(layout)}


def serialize_layout_state(layout: dict[str, Any]) -> str:
    authoritative = {
        "schema_version": layout["schema_version"],
        "layout_id": layout["layout_id"],
        "section_states": layout["section_states"],
        "portal_states": layout["portal_states"],
        "rooms": layout["rooms"],
        "objects": layout["objects"],
        "modules": layout.get("modules", []),
        "blueprints": layout.get("blueprints", []),
        "utility_nodes": layout["utility_nodes"],
        "utility_branches": layout["utility_branches"],
        "utility_consumers": layout["utility_consumers"],
        "hazards": layout.get("hazards", []),
        "hope_anchors": layout.get("hope_anchors", []),
        "resident_locations": layout.get("resident_locations", []),
        "presentation_state": layout.get("presentation_state", {}),
    }
    return json.dumps(authoritative, sort_keys=True, separators=(",", ":"))


def restore_layout_state(layout: dict[str, Any], serialized: str) -> dict[str, Any]:
    restored = copy.deepcopy(layout)
    authoritative = json.loads(serialized)
    for key, value in authoritative.items():
        restored[key] = value
    return restored


def validate_instance_addresses(data: SpatialData, layout: dict[str, Any]) -> None:
    for instance in layout["objects"]:
        validate_address(data.station, instance["anchor"])
        object_cells(data, instance)
        for point in object_interaction_points(data, instance):
            validate_address(data.station, point)
    for resident in layout.get("resident_locations", []):
        validate_address(data.station, resident["address"])
