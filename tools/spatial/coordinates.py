"""Authoritative logical coordinate helpers.

Rendering, placement, navigation, utilities, incidents, and saves all consume the
same section-local address. World transforms are derived presentation values.
"""

from __future__ import annotations

from typing import Any, Iterable


class CoordinateError(ValueError):
    """Raised when an address cannot exist in the authored station shell."""


def cell_key(address: dict[str, Any]) -> tuple[str, int, int, int]:
    return (
        str(address["section_id"]),
        int(address["level"]),
        int(address["x"]),
        int(address["lane"]),
    )


def key_to_address(key: tuple[str, int, int, int]) -> dict[str, Any]:
    section_id, level, x, lane = key
    return {"section_id": section_id, "level": level, "x": x, "lane": lane}


def validate_address(station: dict[str, Any], address: dict[str, Any]) -> dict[str, Any]:
    section_id = str(address.get("section_id", ""))
    sections = station["sections"]
    if section_id not in sections:
        raise CoordinateError(f"invalid section: {section_id}")
    section = sections[section_id]
    level = int(address.get("level", -999))
    lane = int(address.get("lane", -999))
    x = int(address.get("x", -999))
    if level not in section["levels"]:
        raise CoordinateError(f"invalid level {level} for {section_id}")
    if lane not in section["allowed_depth_lanes"]:
        raise CoordinateError(f"invalid depth lane {lane} for {section_id}")
    if not 0 <= x < int(section["width"]):
        raise CoordinateError(f"x {x} outside section {section_id}")
    return {"section_id": section_id, "level": level, "x": x, "lane": lane}


def section_local_to_global(
    station: dict[str, Any], address: dict[str, Any]
) -> dict[str, int]:
    local = validate_address(station, address)
    origin = station["sections"][local["section_id"]]["origin"]
    return {
        "x": int(origin["x"]) + local["x"],
        "level": int(origin["level"]) + local["level"],
        "lane": int(origin.get("lane", 0)) + local["lane"],
    }


def global_to_section_local(
    station: dict[str, Any], section_id: str, coordinate: dict[str, Any]
) -> dict[str, Any]:
    if section_id not in station["sections"]:
        raise CoordinateError(f"invalid section: {section_id}")
    origin = station["sections"][section_id]["origin"]
    local = {
        "section_id": section_id,
        "x": int(round(float(coordinate["x"]))) - int(origin["x"]),
        "level": int(round(float(coordinate["level"]))) - int(origin["level"]),
        "lane": int(round(float(coordinate["lane"]))) - int(origin.get("lane", 0)),
    }
    return validate_address(station, local)


def logical_to_world(
    station: dict[str, Any], address: dict[str, Any]
) -> dict[str, float]:
    logical = section_local_to_global(station, address)
    transform = station["coordinate_contract"]["world_transform"]
    return {
        "x": logical["x"] * float(transform["cell_width"]),
        "y": logical["level"] * float(transform["level_height"]),
        "z": logical["lane"] * float(transform["lane_depth"]),
    }


def world_to_nearest_cell(
    station: dict[str, Any], section_id: str, world: dict[str, Any]
) -> dict[str, Any]:
    transform = station["coordinate_contract"]["world_transform"]
    global_coordinate = {
        "x": round(float(world["x"]) / float(transform["cell_width"])),
        "level": round(float(world["y"]) / float(transform["level_height"])),
        "lane": round(float(world["z"]) / float(transform["lane_depth"])),
    }
    return global_to_section_local(station, section_id, global_coordinate)


def expand_cell_ranges(
    section_id: str, ranges: Iterable[dict[str, Any]]
) -> set[tuple[str, int, int, int]]:
    cells: set[tuple[str, int, int, int]] = set()
    for item in ranges:
        start = int(item.get("x_start", item.get("x", 0)))
        end = int(item.get("x_end", item.get("x", start)))
        lanes = item.get("lanes", [item.get("lane", 0)])
        for x in range(start, end + 1):
            for lane in lanes:
                cells.add((section_id, int(item.get("level", 0)), x, int(lane)))
    return cells


def rotated_size(width: int, depth: int, rotation: int) -> tuple[int, int]:
    normalized = int(rotation) % 360
    if normalized not in {0, 90, 180, 270}:
        raise CoordinateError(f"unsupported cardinal rotation: {rotation}")
    return (depth, width) if normalized in {90, 270} else (width, depth)


def footprint_cells(
    station: dict[str, Any],
    anchor: dict[str, Any],
    footprint: dict[str, Any],
    rotation: int = 0,
) -> set[tuple[str, int, int, int]]:
    origin = validate_address(station, anchor)
    width, depth = rotated_size(
        int(footprint.get("width", 1)), int(footprint.get("depth", 1)), rotation
    )
    cells: set[tuple[str, int, int, int]] = set()
    for dx in range(width):
        for dlane in range(depth):
            candidate = {
                "section_id": origin["section_id"],
                "level": origin["level"],
                "x": origin["x"] + dx,
                "lane": origin["lane"] + dlane,
            }
            validate_address(station, candidate)
            cells.add(cell_key(candidate))
    return cells


def offset_address(
    station: dict[str, Any], anchor: dict[str, Any], offset: dict[str, Any]
) -> dict[str, Any]:
    candidate = {
        "section_id": anchor["section_id"],
        "level": int(anchor["level"]) + int(offset.get("dlevel", 0)),
        "x": int(anchor["x"]) + int(offset.get("dx", 0)),
        "lane": int(anchor["lane"]) + int(offset.get("dlane", 0)),
    }
    return validate_address(station, candidate)


def bounds_for_cells(
    station: dict[str, Any], cells: Iterable[tuple[str, int, int, int]]
) -> dict[str, Any]:
    logical = [section_local_to_global(station, key_to_address(cell)) for cell in cells]
    if not logical:
        raise CoordinateError("camera bounds require at least one cell")
    return {
        "min_x": min(cell["x"] for cell in logical),
        "max_x": max(cell["x"] for cell in logical),
        "min_level": min(cell["level"] for cell in logical),
        "max_level": max(cell["level"] for cell in logical),
        "min_lane": min(cell["lane"] for cell in logical),
        "max_lane": max(cell["lane"] for cell in logical),
    }
