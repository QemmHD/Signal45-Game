"""Deterministic cell-and-portal navigation for spatial validation."""

from __future__ import annotations

import heapq
from dataclasses import asdict, dataclass
from typing import Any

try:
    from .coordinates import cell_key, key_to_address, validate_address
    from .model import SpatialData, all_section_cells, object_cells
except ImportError:  # Direct script execution.
    from coordinates import cell_key, key_to_address, validate_address
    from model import SpatialData, all_section_cells, object_cells


OPEN_PORTAL_STATES = {"open", "damaged"}


@dataclass
class PathResult:
    found: bool
    path_class: str
    path: list[dict[str, Any]]
    cost: float
    failure_reason: str | None
    required_portals: list[str]
    hazard_exposure: int
    vertical_transitions: int
    carry_restrictions: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _path_rules(data: SpatialData, path_class: str) -> dict[str, Any]:
    rules = data.station["path_classes"]
    if path_class not in rules:
        raise ValueError(f"unknown path class: {path_class}")
    return rules[path_class]


def portal_state(layout: dict[str, Any], portal_id: str, default: str) -> str:
    return layout.get("portal_states", {}).get(portal_id, default)


def navigation_cells(
    data: SpatialData,
    layout: dict[str, Any],
    *,
    extra_blocked: set[tuple[str, int, int, int]] | None = None,
) -> set[tuple[str, int, int, int]]:
    cells = all_section_cells(data.station, "walkable_cells")
    closed_sections = {
        section_id
        for section_id, state in layout["section_states"].items()
        if state.get("access") in {"blocked", "closed", "sealed", "unreclaimed"}
    }
    cells = {cell for cell in cells if cell[0] not in closed_sections}
    for section_id, state in layout["section_states"].items():
        for item in state.get("blocked_cells", []):
            cells.discard(
                (
                    section_id,
                    int(item.get("level", 0)),
                    int(item["x"]),
                    int(item["lane"]),
                )
            )
    for instance in layout.get("objects", []):
        definition = data.objects["objects"][instance["object_id"]]
        if definition.get("blocks_navigation", False) and instance["state"] not in {
            "stored",
            "blueprint",
        }:
            cells.difference_update(object_cells(data, instance))
    cells.difference_update(extra_blocked or set())
    return cells


def _hazard_map(layout: dict[str, Any]) -> dict[tuple[str, int, int, int], int]:
    result: dict[tuple[str, int, int, int], int] = {}
    for hazard in layout.get("hazards", []):
        if hazard.get("state") not in {"active", "warning"}:
            continue
        severity = int(hazard.get("path_severity", 1))
        for address in hazard.get("cells", []):
            result[cell_key(address)] = max(severity, result.get(cell_key(address), 0))
    return result


def build_graph(
    data: SpatialData,
    layout: dict[str, Any],
    path_class: str,
    *,
    extra_blocked: set[tuple[str, int, int, int]] | None = None,
    disabled_portals: set[str] | None = None,
) -> dict[tuple[str, int, int, int], list[tuple[tuple[str, int, int, int], float, str | None]]]:
    rules = _path_rules(data, path_class)
    cells = navigation_cells(data, layout, extra_blocked=extra_blocked)
    graph: dict[
        tuple[str, int, int, int],
        list[tuple[tuple[str, int, int, int], float, str | None]],
    ] = {cell: [] for cell in cells}
    for cell in sorted(cells):
        section_id, level, x, lane = cell
        neighbors = [
            (section_id, level, x - 1, lane, 1.0),
            (section_id, level, x + 1, lane, 1.0),
            (section_id, level, x, lane - 1, 1.2),
            (section_id, level, x, lane + 1, 1.2),
        ]
        for neighbor_section, neighbor_level, neighbor_x, neighbor_lane, cost in neighbors:
            neighbor = (
                neighbor_section,
                neighbor_level,
                neighbor_x,
                neighbor_lane,
            )
            if neighbor in cells:
                graph[cell].append((neighbor, cost * float(rules["carry_penalty"]), None))

    disabled = disabled_portals or set()
    for portal_id, portal in data.station["portals"].items():
        if portal_id in disabled:
            continue
        state = portal_state(layout, portal_id, portal["initial_state"])
        if state not in OPEN_PORTAL_STATES:
            continue
        if path_class not in portal["path_classes_allowed"]:
            continue
        if int(portal["width"]) < int(rules["minimum_width"]):
            continue
        if portal["type"] in rules.get("forbidden_portal_types", []):
            continue
        source = cell_key(validate_address(data.station, portal["source"]))
        destination = cell_key(validate_address(data.station, portal["destination"]))
        if source not in cells or destination not in cells:
            continue
        cost = float(portal["traversal_cost"]) * float(rules["carry_penalty"])
        graph[source].append((destination, cost, portal_id))
        if portal.get("bidirectional", True):
            graph[destination].append((source, cost, portal_id))
    return graph


