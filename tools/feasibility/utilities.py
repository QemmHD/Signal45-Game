"""Section-level utility calculations and the Relay Load Test."""

from __future__ import annotations

from typing import Any


EPSILON = 1e-6


def rounded(value: float) -> float:
    return round(float(value) + 0.0, 3)


def discharge_charge(
    config: dict[str, Any],
    available_charge: float,
    requested_delivery: float,
    *,
    branch_connected: bool,
    stages: int = 1,
) -> dict[str, Any]:
    stock = config["stocks"]["Charge"]
    if not branch_connected:
        return {
            "accepted": False,
            "reason": "Charge cannot power a disconnected branch",
            "delivered": 0.0,
            "stock_draw": 0.0,
            "remaining": rounded(available_charge),
        }
    discharge_limit = float(stock["discharge_limit_per_stage"]) * max(1, int(stages))
    delivered = min(float(requested_delivery), discharge_limit)
    loss = float(stock["discharge_loss"])
    required_draw = delivered / (1.0 - loss)
    draw = min(float(available_charge), required_draw)
    actual_delivery = draw * (1.0 - loss)
    return {
        "accepted": actual_delivery > EPSILON,
        "reason": None if actual_delivery > EPSILON else "Charge reserve empty",
        "requested_delivery": rounded(requested_delivery),
        "delivered": rounded(actual_delivery),
        "stock_draw": rounded(draw),
        "conversion_loss": rounded(draw - actual_delivery),
        "remaining": rounded(max(0.0, available_charge - draw)),
        "discharge_limit": rounded(discharge_limit),
    }


def relay_load_test(
    config: dict[str, Any], response: str, available_charge: float, *, branch_connected: bool = True
) -> dict[str, Any]:
    event = config["relay_load_test"]
    capacity = config["utilities"]["power"]["source_capacity"] * config["utilities"]["power"]["condition"]
    ordinary = float(event["ordinary_demand"])
    temporary = float(event["temporary_demand"])
    demand = ordinary + temporary
    deficit = max(0.0, demand - capacity)
    result: dict[str, Any] = {
        "response": response,
        "capacity": rounded(capacity),
        "ordinary_demand": rounded(ordinary),
        "temporary_demand": rounded(temporary),
        "peak_demand": rounded(demand),
        "temporary_deficit": rounded(deficit),
        "lighting_visible_before": True,
        "lighting_visible_during": True,
        "lighting_restored": True,
        "charge_draw": 0.0,
        "warning_lead_delta": 0,
        "safe_save_before_commitment": True,
        "injury": "none",
        "campaign_ending_consequence": False,
        "power_is_capacity": True,
        "charge_is_stored_reserve": True,
    }
    if response == "charge":
        discharge = discharge_charge(
            config, available_charge, max(deficit, event["charge_delivery"]), branch_connected=branch_connected
        )
        result["discharge"] = discharge
        result["charge_draw"] = discharge["stock_draw"]
        result["resolved"] = discharge["accepted"] and discharge["delivered"] + EPSILON >= deficit
        result["reason"] = discharge["reason"]
    elif response == "shed_lighting":
        result["lighting_visible_during"] = False
        result["shed_load"] = event["shed_load"]
        result["resolved"] = float(event["shed_amount"]) + EPSILON >= deficit
        result["reason"] = None
    elif response == "delay":
        result["resolved"] = True
        result["calibration_delayed"] = True
        result["warning_lead_delta"] = -1
        result["reason"] = "Calibration deferred; storm estimate remains less certain for one stage"
    else:
        raise ValueError(f"unknown Relay Load Test response {response}")
    return result


def progress_air_stage(config: dict[str, Any], current: str, pressure_steps: int, interruption_steps: int = 0) -> dict[str, Any]:
    stages = config["utilities"]["air"]["degradation_stages"]
    start = stages.index(current)
    end = min(len(stages) - 1, max(0, start + pressure_steps - interruption_steps))
    return {
        "from": current,
        "to": stages[end],
        "stages_crossed": end - start,
        "warning_shown": end > start,
        "instant_unexplained_exposure": end - start > 1 and current == "stable",
        "responses": config["utilities"]["air"]["responses"],
    }


def diagnose_water_link(
    config: dict[str, Any],
    *,
    source: float,
    pump: float,
    treatment: float,
    delivery: float,
    storage_state: str,
    demand: float,
) -> dict[str, Any]:
    throughput = source * pump * treatment * delivery
    if storage_state == "contaminated":
        failing = "clean storage"
    elif source <= EPSILON:
        failing = "source"
    elif pump < 0.75:
        failing = "pumping"
    elif treatment < 0.75:
        failing = "treatment"
    elif delivery < 0.75:
        failing = "delivery"
    elif throughput + EPSILON < demand:
        failing = "source capacity"
    else:
        failing = None
    return {
        "source": rounded(source),
        "pump": rounded(pump),
        "treatment": rounded(treatment),
        "delivery_efficiency": rounded(delivery),
        "clean_storage": storage_state,
        "throughput": rounded(throughput),
        "demand": rounded(demand),
        "headroom": rounded(throughput - demand),
        "failing_link": failing,
        "diagnosable_within_taps": 2,
    }


def structure_transition(
    config: dict[str, Any], current: str, pressure_steps: int, reinforcement_steps: int = 0
) -> dict[str, Any]:
    states = config["utilities"]["structure"]["states"]
    start = states.index(current)
    end = min(len(states) - 1, max(0, start + pressure_steps - reinforcement_steps))
    state = states[end]
    return {
        "from": current,
        "to": state,
        "warning": state in {"unstable", "critical"},
        "access_open": state not in {"critical", "closed"},
        "evacuation_required": state in {"critical", "closed"},
        "tasks_suspended": state == "closed",
        "adjacent_propagation_depth": min(
            int(config["utilities"]["structure"]["maximum_adjacent_propagation"]),
            1 if state == "closed" else 0,
        ),
        "unseen_injury": False,
    }
