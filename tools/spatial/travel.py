"""Coordinate-derived logical travel and hauling proxies.

The outputs are normalized indices, never claims about measured seconds.
"""

from __future__ import annotations

import math
from statistics import mean
from typing import Any

try:
    from .model import SpatialData
    from .navigation import find_path, path_survives_without_portal
except ImportError:  # Direct script execution.
    from model import SpatialData
    from navigation import find_path, path_survives_without_portal


def percentile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, math.ceil(len(ordered) * fraction) - 1))
    return round(ordered[index], 3)


def _named_path(
    data: SpatialData, layout: dict[str, Any], metric: dict[str, Any]
) -> dict[str, Any]:
    result = find_path(
        data,
        layout,
        metric["start"],
        metric["end"],
        metric["path_class"],
    )
    return {
        "name": metric["name"],
        "path_class": metric["path_class"],
        "found": result.found,
        "cost": result.cost if result.found else None,
        "failure_reason": result.failure_reason,
        "required_portals": result.required_portals,
        "vertical_transitions": result.vertical_transitions,
        "hazard_exposure": result.hazard_exposure,
        "path": result.path,
    }


def _travel_factor(score: float) -> float:
    if score <= 12.0:
        return 0.08
    if score <= 14.0:
        return 0.10
    if score <= 18.0:
        return 0.12
    return 0.16


def _hauling_factor(material_cost: float, heavy_cost: float) -> float:
    # Routine deliveries dominate the weekly allowance. Heavy moves are already
    # represented in project work stages, so they receive a bounded 20% weight.
    score = material_cost * 0.80 + heavy_cost * 0.20
    if score <= 17.0:
        return 0.04
    if score <= 20.0:
        return 0.05
    return 0.07


def _single_points_of_failure(
    data: SpatialData, layout: dict[str, Any]
) -> list[str]:
    gate = layout["safety_checks"]["main_gate"]
    safe = layout["safety_checks"]["safe_area"]
    baseline = find_path(data, layout, gate, safe, "emergency_evacuation")
    if not baseline.found:
        return ["baseline_emergency_path_missing"]
    points: list[str] = []
    for portal_id in sorted(set(baseline.required_portals)):
        if not path_survives_without_portal(
            data, layout, gate, safe, "emergency_evacuation", portal_id
        ):
            points.append(portal_id)
    return points


def calculate_travel_metrics(
    data: SpatialData, layout: dict[str, Any]
) -> dict[str, Any]:
    named = [_named_path(data, layout, metric) for metric in layout["metric_paths"]]
    lookup = {item["name"]: item for item in named}
    ordinary = [
        item["cost"]
        for item in named
        if item["found"] and item["path_class"] == "normal_walk"
    ]
    essential = [
        item["cost"]
        for item in named
        if item["found"] and item["name"] in layout["essential_metric_names"]
    ]
    material = lookup["materials_delivery"]["cost"] or 0.0
    heavy = lookup["heavy_carry"]["cost"] or 0.0
    average = round(mean(ordinary), 3) if ordinary else 0.0
    p95 = percentile(ordinary, 0.95)
    longest = round(max(essential), 3) if essential else 0.0
    portal_delay = round(
        sum(len(item["required_portals"]) for item in named if item["found"]) / max(1, len(named)),
        3,
    )
    score = round(average * 0.50 + p95 * 0.25 + longest * 0.15 + portal_delay * 0.10, 3)
    cell_usage: dict[tuple[str, int, int, int], int] = {}
    for item in named:
        for address in item["path"]:
            key = (address["section_id"], address["level"], address["x"], address["lane"])
            cell_usage[key] = cell_usage.get(key, 0) + 1
    congestion = round(max(cell_usage.values(), default=0) / max(1, len(named)), 3)
    single_points = _single_points_of_failure(data, layout)
    baseline_evacuation = find_path(
        data,
        layout,
        layout["safety_checks"]["main_gate"],
        layout["safety_checks"]["safe_area"],
        "emergency_evacuation",
    )
    alternate_routes = sum(
        1
        for portal_id in sorted(set(baseline_evacuation.required_portals))
        if path_survives_without_portal(
            data,
            layout,
            layout["safety_checks"]["main_gate"],
            layout["safety_checks"]["safe_area"],
            "emergency_evacuation",
            portal_id,
        )
    )
    travel_factor = _travel_factor(score)
    hauling_factor = _hauling_factor(material, heavy)
    old_travel = float(layout["comparison_allowance"]["travel_factor"])
    old_hauling = float(layout["comparison_allowance"]["hauling_factor"])
    return {
        "layout_id": layout["layout_id"],
        "logical_distance_notice": "Logical path-cost proxies; not measured real seconds.",
        "layout_validity_input": all(item["found"] for item in named),
        "named_paths": named,
        "ordinary_average_path": average,
        "ordinary_p95_path": p95,
        "longest_essential_path": longest,
        "materials_delivery_path": material,
        "heavy_carry_path": heavy,
        "gate_to_medical_path": lookup["gate_to_medical"]["cost"],
        "gate_to_stabilization_path": lookup["gate_to_stabilization"]["cost"],
        "storage_to_workshop_path": lookup["storage_to_workshop"]["cost"],
        "rest_to_work_path": lookup["rest_to_work"]["cost"],
        "filter_service_path": lookup["filter_service"]["cost"],
        "pump_service_path": lookup["pump_service"]["cost"],
        "water_isolation_path": lookup["water_isolation"]["cost"],
        "evacuation_path": lookup["evacuation"]["cost"],
        "vertical_transitions": sum(item["vertical_transitions"] for item in named),
        "portal_delay_proxy": portal_delay,
        "congestion_proxy": congestion,
        "single_point_of_failure_count": len(single_points),
        "single_points_of_failure": single_points,
        "alternate_route_count": alternate_routes,
        "weighted_travel_score": score,
        "coordinate_travel_factor": travel_factor,
        "coordinate_hauling_factor": hauling_factor,
        "existing_abstract_travel_factor": old_travel,
        "existing_abstract_hauling_factor": old_hauling,
        "travel_factor_difference": round(travel_factor - old_travel, 3),
        "hauling_factor_difference": round(hauling_factor - old_hauling, 3),
        "double_counted": False,
        "day5_response_budget": layout["day5_response_budget"],
        "day5_max_response_path": max(
            lookup[name]["cost"] or 0.0 for name in layout["day5_metric_names"]
        ),
    }
