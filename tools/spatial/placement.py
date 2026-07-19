"""Placement, blueprint, module, and severe-access validation."""

from __future__ import annotations

import copy
from typing import Any

try:
    from .coordinates import cell_key, footprint_cells, key_to_address, offset_address
    from .model import SpatialData, all_section_cells, fixed_architecture_cells, object_cells, room_by_id, room_cells
    from .navigation import find_path
except ImportError:  # Direct script execution.
    from coordinates import cell_key, footprint_cells, key_to_address, offset_address
    from model import SpatialData, all_section_cells, fixed_architecture_cells, object_cells, room_by_id, room_cells
    from navigation import find_path


REASON_CATALOG = {
    "outside_buildable_area": ("Outside the authored buildable area.", "Move the preview into a highlighted buildable bay.", "boundary"),
    "overlaps_fixed_architecture": ("This overlaps fixed railway structure.", "Move clear of columns, track edges, walls, or machinery.", "fixed-structure"),
    "overlaps_room": ("This room overlaps another physical area.", "Use another bay or repurpose the existing room.", "overlap"),
    "overlaps_object": ("Another installed object occupies this space.", "Move or store the existing object first.", "overlap"),
    "blocks_required_portal": ("This blocks a required door or passage.", "Move it away from the highlighted portal cells.", "portal"),
    "blocks_only_route": ("This would remove the only usable shelter route.", "Leave one continuous route open.", "route"),
    "strands_resident": ("A resident would be stranded.", "Move the object or evacuate before changing access.", "resident"),
    "strands_essential_room": ("An essential room would become unreachable.", "Preserve an interaction path to the highlighted room.", "essential-room"),
    "blocks_emergency_path": ("This removes the only emergency path.", "Keep a valid route to the safe area.", "emergency"),
    "blocks_interaction_point": ("Every interaction point would be blocked.", "Keep at least one highlighted approach cell clear.", "interaction"),
    "insufficient_clearance": ("There is not enough use or carrying clearance.", "Move the object away from the highlighted clearance cells.", "clearance"),
    "unsupported_rotation": ("This object cannot use that rotation.", "Choose one of the shown rotations.", "rotation"),
    "incompatible_room_family": ("This object is not compatible with the selected room.", "Choose a compatible room or object.", "room-family"),
    "incompatible_section": ("This object cannot be installed in this station section.", "Choose a compatible authored section.", "section"),
    "missing_socket": ("The required equipment socket is unavailable.", "Choose an open matching socket.", "socket"),
    "missing_utility_node": ("No required utility node serves this placement.", "Place it in a served section or connect the branch.", "utility-node"),
    "disconnected_branch": ("The required utility branch is disconnected.", "Reconnect or repair the branch first.", "disconnected"),
    "structure_unsupported": ("The local structure cannot support this placement.", "Reinforce the highlighted support zone.", "structure"),
    "hazard_present": ("An active hazard occupies this space.", "Clear or isolate the hazard first.", "hazard"),
    "project_space_reserved": ("An active project already reserves this space.", "Cancel, finish, or move the other blueprint.", "reserved"),
    "module_parent_invalid": ("This module has no valid operational parent.", "Attach it to the required room or object socket.", "module-parent"),
    "module_capacity_exceeded": ("That parent has no compatible module capacity left.", "Remove another module or select a different parent.", "module-capacity"),
}


def _reason(code: str, cells: set[tuple[str, int, int, int]] | None = None) -> dict[str, Any]:
    message, suggestion, indicator = REASON_CATALOG[code]
    return {
        "code": code,
        "message": message,
        "highlighted_cells": [key_to_address(cell) for cell in sorted(cells or set())],
        "suggested_correction": suggestion,
        "accessible_indicator": indicator,
    }


def _result(reasons: list[dict[str, Any]]) -> dict[str, Any]:
    return {"valid": not reasons, "reasons": reasons}


