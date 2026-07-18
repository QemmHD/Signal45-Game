"""Resident-condition and discrete ration rules for Signal 45 Prompt 3.

This module deliberately models only the bounded survival facts needed by
The First Count.  It does not implement resident AI or continuous need drain.
"""

from __future__ import annotations

from typing import Any


EPSILON = 1e-6


def rounded(value: float) -> float:
    return round(float(value) + 0.0, 3)


def default_conditions() -> dict[str, str]:
    return {
        "health": "healthy",
        "hunger": "fed",
        "fatigue": "rested",
        "stress": "steady",
    }

def resident_work_profile(
    config: dict[str, Any],
    resident_name: str,
    conditions: dict[str, str] | None = None,
    *,
    availability: float = 1.0,
    global_multiplier: float = 1.0,
    medical_restriction: str = "none",
) -> dict[str, Any]:
    """Return legible productive and self-preservation capacity separately.

    The model uses the largest condition penalty plus half of the remaining
    penalties, capped by canonical data. Critical Health, collapse-risk
    Fatigue, and explicit non-working medical restrictions override the
    arithmetic and produce zero productive project work.
    """

    work = config["work"]
    resident = config["residents"][resident_name]
    states = default_conditions()
    states.update(conditions or {})
    availability = min(1.0, max(0.0, float(availability)))
    restriction_data = config["medical_restrictions"][medical_restriction]

    unavailable = availability <= EPSILON
    critical_health = states["health"] == "critical"
    collapse_risk = states["fatigue"] == "collapse_risk"
    medically_incapacitated = bool(restriction_data["productive_work_blocked"])
    forced_zero = unavailable or critical_health or collapse_risk or medically_incapacitated

    penalties = [
        float(work["condition_penalties"][condition][state])
        for condition, state in states.items()
    ]
    dominant = max(penalties)
    secondary = sum(penalties) - dominant
    rule = work["condition_combination"]
    combined_penalty = min(
        float(rule["maximum_penalty"]),
        dominant + secondary * float(rule["secondary_weight"]),
    )
    base = float(resident["base_capacity"]) * availability * float(global_multiplier)
    productive = 0.0 if forced_zero else max(0.0, base * (1.0 - combined_penalty))

    if unavailable:
        restriction = "unavailable"
    elif critical_health:
        restriction = "critical_health"
    elif collapse_risk:
        restriction = "collapse_risk"
    elif medically_incapacitated:
        restriction = medical_restriction
    elif combined_penalty >= 0.50:
        restriction = "light_duties_only"
    elif combined_penalty >= 0.25:
        restriction = "reduced_shift"
    else:
        restriction = "none"

    self_action = (
        not unavailable
        and bool(restriction_data["emergency_self_action"])
        and medical_restriction != "unconscious"
    )
    assignment_eligible = productive > EPSILON and not medically_incapacitated
    requires_assistance = bool(restriction_data["requires_assistance"]) or critical_health
    evacuation_required = bool(restriction_data["evacuation_required"])

    return {
        "resident": resident_name,
        "conditions": states,
        "productive_capacity": rounded(productive),
        "productive_work_capacity": rounded(productive),
        "combined_penalty": rounded(combined_penalty),
        "dominant_penalty": rounded(dominant),
        "current_work_restriction": restriction,
        "emergency_self_action_available": self_action,
        "emergency_self_action": self_action,
        "assignment_eligible": assignment_eligible,
        "available_for_assignment": assignment_eligible,
        "treatment_required": critical_health or bool(restriction_data["treatment_required"]),
        "evacuation_required": evacuation_required,
        "requires_assistance": requires_assistance,
        "medical_restriction": medical_restriction,
    }


def shelter_emergency_capacity(
    profiles: list[dict[str, Any]], minimum_required: float
) -> dict[str, Any]:
    """Apply the anti-death-spiral safeguard to the labor pool, not people."""

    eligible = [
        profile
        for profile in profiles
        if profile["assignment_eligible"] and profile["productive_capacity"] > EPSILON
    ]
    available = sum(profile["productive_capacity"] for profile in eligible)
    supplied = min(float(minimum_required), available)
    return {
        "required": rounded(minimum_required),
        "available": rounded(available),
        "supplied": rounded(supplied),
        "met": supplied + EPSILON >= float(minimum_required),
        "providers": [profile["resident"] for profile in eligible],
        "forced_incapacitated_labor": False,
        "outside_or_manual_fallback_required": supplied + EPSILON < float(minimum_required),
    }


def food_issue(
    config: dict[str, Any], resident_count: int, *, issue: str = "normal"
) -> dict[str, Any]:
    food = config["stocks"]["Food"]
    key = {
        "normal": "normal_per_resident_day",
        "restricted": "restricted_per_resident_day",
        "missed": "missed_per_resident_day",
        "emergency": "emergency_per_resident_day",
    }[issue]
    per_person = float(food[key])
    effects = config["emergency_actions"]["ration_food"]["condition_effects"].get(
        issue, {"hunger_steps": 0, "stress_points": 0}
    )
    return {
        "issue": issue,
        "resident_count": resident_count,
        "per_person": per_person,
        "amount": rounded(resident_count * per_person),
        "hunger_steps": int(effects["hunger_steps"]),
        "stress_points": int(effects["stress_points"]),
        "critical_health_loss": False,
    }


def water_issue(
    config: dict[str, Any], resident_count: int, *, issue: str = "normal"
) -> dict[str, Any]:
    water = config["stocks"]["Clean Water"]
    key = {
        "normal": "normal_per_resident_day",
        "restricted": "restricted_per_resident_day",
    }[issue]
    per_person = float(water[key])
    action = config["emergency_actions"]["restrict_water"]
    return {
        "issue": issue,
        "resident_count": resident_count,
        "per_person": per_person,
        "amount": rounded(resident_count * per_person),
        "safe_days": int(action["maximum_consecutive_safe_days"]),
        "treatment_restricted": issue == "restricted",
        "stress_points": int(action["stress_points_per_day"] if issue == "restricted" else 0),
    }


def ration_consequence(config: dict[str, Any], consecutive_days: int) -> dict[str, Any]:
    """Escalate ration costs deterministically; one missed meal is not critical."""

    if consecutive_days <= 0:
        hunger = "fed"
        stress = 0
        health_effect = "none"
    elif consecutive_days == 1:
        hunger = "hungry"
        stress = 2
        health_effect = "none"
    elif consecutive_days == 2:
        hunger = "restricted"
        stress = 5
        health_effect = "none"
    else:
        hunger = "prolonged"
        stress = 9
        health_effect = "strained_after_warning"
    return {
        "consecutive_days": consecutive_days,
        "hunger_band": hunger,
        "stress_points": stress,
        "health_effect": health_effect,
        "immediate_critical_harm": False,
        "reversible_next_day": consecutive_days <= 2,
    }
