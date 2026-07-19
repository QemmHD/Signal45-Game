"""Section-level utility topology and service-access validation."""

from __future__ import annotations

from collections import deque
from typing import Any

try:
    from .model import SpatialData
    from .navigation import find_path
except ImportError:  # Direct script execution.
    from model import SpatialData
    from navigation import find_path


def nodes_by_id(layout: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {node["node_id"]: node for node in layout["utility_nodes"]}


def branches_by_id(layout: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {branch["branch_id"]: branch for branch in layout["utility_branches"]}


def utility_adjacency(
    layout: dict[str, Any], utility: str
) -> dict[str, set[str]]:
    nodes = {
        node["node_id"]
        for node in layout["utility_nodes"]
        if node["utility"] == utility and node["state"] == "live"
    }
    adjacency = {node_id: set() for node_id in nodes}
    for branch in layout["utility_branches"]:
        if branch["utility"] != utility or not branch["live"] or branch.get("isolated", False):
            continue
        if branch["source_node"] in nodes and branch["target_node"] in nodes:
            adjacency[branch["source_node"]].add(branch["target_node"])
            adjacency[branch["target_node"]].add(branch["source_node"])
    return adjacency


def node_connected_to_source(
    layout: dict[str, Any], utility: str, node_id: str
) -> bool:
    nodes = nodes_by_id(layout)
    if node_id not in nodes or nodes[node_id]["state"] != "live":
        return False
    sources = {
        node["node_id"]
        for node in layout["utility_nodes"]
        if node["utility"] == utility
        and node["node_type"] in {"source", "support_source", "storage_source"}
        and node["state"] == "live"
    }
    adjacency = utility_adjacency(layout, utility)
    queue = deque([node_id])
    visited = {node_id}
    while queue:
        current = queue.popleft()
        if current in sources:
            return True
        for neighbor in adjacency.get(current, set()):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return False


def consumer_status(layout: dict[str, Any], consumer_id: str) -> dict[str, Any]:
    matches = [
        consumer for consumer in layout["utility_consumers"] if consumer["consumer_id"] == consumer_id
    ]
    if len(matches) != 1:
        return {"connected": False, "reason": "consumer_missing_or_duplicated", "count": len(matches)}
    consumer = matches[0]
    connected = node_connected_to_source(layout, consumer["utility"], consumer["node_id"])
    return {
        "connected": connected and consumer["state"] in {"operational", "shed"},
        "reason": None if connected else "disconnected_branch",
        "consumer": consumer,
    }


def validate_platform_lighting(layout: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    consumers = [
        consumer
        for consumer in layout["utility_consumers"]
        if consumer["consumer_id"] == "platform_lighting"
    ]
    if len(consumers) != 1:
        errors.append(f"platform_lighting must exist exactly once, found {len(consumers)}")
        return errors
    consumer = consumers[0]
    if consumer["utility"] != "Power" or consumer["priority"] != "optional":
        errors.append("platform_lighting must be one Optional Power consumer")
    object_ids = {
        instance["instance_id"]: instance for instance in layout["objects"]
    }
    lamp = object_ids.get(consumer["object_instance_id"])
    if not lamp or lamp["object_id"] != "platform_work_lamp":
        errors.append("platform_lighting must map to the Platform Work Lamp")
    forbidden = {"task_lighting", "comfort_lighting"}
    duplicated = forbidden & {consumer["consumer_id"] for consumer in layout["utility_consumers"]}
    if duplicated:
        errors.append(f"retired lighting consumers remain: {sorted(duplicated)}")
    upgrades = [
        module
        for module in layout.get("modules", [])
        if module["module_id"] == "platform_lighting_upgrade" and module["state"] == "operational"
    ]
    if upgrades and any(module["parent_instance_id"] != lamp["instance_id"] for module in upgrades):
        errors.append("Platform Lighting Upgrade must attach to the same lamp")
    if upgrades and len(consumers) != 1:
        errors.append("Platform Lighting Upgrade may not create another consumer")
    return errors


def shed_platform_lighting(layout: dict[str, Any]) -> dict[str, Any]:
    status = consumer_status(layout, "platform_lighting")
    if not status["connected"]:
        return {"changed": False, "reason": status["reason"]}
    consumer = status["consumer"]
    if consumer["state"] == "shed":
        return {"changed": False, "reason": "already_shed"}
    consumer["state"] = "shed"
    for instance in layout["objects"]:
        if instance["instance_id"] == consumer["object_instance_id"]:
            instance["state"] = "dimmed"
    return {"changed": True, "consumer_id": "platform_lighting", "load_relieved": consumer["load"]}


def restore_platform_lighting(layout: dict[str, Any], power_margin: float) -> dict[str, Any]:
    consumer = next(
        item for item in layout["utility_consumers"] if item["consumer_id"] == "platform_lighting"
    )
    if consumer["state"] != "shed":
        return {"changed": False, "reason": "not_shed"}
    if power_margin + 1e-9 < float(consumer["load"]):
        return {"changed": False, "reason": "insufficient_margin"}
    consumer["state"] = "operational"
    for instance in layout["objects"]:
        if instance["instance_id"] == consumer["object_instance_id"]:
            instance["state"] = "operational"
    return {"changed": True, "consumer_id": "platform_lighting"}


def charge_backup_available(layout: dict[str, Any], consumer_id: str) -> bool:
    status = consumer_status(layout, consumer_id)
    if not status["connected"]:
        return False
    consumer = status["consumer"]
    nodes = nodes_by_id(layout)
    return bool(nodes[consumer["node_id"]].get("charge_backup_compatible", False))


def service_access(
    data: SpatialData,
    layout: dict[str, Any],
    node_id: str,
    start: dict[str, Any] | None = None,
) -> dict[str, Any]:
    node = nodes_by_id(layout)[node_id]
    origin = start or layout["safety_checks"]["safe_area"]
    path = find_path(data, layout, origin, node["service_point"], "utility_service")
    return {"reachable": path.found, "path": path.to_dict(), "node_id": node_id}


def preview_isolation(layout: dict[str, Any], branch_id: str) -> dict[str, Any]:
    branch = branches_by_id(layout)[branch_id]
    affected_consumers = [
        consumer["consumer_id"]
        for consumer in layout["utility_consumers"]
        if consumer["node_id"] in {branch["source_node"], branch["target_node"]}
    ]
    return {
        "branch_id": branch_id,
        "rooms_affected": branch.get("rooms_affected", []),
        "residents_affected": branch.get("residents_affected", []),
        "consumers_affected": affected_consumers,
        "recovery_method": branch["recovery_method"],
    }