def validate_room_placement(
    data: SpatialData,
    layout: dict[str, Any],
    candidate: dict[str, Any],
) -> dict[str, Any]:
    candidate_cells = room_cells(data.station, candidate)
    fixed = fixed_architecture_cells(data.station)
    buildable = all_section_cells(data.station, "buildable_cells")
    reasons: list[dict[str, Any]] = []
    fixed_overlap = candidate_cells & fixed
    if fixed_overlap:
        reasons.append(_reason("overlaps_fixed_architecture", fixed_overlap))
    outside = candidate_cells - buildable
    if outside:
        reasons.append(_reason("outside_buildable_area", outside))
    occupied: set[tuple[str, int, int, int]] = set()
    for room in layout["rooms"]:
        if room["instance_id"] != candidate.get("instance_id"):
            occupied.update(room_cells(data.station, room))
    overlap = candidate_cells & occupied
    if overlap:
        reasons.append(_reason("overlaps_room", overlap))
    reserved = set()
    for blueprint in layout.get("blueprints", []):
        if blueprint.get("state") in {"active", "reserved", "delivery", "under_construction"}:
            reserved.update(tuple(cell) for cell in blueprint.get("occupied_cell_keys", []))
    reservation_overlap = candidate_cells & reserved
    if reservation_overlap:
        reasons.append(_reason("project_space_reserved", reservation_overlap))
    family_id = candidate["family_id"]
    family = data.room_families["families"].get(family_id)
    section_type = data.station["sections"][candidate["section_id"]]["section_type"]
    if not family or section_type not in family["compatible_section_types"]:
        reasons.append(_reason("incompatible_section", candidate_cells))
    return _result(reasons)


def _object_instance_cells(
    data: SpatialData,
    object_id: str,
    anchor: dict[str, Any],
    rotation: int,
) -> set[tuple[str, int, int, int]]:
    definition = data.objects["objects"][object_id]
    return footprint_cells(data.station, anchor, definition["footprint"], rotation)


def validate_object_placement(
    data: SpatialData,
    layout: dict[str, Any],
    candidate: dict[str, Any],
    *,
    include_severe_access: bool = True,
) -> dict[str, Any]:
    definition = data.objects["objects"][candidate["object_id"]]
    rotation = int(candidate.get("rotation", 0))
    reasons: list[dict[str, Any]] = []
    if rotation not in definition["rotation_options"]:
        reasons.append(_reason("unsupported_rotation"))
        return _result(reasons)
    cells = _object_instance_cells(data, candidate["object_id"], candidate["anchor"], rotation)
    fixed_overlap = cells & fixed_architecture_cells(data.station)
    if fixed_overlap:
        reasons.append(_reason("overlaps_fixed_architecture", fixed_overlap))
    outside = cells - all_section_cells(data.station, "buildable_cells")
    if outside:
        reasons.append(_reason("outside_buildable_area", outside))
    section_type = data.station["sections"][candidate["anchor"]["section_id"]]["section_type"]
    if section_type not in definition["compatible_section_types"]:
        reasons.append(_reason("incompatible_section", cells))
    room_id = candidate.get("room_instance_id")
    if room_id:
        room = room_by_id(layout, room_id)
        if not cells <= room_cells(data.station, room):
            reasons.append(_reason("outside_buildable_area", cells - room_cells(data.station, room)))
        if room["family_id"] not in definition["compatible_room_families"]:
            reasons.append(_reason("incompatible_room_family", cells))
    elif definition.get("room_required", False):
        reasons.append(_reason("incompatible_room_family", cells))
    occupied: set[tuple[str, int, int, int]] = set()
    for instance in layout["objects"]:
        if instance["instance_id"] != candidate.get("instance_id") and instance["state"] != "stored":
            occupied.update(object_cells(data, instance))
    overlap = cells & occupied
    if overlap:
        reasons.append(_reason("overlaps_object", overlap))
    interaction_cells: set[tuple[str, int, int, int]] = set()
    for offset in definition["interaction_offsets"]:
        try:
            interaction_cells.add(cell_key(offset_address(data.station, candidate["anchor"], offset)))
        except ValueError:
            reasons.append(_reason("blocks_interaction_point", cells))
    if interaction_cells and not interaction_cells <= all_section_cells(data.station, "walkable_cells"):
        reasons.append(_reason("blocks_interaction_point", interaction_cells))
    if interaction_cells & occupied:
        reasons.append(_reason("blocks_interaction_point", interaction_cells & occupied))
    utility = definition.get("utility_requirement")
    if utility:
        served_nodes = [
            node
            for node in layout["utility_nodes"]
            if node["utility"] == utility
            and node["section_id"] == candidate["anchor"]["section_id"]
            and node["state"] == "live"
        ]
        if not served_nodes:
            reasons.append(_reason("missing_utility_node", cells))
    if include_severe_access and definition.get("blocks_navigation", False) and not reasons:
        severe = validate_severe_access(data, layout, cells)
        reasons.extend(severe["reasons"])
    return _result(reasons)


