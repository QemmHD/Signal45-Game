"""Reusable, bounded incident records and scheduler for Signal 45."""

from __future__ import annotations

import copy
from typing import Any


def create_incident(
    config: dict[str, Any], incident_id: str, family: str, *, section: str = "central"
) -> dict[str, Any]:
    definition = config["incident_definitions"][family]
    return {
        "incident_id": incident_id,
        "family": family,
        "source": definition["source"],
        "trigger": definition["trigger"],
        "section": section,
        "affected_room_or_object": definition["affected_room_or_object"],
        "initial_warning": definition["initial_warning"],
        "confidence": definition["confidence"],
        "severity": definition["severity"],
        "current_stage": "warning",
        "time_or_work_until_escalation": definition["escalation_allowance"],
        "affected_stocks": copy.deepcopy(definition["affected_stocks"]),
        "affected_utilities": copy.deepcopy(definition["affected_utilities"]),
        "affected_residents": [],
        "access_effect": definition["access_effect"],
        "propagation_rule": definition["propagation_rule"],
        "maximum_propagation_depth": definition["maximum_propagation_depth"],
        "auto_pause_tier": definition["auto_pause_tier"],
        "immediate_responses": copy.deepcopy(definition["immediate_responses"]),
        "generated_work_orders": copy.deepcopy(definition["generated_work_orders"]),
        "required_materials_or_components": copy.deepcopy(definition["required_materials_or_components"]),
        "required_equipment": copy.deepcopy(definition["required_equipment"]),
        "evacuation_rule": definition["evacuation_rule"],
        "isolation_rule": definition["isolation_rule"],
        "recovery_work": definition["recovery_work"],
        "physical_aftermath": definition["physical_aftermath"],
        "human_consequence_placeholder": definition["human_consequence_placeholder"],
        "delayed_consequence": definition["delayed_consequence"],
        "completion_condition": definition["completion_condition"],
        "failure_condition": definition["failure_condition"],
        "transaction_ids": [f"incident:{incident_id}:warning"],
        "status": "active",
        "major": definition["severity"] == "major",
    }


def schedule_incident(
    active: list[dict[str, Any]], queued: list[dict[str, Any]], candidate: dict[str, Any]
) -> dict[str, Any]:
    major_live = any(item["major"] and item["status"] == "active" for item in active)
    if candidate["major"] and major_live:
        queued.append(candidate)
        return {"started": False, "queued": True, "reason": "one major crisis already active"}
    active.append(candidate)
    return {"started": True, "queued": False, "reason": None}


def advance_incident(incident: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(incident)
    stage_order = ["warning", "active", "severe", "recovery", "resolved"]
    index = stage_order.index(result["current_stage"])
    if index < len(stage_order) - 1:
        result["current_stage"] = stage_order[index + 1]
    result["transaction_ids"].append(
        f"incident:{result['incident_id']}:{result['current_stage']}"
    )
    if result["current_stage"] == "resolved":
        result["status"] = "resolved"
    return result


def interrupt_incident(
    incident: dict[str, Any], response: str, *, isolate: bool = False, evacuate: bool = False
) -> dict[str, Any]:
    result = copy.deepcopy(incident)
    if response not in result["immediate_responses"]:
        raise ValueError(f"response {response} is not valid for {result['family']}")
    result["chosen_response"] = response
    result["isolated"] = isolate
    result["evacuated"] = evacuate
    result["current_stage"] = "recovery"
    result["propagation_stopped"] = True
    result["transaction_ids"].append(f"incident:{result['incident_id']}:interrupt:{response}")
    return result


def recover_incident(incident: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(incident)
    if result["status"] == "resolved":
        return result
    result["current_stage"] = "resolved"
    result["status"] = "resolved"
    result["transaction_ids"].append(f"incident:{result['incident_id']}:resolved")
    result["reward_claim_id"] = f"incident:{result['incident_id']}:recovery_claim"
    return result


def validate_cascade(cascade: list[str], configured_maximum: int) -> dict[str, Any]:
    depth = len(cascade)
    return {
        "cascade": list(cascade),
        "depth": depth,
        "maximum": configured_maximum,
        "bounded": depth <= configured_maximum,
        "duplicate_system": len(set(cascade)) != depth,
        "major_crises": 1,
    }
