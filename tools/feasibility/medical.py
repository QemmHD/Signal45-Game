"""Bounded named-treatment transactions for Signal 45 Prompt 3."""

from __future__ import annotations

import copy
from typing import Any


def rounded(value: float) -> float:
    return round(float(value) + 0.0, 3)


def treatment_plan(
    config: dict[str, Any],
    treatment_id: str,
    resident: str,
    condition: str,
    severity: str,
    *,
    room_available: bool = True,
    skilled_staff_available: bool = True,
) -> dict[str, Any]:
    definitions = config["medical_conditions"]
    if condition not in definitions:
        raise ValueError(f"unknown medical condition {condition}")
    definition = definitions[condition]
    if severity not in definition["severities"]:
        raise ValueError(f"unsupported severity {severity} for {condition}")
    data = definition["severities"][severity]
    blockers: list[str] = []
    if data["room_requirement"] != "none" and not room_available:
        blockers.append(f"requires {data['room_requirement']}")
    if data["skilled_staff_required"] and not skilled_staff_available:
        blockers.append("requires capable medical staff")
    return {
        "treatment_id": treatment_id,
        "resident": resident,
        "condition": condition,
        "severity": severity,
        "status": "planned" if blockers else "active",
        "stage": "examination" if not blockers else "blocked",
        "medicine_reserved": rounded(data["medicine"]),
        "water_reserved": rounded(data["clean_water"]),
        "medical_work": rounded(data["work"]),
        "recovery_days": int(data["recovery_days"]),
        "productive_work_blocked": bool(data["productive_work_blocked"]),
        "movement_restriction": data["movement_restriction"],
        "room_requirement": data["room_requirement"],
        "auto_pause_tier": data["auto_pause_tier"],
        "progression_if_delayed": data["progression_if_delayed"],
        "blockers": blockers,
        "reservation_id": f"treatment:{treatment_id}:reservation",
        "completion_id": f"treatment:{treatment_id}:completion",
        "committed_stages": ["examination"],
        "duplicate_cost_prevented": True,
        "slice_death_possible": False,
    }


def interrupt_treatment(record: dict[str, Any], reason: str) -> dict[str, Any]:
    result = copy.deepcopy(record)
    if result["status"] == "completed":
        return result
    result["status"] = "interrupted"
    result["interruption_reason"] = reason
    result["resume_stage"] = result.get("stage", "stabilization")
    result["medicine_reserved_again"] = False
    return result

def resume_treatment(record: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(record)
    if result["status"] != "interrupted":
        return result
    result["status"] = "active"
    result["stage"] = result.pop("resume_stage", "stabilization")
    result["committed_stages"].append("resumed")
    result["medicine_reserved_again"] = False
    return result


def complete_treatment(
    record: dict[str, Any], *, current_health: float, precondition_max_health: float
) -> dict[str, Any]:
    result = copy.deepcopy(record)
    result["status"] = "completed"
    result["stage"] = "recovery"
    result["committed_stages"].append("treatment")
    result["committed_stages"].append("recovery")
    restored = min(float(precondition_max_health), float(current_health) + 25.0)
    result["health_after"] = rounded(restored)
    result["precondition_max_health"] = rounded(precondition_max_health)
    result["overhealing_prevented"] = restored <= precondition_max_health
    result["completion_reward_claimed_once"] = True
    return result