def validate_severe_access(
    data: SpatialData,
    layout: dict[str, Any],
    blocked_cells: set[tuple[str, int, int, int]],
) -> dict[str, Any]:
    checks = layout["safety_checks"]
    reasons: list[dict[str, Any]] = []
    gate = checks["main_gate"]
    safe = checks["safe_area"]
    if not find_path(data, layout, gate, safe, "emergency_evacuation", extra_blocked=blocked_cells).found:
        reasons.append(_reason("blocks_only_route", blocked_cells))
        reasons.append(_reason("blocks_emergency_path", blocked_cells))
    for resident in layout.get("resident_locations", []):
        if not find_path(
            data,
            layout,
            resident["address"],
            safe,
            "emergency_evacuation",
            extra_blocked=blocked_cells,
        ).found:
            reasons.append(_reason("strands_resident", blocked_cells))
            break
    for interaction in checks["essential_interactions"]:
        if not find_path(
            data,
            layout,
            gate,
            interaction,
            "normal_walk",
            extra_blocked=blocked_cells,
        ).found:
            reasons.append(_reason("strands_essential_room", blocked_cells))
            break
    unique = {reason["code"]: reason for reason in reasons}
    return _result(list(unique.values()))


def validate_portal_change(
    data: SpatialData,
    layout: dict[str, Any],
    portal_id: str,
    new_state: str,
) -> dict[str, Any]:
    """Preview and refuse a portal closure that strands people or essential access."""
    if portal_id not in data.station["portals"]:
        raise KeyError(portal_id)
    portal = data.station["portals"][portal_id]
    closing = new_state in {"closed", "locked", "blocked", "sealed", "isolated", "under_repair"}
    reasons: list[dict[str, Any]] = []
    affected_residents: list[str] = []
    affected_rooms: list[str] = []
    checks = layout["safety_checks"]
    if closing:
        disabled = {portal_id}
        if not find_path(
            data, layout, checks["main_gate"], checks["safe_area"],
            "emergency_evacuation", disabled_portals=disabled,
        ).found:
            reasons.extend([_reason("blocks_only_route"), _reason("blocks_emergency_path")])
        for resident in layout.get("resident_locations", []):
            if not find_path(
                data, layout, resident["address"], checks["safe_area"],
                "emergency_evacuation", disabled_portals=disabled,
            ).found:
                affected_residents.append(resident["resident_id"])
        if affected_residents:
            reasons.append(_reason("strands_resident"))
        for room in layout.get("rooms", []):
            if not room.get("essential"):
                continue
            if not find_path(
                data, layout, checks["main_gate"], room["primary_interaction"],
                "normal_walk", disabled_portals=disabled,
            ).found:
                affected_rooms.append(room["instance_id"])
        if affected_rooms:
            reasons.append(_reason("strands_essential_room"))
    unique = {reason["code"]: reason for reason in reasons}
    result = _result(list(unique.values()))
    result["preview"] = {
        "portal_id": portal_id,
        "new_state": new_state,
        "residents_affected": affected_residents,
        "rooms_affected": affected_rooms,
        "utilities_affected": portal.get("utility_relationship", []),
        "hazard_boundary": portal.get("hazard_relationship"),
        "recovery_method": portal.get("closure_behavior"),
    }
    return result


def new_blueprint(
    project_id: str,
    occupied_cells: set[tuple[str, int, int, int]],
    materials: float,
    work: float,
) -> dict[str, Any]:
    return {
        "project_id": project_id,
        "state": "preview",
        "materials_required": float(materials),
        "materials_reserved": 0.0,
        "materials_delivered": 0.0,
        "work_required": float(work),
        "work_applied": 0.0,
        "occupied_cell_keys": [list(cell) for cell in sorted(occupied_cells)],
        "transactions": [],
        "capability_granted": False,
        "refund_claimed": False,
    }


def save_inactive_blueprint(blueprint: dict[str, Any]) -> None:
    if blueprint["state"] == "preview":
        blueprint["state"] = "saved_inactive"


def activate_blueprint(blueprint: dict[str, Any], stocks: dict[str, float]) -> bool:
    transaction = f"{blueprint['project_id']}:activation"
    if transaction in blueprint["transactions"]:
        return False
    if stocks["Materials"] < blueprint["materials_required"]:
        return False
    stocks["Materials"] -= blueprint["materials_required"]
    blueprint["materials_reserved"] = blueprint["materials_required"]
    blueprint["state"] = "reserved"
    blueprint["transactions"].append(transaction)
    return True