def find_path(
    data: SpatialData,
    layout: dict[str, Any],
    start: dict[str, Any],
    end: dict[str, Any],
    path_class: str = "normal_walk",
    *,
    extra_blocked: set[tuple[str, int, int, int]] | None = None,
    disabled_portals: set[str] | None = None,
    avoid_hazards: bool = True,
) -> PathResult:
    validate_address(data.station, start)
    validate_address(data.station, end)
    rules = _path_rules(data, path_class)
    graph = build_graph(
        data,
        layout,
        path_class,
        extra_blocked=extra_blocked,
        disabled_portals=disabled_portals,
    )
    start_key = cell_key(start)
    end_key = cell_key(end)
    if start_key not in graph:
        return PathResult(False, path_class, [], 0.0, "start_not_walkable", [], 0, 0, [])
    if end_key not in graph:
        return PathResult(False, path_class, [], 0.0, "destination_not_walkable", [], 0, 0, [])

    hazard_map = _hazard_map(layout)
    tolerance = int(rules["hazard_tolerance"])
    queue: list[tuple[float, tuple[str, int, int, int]]] = [(0.0, start_key)]
    distances = {start_key: 0.0}
    previous: dict[
        tuple[str, int, int, int],
        tuple[tuple[str, int, int, int], str | None],
    ] = {}
    while queue:
        distance, cell = heapq.heappop(queue)
        if distance > distances[cell] + 1e-9:
            continue
        if cell == end_key:
            break
        for neighbor, edge_cost, portal_id in graph[cell]:
            severity = hazard_map.get(neighbor, 0)
            if severity > tolerance and avoid_hazards:
                continue
            hazard_cost = severity * float(rules.get("hazard_cost", 4.0))
            candidate = distance + edge_cost + hazard_cost
            if candidate + 1e-9 < distances.get(neighbor, float("inf")):
                distances[neighbor] = candidate
                previous[neighbor] = (cell, portal_id)
                heapq.heappush(queue, (candidate, neighbor))

    if end_key not in distances:
        closed = [
            portal_id
            for portal_id, portal in data.station["portals"].items()
            if portal_state(layout, portal_id, portal["initial_state"]) not in OPEN_PORTAL_STATES
        ]
        reason = "portal_closed_or_isolated" if closed else "no_valid_path"
        return PathResult(False, path_class, [], 0.0, reason, [], 0, 0, [])

    reverse_path = [end_key]
    portals: list[str] = []
    current = end_key
    while current != start_key:
        parent, portal_id = previous[current]
        if portal_id:
            portals.append(portal_id)
        reverse_path.append(parent)
        current = parent
    keys = list(reversed(reverse_path))
    used_portals = list(reversed(portals))
    hazard_exposure = sum(1 for key in keys if hazard_map.get(key, 0) > 0)
    vertical = sum(1 for left, right in zip(keys, keys[1:]) if left[1] != right[1])
    restrictions: list[str] = []
    if path_class in {"heavy_carry", "patient_carry"} and any(
        data.station["portals"][portal_id]["type"] == "ladder"
        for portal_id in used_portals
    ):
        restrictions.append("ladder_incompatible")
    return PathResult(
        True,
        path_class,
        [key_to_address(key) for key in keys],
        round(distances[end_key], 3),
        None,
        used_portals,
        hazard_exposure,
        vertical,
        restrictions,
    )


def path_survives_without_portal(
    data: SpatialData,
    layout: dict[str, Any],
    start: dict[str, Any],
    end: dict[str, Any],
    path_class: str,
    portal_id: str,
) -> bool:
    return find_path(
        data,
        layout,
        start,
        end,
        path_class,
        disabled_portals={portal_id},
    ).found
