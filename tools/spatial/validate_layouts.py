"""Validate authoritative station data, layouts, and feasibility cross-links."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    from .coordinates import cell_key, validate_address
    from .model import (
        SpatialData,
        derive_functional_area_count,
        derive_room_families,
        load_spatial_data,
        object_cells,
        object_interaction_points,
        room_cells,
        validate_instance_addresses,
    )
    from .navigation import find_path
    from .travel import calculate_travel_metrics
    from .utilities import service_access, validate_platform_lighting
except ImportError:  # Direct script execution.
    from coordinates import cell_key, validate_address
    from model import (
        SpatialData,
        derive_functional_area_count,
        derive_room_families,
        load_spatial_data,
        object_cells,
        object_interaction_points,
        room_cells,
        validate_instance_addresses,
    )
    from navigation import find_path
    from travel import calculate_travel_metrics
    from utilities import service_access, validate_platform_lighting


ROOT = Path(__file__).resolve().parents[2]
FEASIBILITY_MODEL = ROOT / "tools" / "feasibility" / "data" / "model.json"
REPORT_DIR = Path(__file__).resolve().parent / "reports"

SECTION_FIELDS = {
    "section_id", "display_name", "narrative_identity", "section_type", "origin",
    "levels", "width", "allowed_depth_lanes", "bay_definitions", "fixed_architecture",
    "buildable_cells", "convertible_shell_cells", "walkable_cells", "blocked_cells",
    "reclaimable_obstacles", "structural_support_cells", "track_or_platform_edge_cells",
    "entry_portals", "exit_portals", "vertical_links", "utility_trunks", "utility_nodes",
    "isolation_controls", "initial_hazards", "reclamation_class",
    "reclamation_dependencies", "occupancy_limit", "environmental_properties",
    "emergency_safe_cells", "camera_overview_bounds", "room_focus_bounds",
    "occlusion_groups", "selection_volume", "save_representation",
    "discovery_condition", "possible_story_reveal",
}

OBJECT_FIELDS = {
    "object_id", "display_name", "behavior_family", "footprint", "rotation_options",
    "anchor_rule", "interaction_offsets", "approach_directions", "clearance_offsets",
    "blocking_rules", "blocks_navigation", "carrying_requirement", "utility_requirement",
    "compatible_room_families", "compatible_section_types", "room_required",
    "socket_requirement", "module_parent_rule", "module_sockets", "capacity", "use_behavior", "construction_class",
    "materials_cost", "component_blocker", "upgrade_state", "damage_state",
    "storage_or_deconstruction_result", "selection_bounds", "room_focus_target",
    "save_representation",
}


def _unique(items: list[dict[str, Any]], key: str, label: str, errors: list[str]) -> None:
    values = [item[key] for item in items]
    if len(values) != len(set(values)):
        errors.append(f"{label}: duplicate {key}")


def _target_exists(data: SpatialData, layout: dict[str, Any], target: dict[str, str]) -> bool:
    target_id = target["target_id"]
    kind = target["type"]
    if kind in {"room", "temporary_zone"}:
        return any(room["instance_id"] == target_id for room in layout["rooms"])
    if kind in {"object", "temporary_object"}:
        return any(item["instance_id"] == target_id for item in layout["objects"])
    if kind == "module":
        return any(item.get("instance_id") == target_id for item in layout.get("modules", [])) or target_id in data.objects["modules"]
    if kind == "reclamation":
        return target_id in data.reclamation["targets"]
    if kind == "repair_state":
        return any(item["hazard_id"] == target_id for item in layout.get("hazards", []))
    return False


def validate_catalogs(data: SpatialData) -> list[str]:
    errors: list[str] = []
    station = data.station
    if station.get("hierarchy") != ["station", "section", "bay", "cell"]:
        errors.append("station hierarchy must be station -> section -> bay -> cell")
    if set(data.room_families["families"]) != {
        "rest", "medical", "food", "storage", "utility", "workshop", "operations"
    }:
        errors.append("vertical slice must define exactly the seven locked room families")
    for section_id, section in station["sections"].items():
        missing = SECTION_FIELDS - set(section)
        if missing:
            errors.append(f"section {section_id}: missing fields {sorted(missing)}")
        if section.get("section_id") != section_id:
            errors.append(f"section {section_id}: embedded ID mismatch")
        bay_ids = [bay["bay_id"] for bay in section["bay_definitions"]]
        if len(bay_ids) != len(set(bay_ids)):
            errors.append(f"section {section_id}: duplicate bay ID")
        feature_ids = [feature["feature_id"] for feature in section["fixed_architecture"]]
        if len(feature_ids) != len(set(feature_ids)):
            errors.append(f"section {section_id}: duplicate fixed feature ID")
    for portal_id, portal in station["portals"].items():
        if portal["portal_id"] != portal_id:
            errors.append(f"portal {portal_id}: embedded ID mismatch")
        for endpoint in (portal["source"], portal["destination"]):
            try:
                validate_address(station, endpoint)
            except ValueError as exc:
                errors.append(f"portal {portal_id}: {exc}")
    for object_id, definition in data.objects["objects"].items():
        missing = OBJECT_FIELDS - set(definition)
        if missing:
            errors.append(f"object {object_id}: missing fields {sorted(missing)}")
        if definition.get("object_id") != object_id:
            errors.append(f"object {object_id}: embedded ID mismatch")
    return errors


def validate_layout(data: SpatialData, layout: dict[str, Any]) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    layout_id = layout["layout_id"]
    try:
        validate_instance_addresses(data, layout)
    except (ValueError, KeyError) as exc:
        errors.append(f"{layout_id}: invalid address: {exc}")

    for collection, key in (
        ("rooms", "instance_id"), ("objects", "instance_id"), ("modules", "instance_id"),
        ("utility_nodes", "node_id"), ("utility_branches", "branch_id"),
        ("utility_consumers", "consumer_id"), ("hope_anchors", "anchor_id"),
    ):
        _unique(layout.get(collection, []), key, f"{layout_id}/{collection}", errors)

    occupied_rooms: dict[tuple[str, int, int, int], str] = {}
    for room in layout["rooms"]:
        if room["family_id"] not in data.room_families["families"]:
            errors.append(f"{layout_id}: unknown family {room['family_id']}")
        for cell in room_cells(data.station, room):
            previous = occupied_rooms.get(cell)
            if previous and not room.get("temporary_zone", False):
                errors.append(f"{layout_id}: rooms {previous} and {room['instance_id']} overlap at {cell}")
            elif not room.get("temporary_zone", False):
                occupied_rooms[cell] = room["instance_id"]

    occupied_objects: dict[tuple[str, int, int, int], str] = {}
    object_ids = {item["instance_id"] for item in layout["objects"]}
    for instance in layout["objects"]:
        definition = data.objects["objects"].get(instance["object_id"])
        if not definition:
            errors.append(f"{layout_id}: unknown object {instance['object_id']}")
            continue
        for cell in object_cells(data, instance):
            previous = occupied_objects.get(cell)
            if previous:
                errors.append(f"{layout_id}: objects {previous} and {instance['instance_id']} overlap at {cell}")
            occupied_objects[cell] = instance["instance_id"]
        if instance.get("room_instance_id"):
            rooms = [room for room in layout["rooms"] if room["instance_id"] == instance["room_instance_id"]]
            if len(rooms) != 1:
                errors.append(f"{layout_id}: object {instance['instance_id']} has invalid room parent")
            elif not object_cells(data, instance) <= room_cells(data.station, rooms[0]):
                errors.append(f"{layout_id}: object {instance['instance_id']} lies outside its room")
        reachable = False
        for point in object_interaction_points(data, instance):
            if find_path(data, layout, layout["safety_checks"]["safe_area"], point, "normal_walk").found:
                reachable = True
                break
        if not reachable:
            errors.append(f"{layout_id}: object {instance['instance_id']} has no reachable interaction point")

    for room in layout["rooms"]:
        if room.get("state") in {"operational", "upgraded", "repurposed", "impaired", "under_repair"}:
            path = find_path(
                data, layout, layout["safety_checks"]["main_gate"],
                room["primary_interaction"], "normal_walk",
            )
            if not path.found:
                errors.append(f"{layout_id}: room {room['instance_id']} is unreachable")

    for node in layout["utility_nodes"]:
        if not service_access(data, layout, node["node_id"])["reachable"]:
            errors.append(f"{layout_id}: utility node {node['node_id']} lacks service access")

    node_ids = {node["node_id"] for node in layout["utility_nodes"]}
    for branch in layout["utility_branches"]:
        if branch["source_node"] not in node_ids or branch["target_node"] not in node_ids:
            errors.append(f"{layout_id}: branch {branch['branch_id']} has missing endpoint")
    for consumer in layout["utility_consumers"]:
        if consumer["node_id"] not in node_ids:
            errors.append(f"{layout_id}: consumer {consumer['consumer_id']} has missing node")
        if consumer.get("object_instance_id") not in object_ids:
            errors.append(f"{layout_id}: consumer {consumer['consumer_id']} has missing object")
    errors.extend(f"{layout_id}: {item}" for item in validate_platform_lighting(layout))

    if layout["portal_states"].get("east_vertical_link") != "sealed" or layout["portal_states"].get("future_upper_link") != "blocked":
        errors.append(f"{layout_id}: future vertical route must remain sealed and blocked")
    future_probe = find_path(
        data, layout,
        {"section_id": "east_staff_wing", "level": 0, "x": 9, "lane": 1},
        {"section_id": "vertical_shaft", "level": 1, "x": 2, "lane": 0},
        "normal_walk",
    )
    if future_probe.found:
        errors.append(f"{layout_id}: future vertical route is pathable")
    if "vertical_route_jam" not in layout.get("selection_regions", []):
        errors.append(f"{layout_id}: future vertical route is not inspectable")

    for project_id, target in layout.get("project_targets", {}).items():
        if not _target_exists(data, layout, target):
            errors.append(f"{layout_id}: project {project_id} target {target['target_id']} missing")

    for incident_id, target in layout["incident_spatial_targets"].items():
        if target["section_id"] not in data.station["sections"]:
            errors.append(f"{layout_id}: incident {incident_id} has invalid section")
        if target["service_node"] not in node_ids:
            errors.append(f"{layout_id}: incident {incident_id} has no service node")

    for anchor in layout.get("hope_anchors", []):
        if anchor.get("grants_stock") or anchor.get("clears_consequences"):
            errors.append(f"{layout_id}: hope anchor {anchor['anchor_id']} grants forbidden relief")
        references: list[dict[str, Any]] = []
        if anchor["reference_type"] == "object":
            references = [item for item in layout["objects"] if item["instance_id"] == anchor["reference_id"]]
        elif anchor["reference_type"] == "room":
            references = [item for item in layout["rooms"] if item["instance_id"] == anchor["reference_id"]]
        elif anchor["reference_type"] == "repair_state":
            references = [item for item in layout.get("hazards", []) if item["hazard_id"] == anchor["reference_id"]]
        if len(references) != 1 or references[0].get("state") != anchor["required_state"]:
            errors.append(f"{layout_id}: hope anchor {anchor['anchor_id']} is not earned and operational")

    try:
        area_count = derive_functional_area_count(layout)
    except ValueError as exc:
        errors.append(f"{layout_id}: {exc}")
        area_count = -1
    expected_areas = 4 if layout_id == "day1" else 10
    if area_count != expected_areas:
        errors.append(f"{layout_id}: derived area count {area_count}, expected {expected_areas}")
    families = derive_room_families(layout)
    if layout["day"] == 7 and len(families) != 7:
        errors.append(f"{layout_id}: Day 7 must use exactly seven families")

    metrics = calculate_travel_metrics(data, layout)
    if not metrics["layout_validity_input"]:
        errors.append(f"{layout_id}: one or more declared metric paths are unreachable")
    if metrics["day5_max_response_path"] > float(layout["day5_response_budget"]):
        errors.append(f"{layout_id}: Day 5 response path exceeds declared proxy budget")

    summary = {
        "layout_id": layout_id,
        "valid": not errors,
        "functional_area_count": area_count,
        "room_family_count": len(families),
        "room_families": sorted(families),
        "object_count": len(layout["objects"]),
        "portal_count": sum(1 for state in layout["portal_states"].values() if state == "open"),
        "utility_node_count": len(layout["utility_nodes"]),
        "connected_utility_consumers": len(layout["utility_consumers"]),
        "unreachable_interaction_points": sum(1 for error in errors if "interaction point" in error),
        "travel": metrics,
        "errors": errors,
    }
    return errors, summary


def validate_cross_model(data: SpatialData, summaries: dict[str, dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    feasibility = json.loads(FEASIBILITY_MODEL.read_text(encoding="utf-8"))
    projects = {project["id"]: project for project in feasibility["projects"]}
    for layout_id, layout in data.layouts.items():
        for project_id in layout.get("project_targets", {}):
            if project_id not in projects:
                errors.append(f"{layout_id}: spatial project {project_id} absent from feasibility model")
    for route, layout_id in (("east", "east_day7"), ("west", "west_day7")):
        mapping = feasibility["routes"][route].get("spatial_mapping", {})
        metrics = summaries[layout_id]["travel"]
        if mapping.get("layout_id") != layout_id or not mapping.get("replaces_abstract"):
            errors.append(f"{route}: spatial mapping does not replace abstract allowance")
        if float(mapping.get("coordinate_travel_factor", -1)) != metrics["coordinate_travel_factor"]:
            errors.append(f"{route}: stored coordinate travel factor differs from spatial report")
        if float(mapping.get("coordinate_hauling_factor", -1)) != metrics["coordinate_hauling_factor"]:
            errors.append(f"{route}: stored coordinate hauling factor differs from spatial report")
        if float(mapping.get("travel_factor", -1)) < metrics["coordinate_travel_factor"]:
            errors.append(f"{route}: selected travel factor understates coordinate evidence")
        if float(mapping.get("hauling_factor", -1)) < metrics["coordinate_hauling_factor"]:
            errors.append(f"{route}: selected hauling factor understates coordinate evidence")
    if any("travel_double_counted" not in Path(ROOT / "tools/feasibility/model.py").read_text(encoding="utf-8") for _ in [0]):
        errors.append("feasibility output lacks explicit no-double-counting field")

    power = feasibility["utilities"]["power"]
    if set(power["loads"]) & {"task_lighting", "comfort_lighting"}:
        errors.append("retired lighting loads remain in feasibility data")
    if list(name for name in power["loads"] if name == "platform_lighting") != ["platform_lighting"]:
        errors.append("feasibility model must contain exactly one platform_lighting load")
    if feasibility["relay_load_test"]["shed_load"] != "platform_lighting":
        errors.append("Relay Load Test does not shed canonical platform lighting")

    project_benefits = {key: value.get("benefits", {}) for key, value in projects.items()}
    if "functional_areas" in project_benefits["triage_cot_install"]:
        errors.append("temporary triage cot incorrectly adds physical area")
    if "functional_areas" in project_benefits["concession_repurpose"]:
        errors.append("repurpose incorrectly increments physical area")
    for project_id in ("east_utility_connection", "west_utility_connection", "triage_upgrade"):
        if project_benefits[project_id].get("functional_areas") != 1:
            errors.append(f"{project_id} must add its spatially distinct area")

    east = summaries["east_day7"]["travel"]
    west = summaries["west_day7"]["travel"]
    if not west["pump_service_path"] < east["pump_service_path"]:
        errors.append("West lacks shorter Pump service geometry")
    if not west["water_isolation_path"] < east["water_isolation_path"]:
        errors.append("West lacks shorter Water isolation geometry")
    if not west["materials_delivery_path"] < east["materials_delivery_path"]:
        errors.append("West lacks shorter Water-parts delivery geometry")
    if not east["rest_to_work_path"] < west["rest_to_work_path"]:
        errors.append("East lacks better Rest access geometry")
    if not east["gate_to_medical_path"] > west["gate_to_medical_path"]:
        errors.append("East gate-to-Medical drawback is missing")
    return errors


def run_validation() -> dict[str, Any]:
    data = load_spatial_data()
    errors = validate_catalogs(data)
    summaries: dict[str, dict[str, Any]] = {}
    for layout_id in sorted(data.layouts):
        layout_errors, summary = validate_layout(data, data.layout(layout_id))
        errors.extend(layout_errors)
        summaries[layout_id] = summary
    cross_errors = validate_cross_model(data, summaries)
    errors.extend(cross_errors)
    return {
        "schema_version": 1,
        "model_stage": "Prompt 4 spatial building",
        "provisional": True,
        "logical_distance_notice": "Travel values are coordinate-derived logical proxies, not measured real seconds.",
        "valid": not errors,
        "errors": errors,
        "cross_model_errors": cross_errors,
        "layouts": summaries,
    }


def write_reports(report: dict[str, Any]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    (REPORT_DIR / "layout_validation.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    travel = {key: value["travel"] for key, value in report["layouts"].items()}
    (REPORT_DIR / "travel_metrics.json").write_text(
        json.dumps(travel, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    lines = [
        "# Spatial Layout Validation Summary", "",
        "> Logical path-cost proxies only; these are not measured real seconds.", "",
        "| Layout | Valid | Areas | Families | Travel | Hauling | Gate→Medical | Pump service |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for layout_id, item in sorted(report["layouts"].items()):
        travel_item = item["travel"]
        lines.append(
            f"| {layout_id} | {'yes' if item['valid'] else 'no'} | {item['functional_area_count']} | "
            f"{item['room_family_count']} | {travel_item['coordinate_travel_factor']:.2f} | "
            f"{travel_item['coordinate_hauling_factor']:.2f} | {travel_item['gate_to_medical_path']} | "
            f"{travel_item['pump_service_path']} |"
        )
    lines += ["", f"Overall: **{'VALID' if report['valid'] else 'INVALID'}**.", ""]
    if report["errors"]:
        lines += ["## Errors", ""] + [f"- {error}" for error in report["errors"]] + [""]
    (REPORT_DIR / "layout_summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-reports", action="store_true")
    args = parser.parse_args()
    report = run_validation()
    if args.write_reports:
        write_reports(report)
    for error in report["errors"]:
        print(f"ERROR {error}", file=sys.stderr)
    print(
        f"SPATIAL_VALID layouts={len(report['layouts'])} errors={len(report['errors'])} "
        f"status={'pass' if report['valid'] else 'fail'}"
    )
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