def deliver_blueprint(blueprint: dict[str, Any]) -> bool:
    transaction = f"{blueprint['project_id']}:delivery"
    if transaction in blueprint["transactions"] or blueprint["state"] not in {"reserved", "delivery"}:
        return False
    blueprint["materials_delivered"] = blueprint["materials_reserved"]
    blueprint["state"] = "delivery"
    blueprint["transactions"].append(transaction)
    return True


def apply_construction_work(blueprint: dict[str, Any], amount: float) -> float:
    if blueprint["state"] not in {"delivery", "under_construction"}:
        return 0.0
    remaining = blueprint["work_required"] - blueprint["work_applied"]
    applied = min(max(0.0, amount), remaining)
    blueprint["work_applied"] = round(blueprint["work_applied"] + applied, 3)
    blueprint["state"] = "under_construction"
    return applied


def complete_blueprint(blueprint: dict[str, Any]) -> bool:
    transaction = f"{blueprint['project_id']}:completion"
    if transaction in blueprint["transactions"]:
        return False
    if blueprint["work_applied"] + 1e-9 < blueprint["work_required"]:
        return False
    blueprint["state"] = "operational"
    blueprint["capability_granted"] = True
    blueprint["transactions"].append(transaction)
    return True


def cancel_blueprint(
    blueprint: dict[str, Any], stocks: dict[str, float], refund_fraction: float
) -> float:
    transaction = f"{blueprint['project_id']}:cancellation"
    if transaction in blueprint["transactions"] or blueprint["state"] in {"operational", "cancelled"}:
        return 0.0
    unconsumed = max(0.0, blueprint["materials_reserved"] - blueprint["materials_delivered"])
    refund = round(unconsumed * max(0.0, min(1.0, refund_fraction)), 3)
    stocks["Materials"] += refund
    blueprint["state"] = "cancelled"
    blueprint["refund_claimed"] = True
    blueprint["transactions"].append(transaction)
    return refund


def deconstruct_once(
    object_state: dict[str, Any], stocks: dict[str, float], original_cost: float, salvage_fraction: float
) -> float:
    transaction = f"{object_state['instance_id']}:deconstruct"
    transactions = object_state.setdefault("transactions", [])
    if transaction in transactions or object_state["state"] == "stored":
        return 0.0
    salvage = round(original_cost * min(max(salvage_fraction, 0.0), 0.75), 3)
    stocks["Materials"] += salvage
    object_state["state"] = "stored"
    transactions.append(transaction)
    return salvage


def repurpose_room(room: dict[str, Any], new_family: str, *, incident_active: bool) -> bool:
    if incident_active or room["state"] in {"critical", "isolated", "under_repair"}:
        return False
    room["family_id"] = new_family
    room["state"] = "repurposed"
    return True


def validate_module(
    layout: dict[str, Any], module: dict[str, Any], objects: dict[str, Any]
) -> dict[str, Any]:
    reasons: list[dict[str, Any]] = []
    if module.get("parent_type") == "module":
        reasons.append(_reason("module_parent_invalid"))
        return _result(reasons)
    parents = {
        instance["instance_id"]: instance
        for instance in layout["objects"]
        if instance["state"] not in {"stored", "destroyed"}
    }
    parent = parents.get(module.get("parent_instance_id"))
    if not parent:
        reasons.append(_reason("module_parent_invalid"))
        return _result(reasons)
    definition = objects["objects"][parent["object_id"]]
    compatible = [socket for socket in definition.get("module_sockets", []) if socket["type"] == module["socket_type"]]
    installed = [
        existing
        for existing in layout.get("modules", [])
        if existing.get("parent_instance_id") == parent["instance_id"]
        and existing.get("socket_type") == module["socket_type"]
        and existing.get("state") != "stored"
    ]
    capacity = sum(int(socket.get("capacity", 1)) for socket in compatible)
    if not compatible:
        reasons.append(_reason("missing_socket"))
    elif len(installed) >= capacity:
        reasons.append(_reason("module_capacity_exceeded"))
    if module.get("unique", False) and any(
        existing.get("module_id") == module["module_id"] and existing.get("state") != "stored"
        for existing in layout.get("modules", [])
    ):
        reasons.append(_reason("module_capacity_exceeded"))
    return _result(reasons)
