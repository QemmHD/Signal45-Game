#!/usr/bin/env python3
"""Deterministic, falsifiable seven-day survival model for Signal 45.

The model intentionally represents only work, stocks, bounded utilities, projects,
events, expedition facts, admissions, and serialization invariants needed by
Prompts 2 and 3. It is not a game engine and does not simulate resident footsteps.
"""

from __future__ import annotations

import copy
import json
import math
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable

try:
    from . import forecasts, incidents, medical, survival, utilities
    from .validate_data import DEFAULT_MODEL, DEFAULT_SCENARIOS, validate_all
except ImportError:  # Direct script/test discovery execution.
    import forecasts
    import incidents
    import medical
    import survival
    import utilities
    from validate_data import DEFAULT_MODEL, DEFAULT_SCENARIOS, validate_all


EPSILON = 1e-6


def rounded(value: float) -> float:
    return round(float(value) + 0.0, 3)


def load_inputs(
    model_path: Path = DEFAULT_MODEL, scenarios_path: Path = DEFAULT_SCENARIOS
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    model, scenario_data = validate_all(model_path, scenarios_path)
    return model, scenario_data["scenarios"]


@dataclass
class ProjectProgress:
    project_id: str
    required_work: float
    remaining_work: float
    status: str = "planned"
    reserved_materials: float = 0.0
    reserved_components: dict[str, int] = field(default_factory=dict)
    completion_day: int | None = None
    cancellation_day: int | None = None
    block_reason: str | None = None
    applied_work: float = 0.0


@dataclass
class SimulationState:
    day: int
    phase: str
    stocks: dict[str, float]
    components: dict[str, int]
    stock_minima: dict[str, float]
    projects: dict[str, ProjectProgress]
    completed_projects: set[str] = field(default_factory=set)
    committed_actions: set[str] = field(default_factory=set)
    claimed_rewards: set[str] = field(default_factory=set)
    functional_areas: int = 4
    rest_capacity: int = 4
    temporary_rest_capacity: int = 0
    benefits: dict[str, float] = field(default_factory=dict)
    signal_evidence: int = 1
    outside_contact: bool = False
    juna_state: str = "not_arrived"
    juna_admitted: bool = False
    storm_state: dict[str, Any] = field(default_factory=dict)
    expedition_state: dict[str, Any] = field(default_factory=dict)
    treatment_open: bool = False
    injury_state: str = "none"
    warnings: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)
    target_misses: list[str] = field(default_factory=list)
    deadline_misses: list[str] = field(default_factory=list)
    shortfalls: dict[str, float] = field(default_factory=dict)
    resident_conditions: dict[str, dict[str, str]] = field(default_factory=dict)
    contextual_conditions: dict[str, dict[str, Any]] = field(default_factory=dict)
    treatments: dict[str, dict[str, Any]] = field(default_factory=dict)
    incidents: dict[str, dict[str, Any]] = field(default_factory=dict)
    incident_queue: list[dict[str, Any]] = field(default_factory=list)
    promises: dict[str, dict[str, Any]] = field(default_factory=dict)
    highball_state: dict[str, Any] = field(default_factory=dict)
    relay_load_test_state: dict[str, Any] = field(default_factory=dict)
    hope_state: dict[str, Any] = field(default_factory=dict)
    proof_gaps: list[str] = field(default_factory=list)
    recovery_reasons: list[str] = field(default_factory=list)
    invariant_errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["completed_projects"] = sorted(self.completed_projects)
        result["committed_actions"] = sorted(self.committed_actions)
        result["claimed_rewards"] = sorted(self.claimed_rewards)
        result["projects"] = {
            project_id: asdict(progress)
            for project_id, progress in sorted(self.projects.items())
        }
        return result

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "SimulationState":
        converted = copy.deepcopy(value)
        converted["completed_projects"] = set(converted.get("completed_projects", []))
        converted["committed_actions"] = set(converted.get("committed_actions", []))
        converted["claimed_rewards"] = set(converted.get("claimed_rewards", []))
        converted["projects"] = {
            project_id: ProjectProgress(**progress)
            for project_id, progress in converted["projects"].items()
        }
        return cls(**converted)

    @classmethod
    def from_json(cls, text: str) -> "SimulationState":
        return cls.from_dict(json.loads(text))


def commit_once(
    state: SimulationState, action_id: str, mutation: Callable[[], None]
) -> bool:
    """Commit a state mutation exactly once."""

    if action_id in state.committed_actions:
        return False
    mutation()
    state.committed_actions.add(action_id)
    return True


def add_stock(state: SimulationState, config: dict[str, Any], stock: str, amount: float) -> float:
    before = state.stocks[stock]
    capacity = config["stocks"][stock]["capacity"]
    if stock == "Charge":
        capacity *= state.benefits.get("charge_capacity_multiplier", 1.0)
    state.stocks[stock] = rounded(min(capacity, before + max(0.0, amount)))
    state.stock_minima[stock] = min(state.stock_minima[stock], state.stocks[stock])
    return rounded(state.stocks[stock] - before)


def consume_stock(
    state: SimulationState,
    stock: str,
    amount: float,
    reason: str,
    *,
    critical: bool = True,
) -> float:
    amount = max(0.0, rounded(amount))
    available = state.stocks[stock]
    consumed = min(available, amount)
    state.stocks[stock] = rounded(available - consumed)
    state.stock_minima[stock] = min(state.stock_minima[stock], state.stocks[stock])
    shortfall = rounded(amount - consumed)
    if shortfall > EPSILON:
        state.shortfalls[stock] = rounded(state.shortfalls.get(stock, 0.0) + shortfall)
        message = f"{reason}: {stock} shortfall {shortfall:.2f}"
        if critical and message not in state.failures:
            state.failures.append(message)
        elif message not in state.warnings:
            state.warnings.append(message)
    return shortfall


def grant_reward_once(
    state: SimulationState,
    config: dict[str, Any],
    reward_id: str,
    *,
    stocks: dict[str, float] | None = None,
    components: dict[str, int] | None = None,
) -> bool:
    if reward_id in state.claimed_rewards:
        return False
    for stock, amount in (stocks or {}).items():
        add_stock(state, config, stock, amount)
    for component, amount in (components or {}).items():
        capacity = config["components"][component]["capacity"]
        state.components[component] = min(
            capacity, state.components.get(component, 0) + int(amount)
        )
    state.claimed_rewards.add(reward_id)
    return True


def default_conditions() -> dict[str, str]:
    return survival.default_conditions()


def calculate_resident_work_profile(
    config: dict[str, Any],
    resident_name: str,
    conditions: dict[str, str] | None = None,
    *,
    availability: float = 1.0,
    global_multiplier: float = 1.0,
    medical_restriction: str = "none",
) -> dict[str, Any]:
    return survival.resident_work_profile(
        config,
        resident_name,
        conditions,
        availability=availability,
        global_multiplier=global_multiplier,
        medical_restriction=medical_restriction,
    )


def calculate_resident_capacity(
    config: dict[str, Any],
    resident_name: str,
    conditions: dict[str, str] | None = None,
    *,
    availability: float = 1.0,
    global_multiplier: float = 1.0,
) -> float:
    return calculate_resident_work_profile(
        config,
        resident_name,
        conditions,
        availability=availability,
        global_multiplier=global_multiplier,
    )["productive_capacity"]


def aptitude_modifier(config: dict[str, Any], resident_name: str, role: str) -> float:
    tag = config["residents"][resident_name]["aptitudes"].get(role, "poor")
    return float(config["work"]["aptitude_multipliers"][tag])


def multi_worker_output(
    config: dict[str, Any], project_class: str, worker_capacities: list[float]
) -> float:
    class_data = config["work"]["project_classes"][project_class]
    efficiencies = class_data["worker_efficiency"]
    limited = worker_capacities[: class_data["max_workers"]]
    return rounded(sum(capacity * efficiencies[index] for index, capacity in enumerate(limited)))


def resolve_construction_risk(risk: dict[str, Any] | None) -> dict[str, Any]:
    risk = risk or {
        "accepted": False,
        "protection": True,
        "warning_ignored": False,
        "stabilization_delayed": False,
    }
    visible_causes: list[str] = []
    score = 0
    if risk.get("accepted"):
        score += 1
        visible_causes.append("visible accepted risk")
    if not risk.get("protection", True):
        score += 1
        visible_causes.append("inadequate protection")
    if risk.get("warning_ignored"):
        score += 1
        visible_causes.append("ignored warning")
    if risk.get("stabilization_delayed"):
        score += 1
        visible_causes.append("delayed stabilization")
    injury = "none"
    if score >= 3:
        injury = "serious"
    elif score >= 2:
        injury = "minor"
    return {
        "injury": injury,
        "hazard_score": score,
        "visible_causes": visible_causes,
        "preventable": True,
        "good_preparation_prevents": resolve_good_preparation(),
    }


def resolve_good_preparation() -> bool:
    result = {"accepted": False, "protection": True, "warning_ignored": False, "stabilization_delayed": False}
    score = int(result["accepted"]) + int(not result["protection"]) + int(result["warning_ignored"]) + int(result["stabilization_delayed"])
    return score < 2


def forecast_stock(
    config: dict[str, Any], stock: str, amount: float, *, resident_count: int = 4
) -> dict[str, Any]:
    return forecasts.stock_forecast_card(
        config, stock, amount, resident_count=resident_count
    )


def calculate_power(
    config: dict[str, Any],
    completed_projects: set[str],
    *,
    storm_affected_systems: int = 0,
    demand_multiplier: float = 1.0,
) -> dict[str, Any]:
    power = config["utilities"]["power"]
    capacity = power["source_capacity"] * power["condition"]
    active_loads = {
        key: power["loads"][key]
        for key in [
            "service_alcove",
            "air_filtration",
            "water_pumping",
            "relay_kiosk",
            "task_lighting",
        ]
    }
    if "triage_cot_install" in completed_projects:
        active_loads["medical_equipment"] = power["loads"]["medical_equipment"]
    if "workshop_install" in completed_projects:
        active_loads["workshop"] = power["loads"]["workshop"]
    if "comfort_lighting" in completed_projects:
        active_loads["comfort_lighting"] = power["loads"]["comfort_lighting"]
    if storm_affected_systems >= 1:
        active_loads["storm_air_overdraw"] = 1.5 * storm_affected_systems
    demand = sum(active_loads.values()) * demand_multiplier
    headroom = capacity - demand
    shutdown = []
    remaining_deficit = max(0.0, -headroom)
    if remaining_deficit > EPSILON:
        for load_name in power["shed_order"]:
            if load_name in active_loads and remaining_deficit > EPSILON:
                shutdown.append(load_name)
                remaining_deficit -= active_loads[load_name] * demand_multiplier
    return {
        "capacity": rounded(capacity),
        "demand": rounded(demand),
        "headroom": rounded(headroom),
        "condition": power["condition"],
        "loads": {key: rounded(value * demand_multiplier) for key, value in active_loads.items()},
        "shutdown_order_if_uncovered": shutdown,
        "priority_tiers": copy.deepcopy(power["priority_tiers"]),
        "first_shed_load": shutdown[0] if shutdown else None,
        "next_endangered": "water_pumping" if headroom < 0 else None,
    }


def calculate_air(
    config: dict[str, Any],
    completed_projects: set[str],
    resident_count: int,
    *,
    storm_profile: str | None = None,
    filter_condition_multiplier: float = 1.0,
) -> dict[str, Any]:
    air = config["utilities"]["air"]
    condition = air["initial_filter_condition"]
    if "storm_filter_prep" in completed_projects:
        condition += 0.18
    condition = min(1.0, condition * filter_condition_multiplier)
    cinder_demand = {None: 0.0, "prepared": 3.0, "partial": 4.0, "unprepared": 5.0, "neglect": 5.0}[storm_profile]
    capacity = air["nominal_capacity"] * condition
    demand = resident_count * air["resident_demand"] + air["room_process_demand"] + cinder_demand
    headroom = capacity - demand
    if headroom >= 1.0:
        state = "stable"
    elif headroom >= 0.0:
        state = "loaded"
    elif headroom >= -2.0:
        state = "degraded"
    elif headroom >= -4.0:
        state = "exposure"
    else:
        state = "evacuate"
    return {
        "capacity": rounded(capacity),
        "demand": rounded(demand),
        "headroom": rounded(headroom),
        "filter_condition": rounded(condition),
        "state": state,
        "failing_link": "filter condition" if headroom < 0 else None,
        "warning_before_exposure": state in {"loaded", "degraded"},
        "exposure_window_stages": air["exposure_window_stages"],
        "responses": copy.deepcopy(air["responses"]),
    }


def calculate_water_utility(
    config: dict[str, Any], route: str, completed_projects: set[str], resident_count: int, *, impaired: bool = False
) -> dict[str, Any]:
    water = config["utilities"]["water"]
    if route == "west" and "west_water_treatment" in completed_projects:
        source = water["west_source_capacity_after_upgrade"]
    else:
        source = water["east_source_capacity"]
    pump = water["pump_availability"] * (0.6 if impaired else 1.0)
    treatment = water["treatment_efficiency"] * (0.75 if impaired else 1.0)
    delivered = source * pump * treatment * water["delivery_efficiency"]
    demand = resident_count * config["stocks"]["Clean Water"]["normal_per_resident_day"]
    headroom = delivered - demand
    if impaired:
        link = "pump availability and treatment"
    elif headroom < 0:
        link = "source capacity"
    else:
        link = None
    diagnosis = utilities.diagnose_water_link(
        config,
        source=source,
        pump=pump,
        treatment=treatment,
        delivery=water["delivery_efficiency"],
        storage_state="suspect" if impaired else "clean",
        demand=demand,
    )
    diagnosis.update(
        {
            "source_capacity": rounded(source),
            "pump_availability": rounded(pump),
            "treatment_efficiency": rounded(treatment),
            "delivery": rounded(delivered),
            "headroom": rounded(headroom),
            "contamination_state": "suspect" if impaired else "clean",
            "failing_link": link or diagnosis["failing_link"],
        }
    )
    return diagnosis


def calculate_structure(
    route: str, completed_projects: set[str], injury_state: str = "none", *, force_closed: bool = False
) -> dict[str, Any]:
    reclaim_id = f"{route}_reclaim"
    if force_closed:
        state = "closed"
    elif reclaim_id not in completed_projects:
        state = "unstable"
    elif injury_state == "serious":
        state = "strained"
    else:
        state = "safe"
    return {
        "state": state,
        "warning": state in {"unstable", "critical"},
        "access_open": state not in {"critical", "closed"},
        "injury_risk_visible": state in {"unstable", "critical"},
    }


def resolve_expedition(
    config: dict[str, Any], route: str, mode: str, options: dict[str, Any] | None = None
) -> dict[str, Any]:
    expedition = config["expedition"]
    options = options or {}
    outcome = options.get("outcome", "complete")
    carry_capacity = int(options.get("carry_capacity", expedition["default_carry_capacity"]))
    tool = options.get("tool", expedition["preferred_tool"])
    optional_policy = options.get("optional_policy", "skip")
    required_component = config["routes"][route]["required_expedition_component"]
    required_secured = outcome not in {"missing_required_reward", "retreat_before_required"}
    wrong_tool = tool != expedition["preferred_tool"]
    travel_time = sum(edge["time"] for edge in expedition["edges"][:2]) + 1.0
    noise = sum(edge["noise"] for edge in expedition["edges"][:2])
    if wrong_tool:
        travel_time += expedition["wrong_tool_extra_time"]
        noise += expedition["wrong_tool_extra_noise"]
    slots_used = 0
    components: dict[str, int] = {}
    stocks: dict[str, float] = {}
    choices: list[str] = []
    if required_secured and carry_capacity >= expedition["required_component_slots"]:
        components[required_component] = 1
        slots_used += expedition["required_component_slots"]
        choices.append(f"secured {required_component}")
    if required_secured and carry_capacity - slots_used >= expedition["materials_slots"]:
        stocks["Materials"] = expedition["materials_reward"]
        slots_used += expedition["materials_slots"]
        choices.append("secured Materials")
    optional_secured = False
    if optional_policy == "attempt" and carry_capacity - slots_used >= expedition["optional_reward_slots"]:
        components["radio_component"] = 1
        slots_used += expedition["optional_reward_slots"]
        optional_secured = True
        choices.append("secured radio_component")
    elif optional_policy == "attempt":
        choices.append("left optional reward due to carry limit")
    retreat = outcome.startswith("retreat")
    partial = retreat or not optional_secured
    delegated_policy = None
    if mode == "delegated":
        delegated_policy = {
            "objective_priority": options.get("objective_priority", "required_component"),
            "risk_tolerance": options.get("risk_tolerance", "medium"),
            "retreat_threshold": options.get(
                "retreat_threshold", "objective_secured"
            ),
            "tool_use_policy": options.get("tool_use_policy", "preserve_if_alternative"),
            "aid_or_theft_boundary": options.get(
                "aid_or_theft_boundary", "do_not_take_claimed_aid"
            ),
        }
    save_points = ["gate", "service_passage"]
    if required_secured:
        save_points.append("maintenance_cage")
    if optional_secured:
        save_points.append("control_booth")
    save_points.append("exit")
    return {
        "graph_id": expedition["id"],
        "mode": mode,
        "same_graph_facts": True,
        "required_component": required_component,
        "required_secured": required_secured,
        "optional_secured": optional_secured,
        "stocks": stocks,
        "components": components,
        "travel_cost": rounded(travel_time),
        "noise": noise,
        "air_protection_required": expedition["air_protection_required"],
        "carry_capacity": carry_capacity,
        "slots_used": slots_used,
        "wrong_tool_alternative_used": wrong_tool,
        "retreat": retreat,
        "partial_success": partial,
        "persistent_state": {"maintenance_cage_open": required_secured, "optional_cache_taken": optional_secured},
        "save_points": save_points,
        "real_minutes": expedition["active_real_minutes"] if mode == "active" else expedition["delegated_real_minutes"],
        "exclusive_reward": False,
        "delegated_policy": delegated_policy,
        "choices": choices,
    }


def highball_cost(config: dict[str, Any], use_number: int) -> dict[str, Any]:
    if use_number < 1:
        raise ValueError("Highball use number must be positive")
    if use_number == 1:
        return copy.deepcopy(config["highball"]["first_use"])
    return copy.deepcopy(config["highball"]["consecutive_use"])


def highball_saved_work(work: float, benefit: float) -> float:
    return rounded(work - work / (1.0 + benefit))


def start_named_treatment(
    state: SimulationState,
    config: dict[str, Any],
    *,
    treatment_id: str,
    resident: str,
    condition: str,
    severity: str,
    room_available: bool = True,
    skilled_staff_available: bool = True,
    medicine_multiplier: float = 1.0,
) -> dict[str, Any]:
    if treatment_id in state.treatments:
        return copy.deepcopy(state.treatments[treatment_id])
    plan = medical.treatment_plan(
        config,
        treatment_id,
        resident,
        condition,
        severity,
        room_available=room_available,
        skilled_staff_available=skilled_staff_available,
    )
    if plan["blockers"]:
        return plan
    plan["medicine_reserved"] = rounded(
        plan["medicine_reserved"] * float(medicine_multiplier)
    )

    def mutation() -> None:
        consume_stock(
            state,
            "Medicine",
            plan["medicine_reserved"],
            f"treatment {treatment_id} Medicine reservation",
        )
        consume_stock(
            state,
            "Clean Water",
            plan["water_reserved"],
            f"treatment {treatment_id} Clean Water reservation",
        )
        state.treatments[treatment_id] = copy.deepcopy(plan)
        state.treatment_open = True

    commit_once(state, plan["reservation_id"], mutation)
    return copy.deepcopy(state.treatments[treatment_id])


def interrupt_named_treatment(
    state: SimulationState, treatment_id: str, reason: str
) -> dict[str, Any]:
    if treatment_id not in state.treatments:
        raise KeyError(treatment_id)

    def mutation() -> None:
        state.treatments[treatment_id] = medical.interrupt_treatment(
            state.treatments[treatment_id], reason
        )

    commit_once(state, f"treatment:{treatment_id}:interrupt", mutation)
    return copy.deepcopy(state.treatments[treatment_id])


def complete_named_treatment(
    state: SimulationState,
    treatment_id: str,
    *,
    current_health: float = 70.0,
    precondition_max_health: float = 100.0,
) -> dict[str, Any]:
    if treatment_id not in state.treatments:
        raise KeyError(treatment_id)

    def mutation() -> None:
        record = state.treatments[treatment_id]
        if record["status"] == "interrupted":
            record = medical.resume_treatment(record)
        state.treatments[treatment_id] = medical.complete_treatment(
            record,
            current_health=current_health,
            precondition_max_health=precondition_max_health,
        )
        state.treatment_open = any(
            item["status"] != "completed" for item in state.treatments.values()
        )

    commit_once(state, f"treatment:{treatment_id}:completion", mutation)
    return copy.deepcopy(state.treatments[treatment_id])


def apply_relay_load_test(
    state: SimulationState,
    config: dict[str, Any],
    response: str,
    *,
    branch_connected: bool = True,
) -> dict[str, Any]:
    if state.relay_load_test_state:
        return copy.deepcopy(state.relay_load_test_state)
    result = utilities.relay_load_test(
        config,
        response,
        state.stocks["Charge"],
        branch_connected=branch_connected,
    )

    def mutation() -> None:
        if result["charge_draw"] > 0:
            consume_stock(
                state,
                "Charge",
                result["charge_draw"],
                "Relay Load Test connected reserve",
            )
        state.relay_load_test_state = copy.deepcopy(result)

    commit_once(state, f"relay_load_test:{response}", mutation)
    return copy.deepcopy(state.relay_load_test_state)


def resolve_hope_beat(
    config: dict[str, Any],
    completed_projects: set[str],
    *,
    available_work: float,
    force_minimal: bool = False,
) -> dict[str, Any]:
    full_id = config["hope_beats"]["full_project"]
    if full_id in completed_projects and not force_minimal:
        full_work = next(
            project["work"] for project in config["projects"] if project["id"] == full_id
        )
        return {
            "type": "full",
            "id": full_id,
            "work": float(full_work),
            "uses_earned_state": True,
            "creates_resources": False,
            "supports_recover_first": True,
        }
    eligible = [
        item
        for item in config["hope_beats"]["fallbacks"]
        if item["requires_project"] in completed_projects
        and float(item["work"]) <= max(0.0, available_work) + EPSILON
    ]
    if not eligible:
        return {
            "type": "none",
            "id": None,
            "work": 0.0,
            "uses_earned_state": False,
            "creates_resources": False,
            "supports_recover_first": False,
        }
    choice = sorted(eligible, key=lambda item: (item["work"], item["id"]))[0]
    return {
        "type": "minimal",
        "id": choice["id"],
        "work": float(choice["work"]),
        "requires_project": choice["requires_project"],
        "uses_earned_state": True,
        "creates_resources": bool(choice["creates_resources"]),
        "supports_recover_first": True,
    }


def highball_strain_tier(config: dict[str, Any], strain: int) -> tuple[str, dict[str, Any]]:
    for name, data in config["highball"]["strain_tiers"].items():
        if int(data["minimum"]) <= strain <= int(data["maximum"]):
            return name, copy.deepcopy(data)
    raise ValueError(f"strain {strain} does not match a configured tier")


def derive_outcome_class(
    config: dict[str, Any],
    *,
    invariant_errors: list[str],
    shelter_failures: list[str],
    proof_gaps: list[str],
    recover_first_reasons: list[str],
    ending_eligibility: dict[str, bool],
    force_proof_incomplete: bool = False,
) -> dict[str, Any]:
    if invariant_errors:
        outcome = "INVARIANT_ERROR"
        limiting = invariant_errors[0]
    elif shelter_failures:
        outcome = "SHELTER_FAILURE"
        limiting = shelter_failures[0]
    elif force_proof_incomplete or proof_gaps:
        if recover_first_reasons and ending_eligibility.get("recover_first") and not force_proof_incomplete:
            outcome = "RECOVER_FIRST"
            limiting = recover_first_reasons[0]
        else:
            outcome = "PROOF_INCOMPLETE"
            limiting = proof_gaps[0] if proof_gaps else "required release-slice proof missing"
    elif recover_first_reasons:
        outcome = "RECOVER_FIRST"
        limiting = recover_first_reasons[0]
    elif any(
        ending_eligibility.get(name, False)
        for name in ["prepare_the_platform", "root_the_settlement", "strengthen_the_relay"]
    ):
        outcome = "FULL_PROOF"
        limiting = "all mandatory survival and slice-proof gates met"
    else:
        outcome = "PROOF_INCOMPLETE"
        limiting = "no supported Day 7 direction"
    return {
        "outcome_class": outcome,
        "survival_viable": outcome not in {"SHELTER_FAILURE", "INVARIANT_ERROR"},
        "slice_proof_complete": outcome == "FULL_PROOF",
        "ending_directions_available": [
            name for name, available in ending_eligibility.items() if available
        ],
        "recover_first_available": bool(ending_eligibility.get("recover_first")),
        "invariant_valid": outcome != "INVARIANT_ERROR",
        "viable": outcome in {"FULL_PROOF", "RECOVER_FIRST"},
        "exact_limiting_fact": limiting,
        "definition": config["outcome_classes"][outcome],
    }


def resolve_incident_case(
    state: SimulationState,
    config: dict[str, Any],
    *,
    family: str,
    response: str | None = None,
    second_major_family: str | None = None,
    queue_minor: bool = False,
    isolate: bool = False,
    evacuate: bool = False,
    recover: bool = True,
) -> dict[str, Any]:
    primary = incidents.create_incident(
        config, f"case:{family}", family, section="test_section"
    )
    active: list[dict[str, Any]] = []
    queued: list[dict[str, Any]] = []
    start = incidents.schedule_incident(active, queued, primary)
    primary = incidents.advance_incident(primary)
    scheduling: list[dict[str, Any]] = [start]
    if second_major_family:
        second = incidents.create_incident(
            config,
            f"case:{second_major_family}:queued",
            second_major_family,
            section="adjacent",
        )
        scheduling.append(incidents.schedule_incident(active, queued, second))
    if queue_minor:
        minor = incidents.create_incident(
            config,
            "case:equipment_breakdown:minor",
            "equipment_breakdown",
            section="central",
        )
        queued.append(minor)
    if response:
        primary = incidents.interrupt_incident(
            primary, response, isolate=isolate, evacuate=evacuate
        )
    if recover and primary["current_stage"] == "recovery":
        primary = incidents.recover_incident(primary)
    if active:
        active[0] = copy.deepcopy(primary)
    state.incidents[primary["incident_id"]] = copy.deepcopy(primary)
    state.incident_queue = copy.deepcopy(queued)
    restored = SimulationState.from_json(state.to_json())
    return {
        "incident": copy.deepcopy(primary),
        "scheduling": scheduling,
        "queued": copy.deepcopy(queued),
        "major_live_count": sum(
            1 for item in active if item["major"] and item["status"] == "active"
        ),
        "second_major_started": not any(item.get("queued") for item in scheduling[1:]),
        "save_roundtrip_equal": restored.to_json() == state.to_json(),
        "recovery_work": float(primary["recovery_work"]),
    }


def calculate_schedule_resilience(
    state: SimulationState,
    selected_projects: dict[str, dict[str, Any]],
    day_reports: list[dict[str, Any]],
    *,
    total_project_capacity: float,
    total_project_used: float,
) -> dict[str, Any]:
    daily_uncommitted = [
        float(day["work"]["daily_uncommitted"]) for day in day_reports
    ]
    phase_slack = [
        float(day["work"]["minimum_phase_slack"]) for day in day_reports
    ]
    critical_path: dict[str, float] = {}
    for project_id, project in selected_projects.items():
        if project["tier"] not in {"mandatory", "route_mandatory", "ambition"}:
            continue
        hard_day = int(project.get("hard_deadline_day", project["deadline_day"]))
        progress = state.projects[project_id]
        if progress.completion_day is None:
            critical_path[project_id] = rounded(
                -progress.remaining_work / max(1.0, float(project["work"]))
            )
        else:
            critical_path[project_id] = rounded(hard_day - progress.completion_day)
    aggregate_unused = rounded(total_project_capacity - total_project_used)
    incident_reserve = rounded(
        sum(day["work"]["incident_reserve"] for day in day_reports)
    )
    incident_reserve_unused = rounded(
        sum(day["work"]["incident_reserve_unused"] for day in day_reports)
    )
    return {
        "aggregate_weekly_unused_work": aggregate_unused,
        "minimum_daily_uncommitted_work": rounded(min(daily_uncommitted)),
        "minimum_phase_slack": rounded(min(phase_slack)),
        "critical_path_slack_by_project_days": critical_path,
        "minimum_critical_path_slack_days": rounded(min(critical_path.values())),
        "incident_response_reserve": incident_reserve,
        "incident_response_reserve_unused": incident_reserve_unused,
        "carryover_capacity": rounded(sum(max(0.0, value) for value in daily_uncommitted)),
        "optional_work_capacity": rounded(
            sum(
                max(0.0, day["work"]["buffer"])
                for day in day_reports
                if day["day"] >= 4
            )
        ),
        "emergency_recovery_capacity": rounded(
            incident_reserve_unused + max(0.0, day_reports[-1]["work"]["buffer"])
        ),
        "critical_days": {
            str(day["day"]): {
                "daily_uncommitted": day["work"]["daily_uncommitted"],
                "phase_slack": day["work"]["minimum_phase_slack"],
            }
            for day in day_reports
            if day["day"] in {2, 3, 5, 6}
        },
        "aggregate_is_not_complete_safety_margin": True,
    }


def build_prompt3_case_evidence(
    state: SimulationState,
    config: dict[str, Any],
    options: dict[str, Any],
    day_reports: list[dict[str, Any]],
) -> dict[str, Any] | None:
    case = options.get("prompt3_case")
    if not case:
        return None
    evidence: dict[str, Any] = {"case": case, "executed": True}
    probe = options.get("capacity_probe")
    if probe:
        profile = calculate_resident_work_profile(
            config,
            probe.get("resident", "Ash"),
            probe.get("conditions"),
            availability=probe.get("availability", 1.0),
            medical_restriction=probe.get("medical_restriction", "none"),
        )
        evidence["capacity_probe"] = profile
        evidence["self_action_counted_as_project_work"] = False
    if options.get("all_medically_unavailable_probe"):
        profiles = [
            calculate_resident_work_profile(
                config,
                resident,
                medical_restriction="medically_incapacitated",
            )
            for resident in ["Ash", "Imka", "Teo", "Maren"]
        ]
        evidence["shelter_emergency_probe"] = survival.shelter_emergency_capacity(
            profiles, config["work"]["minimum_emergency_shelter_capacity"]
        )
    incident_probe = options.get("incident_probe")
    if incident_probe:
        evidence["incident_probe"] = resolve_incident_case(
            state,
            config,
            family=incident_probe["family"],
            response=incident_probe.get("response"),
            second_major_family=incident_probe.get("second_major_family"),
            queue_minor=incident_probe.get("queue_minor", False),
            isolate=incident_probe.get("isolate", False),
            evacuate=incident_probe.get("evacuate", False),
            recover=incident_probe.get("recover", True),
        )
    medical_probe = options.get("medical_probe")
    if medical_probe:
        probe_state = SimulationState.from_json(state.to_json())
        plan = start_named_treatment(
            probe_state,
            config,
            treatment_id=f"probe:{case}",
            resident=medical_probe.get("resident", "Teo"),
            condition=medical_probe["condition"],
            severity=medical_probe["severity"],
        )
        if medical_probe.get("interrupt"):
            plan = interrupt_named_treatment(
                probe_state, plan["treatment_id"], "scenario interruption"
            )
        if medical_probe.get("complete"):
            plan = complete_named_treatment(
                probe_state,
                plan["treatment_id"],
                current_health=medical_probe.get("current_health", 70.0),
                precondition_max_health=medical_probe.get(
                    "precondition_max_health", 100.0
                ),
            )
        restored = SimulationState.from_json(probe_state.to_json())
        evidence["medical_probe"] = plan
        evidence["medical_save_roundtrip"] = restored.to_json() == probe_state.to_json()
    charge_probe = options.get("charge_probe")
    if charge_probe:
        evidence["charge_probe"] = utilities.discharge_charge(
            config,
            charge_probe.get("available", state.stocks["Charge"]),
            charge_probe.get("requested", 1.0),
            branch_connected=charge_probe.get("connected", True),
            stages=charge_probe.get("stages", 1),
        )
    air_probe = options.get("air_probe")
    if air_probe:
        evidence["air_probe"] = utilities.progress_air_stage(
            config,
            air_probe.get("current", "stable"),
            air_probe.get("pressure_steps", 1),
            air_probe.get("interruption_steps", 0),
        )
    structure_probe = options.get("structure_probe")
    if structure_probe:
        evidence["structure_probe"] = utilities.structure_transition(
            config,
            structure_probe.get("current", "strained"),
            structure_probe.get("pressure_steps", 1),
            structure_probe.get("reinforcement_steps", 0),
        )
    if options.get("cascade_probe"):
        evidence["cascade_probe"] = incidents.validate_cascade(
            state.storm_state.get("cascade", config["storm"]["cascade_order"]),
            config["storm"]["maximum_affected_systems"],
        )
    if options.get("save_every_incident_stage"):
        snapshots = []
        probe_incident = incidents.create_incident(
            config, f"save:{case}", "air_contamination"
        )
        for _ in range(4):
            snapshots.append(json.dumps(probe_incident, sort_keys=True))
            probe_incident = incidents.advance_incident(probe_incident)
        evidence["incident_stage_snapshots"] = snapshots
        evidence["incident_stage_roundtrip"] = all(
            json.loads(snapshot) == json.loads(json.dumps(json.loads(snapshot)))
            for snapshot in snapshots
        )
    if options.get("highball_duplicate_probe"):
        before_stocks = copy.deepcopy(state.stocks)
        selected, _ = _selected_projects(
            config, options["route"], options
        )
        _, repeated = _apply_highball_setup(
            state, config, selected, options
        )
        evidence["highball_duplicate_probe"] = {
            "stocks_unchanged": state.stocks == before_stocks,
            "same_order_state": repeated == state.highball_state,
            "cost_commit_count": sum(
                action == "highball:order:costs"
                for action in state.committed_actions
            ),
            "duplicate_benefit_prevented": (
                state.stocks == before_stocks
                and repeated == state.highball_state
            ),
        }
    if options.get("medicine_priority"):
        priority = config["resource_response_values"]["medicine_prioritization"]
        evidence["medicine_prioritization"] = {
            "stabilization_protected": True,
            "deferred_followup_medicine": priority[
                "deferred_followup_medicine"
            ],
            "stress_points": priority["stress_points"],
            "recovery_delay_days": priority["recovery_delay_days"],
            "free_medicine_created": False,
        }
    if options.get("relay_restore_probe"):
        relay = state.relay_load_test_state
        evidence["relay_restore_probe"] = {
            "response": relay.get("response"),
            "visible_before": relay.get("lighting_visible_before"),
            "visible_during": relay.get("lighting_visible_during"),
            "visible_next_stable_phase": relay.get("lighting_restored"),
            "restored_without_new_charge": relay.get("charge_draw", 0.0) == 0.0,
        }
    resilience_probe = options.get("resilience_probe")
    if resilience_probe == "minimum_daily_uncommitted_work":
        evidence["resilience_probe"] = {
            "metric": resilience_probe,
            "value": min(day["work"]["daily_uncommitted"] for day in day_reports),
            "by_day": {
                str(day["day"]): day["work"]["daily_uncommitted"]
                for day in day_reports
            },
        }
    elif resilience_probe == "critical_path_slack":
        evidence["resilience_probe"] = {
            "metric": resilience_probe,
            "minimum_phase_deadline_days": min(
                phase["critical_path_slack_days"]
                for day in day_reports
                for phase in day["phases"]
            ),
        }
    elif resilience_probe == "incident_response_reserve":
        evidence["resilience_probe"] = {
            "metric": resilience_probe,
            "reserved": rounded(
                sum(day["work"]["incident_reserve"] for day in day_reports)
            ),
            "used": rounded(
                sum(day["work"]["incident_reserve_used"] for day in day_reports)
            ),
            "unused": rounded(
                sum(day["work"]["incident_reserve_unused"] for day in day_reports)
            ),
        }
    if options.get("hope_probe"):
        evidence["hope_probe"] = copy.deepcopy(state.hope_state)
    resource_probe = options.get("resource_pressure_probe")
    if resource_probe:
        final_day = day_reports[-1]
        evidence["resource_pressure_probe"] = {
            "stock": resource_probe,
            "ending": final_day["stocks_end"][resource_probe],
            "minimum": final_day["minimum_stock_to_date"][resource_probe],
            "forecast_status": final_day["stock_forecasts"][resource_probe]["status"],
            "minimum_viable_reserve": config["stocks"][resource_probe][
                "minimum_viable_reserve"
            ],
        }
    if options.get("failure_cause_probe"):
        evidence["failure_cause_probe"] = {
            "storm_profile": state.storm_state.get("profile"),
            "cascade": copy.deepcopy(state.storm_state.get("cascade", [])),
            "recoverable": state.storm_state.get("recoverable"),
            "failures": list(state.failures),
        }
    if options.get("response_work_probe"):
        storm_day = next(day for day in day_reports if day["day"] == 5)
        evidence["response_work_probe"] = {
            "actual_incident_work": storm_day["work"]["incident_response"],
            "reserve_used": storm_day["work"]["incident_reserve_used"],
            "overflow": storm_day["work"]["incident_overflow"],
            "daily_uncommitted": storm_day["work"]["daily_uncommitted"],
        }
    if options.get("inject_invariant_error"):
        state.invariant_errors.append(str(options["inject_invariant_error"]))
        evidence["invariant_detected"] = True
    if options.get("no_hidden_work_probe"):
        checks = []
        for day in day_reports:
            work = day["work"]
            accounted = (
                work["personal_overhead"]
                + work["travel"]
                + work["hauling"]
                + work["highball_or_promise_loss"]
                + work["essential_operation_requirement"]
                + work["incident_reserve"]
                + work["incident_overflow"]
                + work["treatment_and_rest"]
                - work["highball_or_promise_loss"]
                + work["mistake_rework"]
                + work["risk_preparation"]
                + work["project_used"]
                + work["buffer"]
            )
            checks.append(
                {
                    "day": day["day"],
                    "gross": work["gross"],
                    "accounted": rounded(accounted),
                    "difference": rounded(work["gross"] - accounted),
                }
            )
        evidence["work_accounting"] = checks
        evidence["all_work_accounted"] = all(
            abs(item["difference"]) <= 0.002 for item in checks
        )
    evidence["distinct_output_marker"] = f"executed:{case}"
    return evidence


def _selected_projects(
    config: dict[str, Any], route: str, options: dict[str, Any]
) -> tuple[dict[str, dict[str, Any]], set[str]]:
    selected: dict[str, dict[str, Any]] = {}
    omitted = set(options.get("omit_projects", []))
    if options.get("omit_project"):
        omitted.add(options["omit_project"])
    selected_optional = options.get("optional_project")
    construction_multiplier = options.get("modifiers", {}).get("construction_work_multiplier", 1.0)
    for source in config["projects"]:
        if source["route"] not in {"all", route}:
            continue
        if source["tier"] == "optional" and source["id"] != selected_optional:
            continue
        if source["id"] in omitted:
            continue
        project = copy.deepcopy(source)
        project["work"] = rounded(project["work"] * construction_multiplier)
        if project["id"] == "route_survey":
            key = f"{route}_survey_work_reduction"
            project["work"] = max(1.0, rounded(project["work"] - config["signals"][options["signal"]][key]))
        disruption = options.get("role_disruption")
        if disruption and project["role"] == disruption.get("role"):
            project["work"] = rounded(project["work"] + disruption.get("extra_work", 0.0))
        selected[project["id"]] = project
    return selected, omitted


def _initial_state(config: dict[str, Any], selected_projects: dict[str, dict[str, Any]], modifiers: dict[str, Any]) -> SimulationState:
    stocks = {name: float(data["start"]) for name, data in config["stocks"].items()}
    charge_multiplier = modifiers.get("charge_capacity_multiplier", 1.0)
    stocks["Charge"] = min(stocks["Charge"], config["stocks"]["Charge"]["capacity"] * charge_multiplier)
    project_states = {
        project_id: ProjectProgress(
            project_id=project_id,
            required_work=project["work"],
            remaining_work=project["work"],
        )
        for project_id, project in selected_projects.items()
    }
    state = SimulationState(
        day=1,
        phase="swelter",
        stocks=stocks,
        components={name: int(data["start"]) for name, data in config["components"].items()},
        stock_minima=copy.deepcopy(stocks),
        projects=project_states,
        functional_areas=config["initial_shelter"]["functional_areas"],
        rest_capacity=config["initial_shelter"]["rest_capacity"],
        temporary_rest_capacity=config["initial_shelter"]["temporary_rest_capacity"],
    )
    state.benefits["charge_capacity_multiplier"] = charge_multiplier
    return state


def _reserve_project(
    state: SimulationState, config: dict[str, Any], project: dict[str, Any], progress: ProjectProgress
) -> bool:
    if progress.status != "planned":
        return progress.status == "active"
    if state.stocks["Materials"] + EPSILON < project["materials"]:
        progress.block_reason = f"missing Materials ({project['materials']})"
        return False
    for component, count in project["components"].items():
        if state.components.get(component, 0) < count:
            progress.block_reason = f"missing component {component}"
            return False

    def mutation() -> None:
        consume_stock(state, "Materials", project["materials"], f"reserve {project['id']}")
        progress.reserved_materials = project["materials"]
        for component, count in project["components"].items():
            state.components[component] -= count
            progress.reserved_components[component] = count
        progress.status = "active"
        progress.block_reason = None

    commit_once(state, f"project:{project['id']}:reserve", mutation)
    return progress.status == "active"


def _complete_project(
    state: SimulationState,
    config: dict[str, Any],
    project: dict[str, Any],
    progress: ProjectProgress,
    route: str,
) -> None:
    def mutation() -> None:
        progress.status = "completed"
        progress.remaining_work = 0.0
        progress.completion_day = state.day
        state.completed_projects.add(project["id"])
        for benefit, value in project["benefits"].items():
            state.benefits[benefit] = state.benefits.get(benefit, 0.0) + value
        state.functional_areas += int(project["benefits"].get("functional_areas", 0))
        state.rest_capacity += int(project["benefits"].get("rest_capacity", 0))
        state.temporary_rest_capacity += int(project["benefits"].get("temporary_rest_capacity", 0))
        if project["id"] == f"{route}_reclaim":
            grant_reward_once(
                state,
                config,
                f"reward:{project['id']}:salvage",
                stocks={"Materials": config["routes"][route]["completion_material_salvage"]},
            )

    commit_once(state, f"project:{project['id']}:complete", mutation)


def cancel_project(
    state: SimulationState,
    config: dict[str, Any],
    selected_projects: dict[str, dict[str, Any]],
    project_id: str,
) -> float:
    progress = state.projects[project_id]
    if progress.status != "active":
        return 0.0
    project = selected_projects[project_id]
    refund_fraction = config["work"]["project_classes"][project["class"]]["cancellation_refund"]
    refunded = rounded(progress.reserved_materials * refund_fraction)

    def mutation() -> None:
        progress.status = "cancelled"
        progress.cancellation_day = state.day
        grant_reward_once(
            state,
            config,
            f"refund:{project_id}",
            stocks={"Materials": refunded},
        )

    committed = commit_once(state, f"project:{project_id}:cancel", mutation)
    return refunded if committed else 0.0


def _allocate_project_work(
    state: SimulationState,
    config: dict[str, Any],
    selected_projects: dict[str, dict[str, Any]],
    capacity: float,
    options: dict[str, Any],
) -> tuple[float, list[dict[str, Any]]]:
    work_log: list[dict[str, Any]] = []
    remaining_capacity = max(0.0, capacity)
    optional_id = options.get("optional_project")
    force_optional = optional_id == "comfort_lighting" and state.day == 2
    priority_optional = optional_id == "visitor_screen" and state.day == 5
    forced_optional_budget = min(5.0, remaining_capacity) if force_optional else remaining_capacity

    def dependencies_done(project: dict[str, Any]) -> bool:
        return all(dependency in state.completed_projects for dependency in project["dependencies"])

    def priority(project_id: str) -> tuple[int, int, int, str]:
        project = selected_projects[project_id]
        progress = state.projects[project_id]
        special = 0 if ((force_optional or priority_optional) and project_id == optional_id) else 1
        active = 0 if progress.status == "active" else 1
        tier = 0 if project["tier"] in {"mandatory", "route_mandatory"} else 2
        return (special, project["deadline_day"], active + tier, project_id)

    while remaining_capacity > EPSILON:
        candidates = [
            project_id
            for project_id, project in selected_projects.items()
            if state.projects[project_id].status in {"planned", "active"}
            and project["available_day"] <= state.day
            and dependencies_done(project)
        ]
        if not candidates:
            break
        candidates.sort(key=priority)
        progressed = False
        for project_id in candidates:
            project = selected_projects[project_id]
            progress = state.projects[project_id]
            if not _reserve_project(state, config, project, progress):
                continue
            allowed = remaining_capacity
            if force_optional and project_id == optional_id:
                allowed = min(allowed, forced_optional_budget)
            amount = min(progress.remaining_work, allowed)
            if amount <= EPSILON:
                continue
            progress.remaining_work = rounded(progress.remaining_work - amount)
            progress.applied_work = rounded(progress.applied_work + amount)
            remaining_capacity = rounded(remaining_capacity - amount)
            work_log.append(
                {
                    "project": project_id,
                    "work": rounded(amount),
                    "remaining": rounded(progress.remaining_work),
                }
            )
            progressed = True
            if progress.remaining_work <= EPSILON:
                _complete_project(state, config, project, progress, options["route"])
            if force_optional and project_id == optional_id:
                force_optional = False
            break
        if not progressed:
            break
    used = rounded(capacity - remaining_capacity)
    return used, work_log


def _apply_trader(
    state: SimulationState, config: dict[str, Any], signal_name: str
) -> dict[str, Any]:
    signal = config["signals"][signal_name]
    cost = signal["trader_cost_materials"]
    if state.stocks["Materials"] < cost:
        return {"arrived": True, "trade_completed": False, "reason": "insufficient Materials"}

    def mutation() -> None:
        consume_stock(state, "Materials", cost, f"trader {signal_name}")
        grant_reward_once(
            state,
            config,
            f"trader:{signal_name}",
            stocks=signal.get("trader_gains", {}),
            components=signal.get("trader_components", {}),
        )
        state.outside_contact = True

    commit_once(state, f"trader:{signal_name}:exchange", mutation)
    return {
        "arrived": True,
        "trade_completed": True,
        "cost_materials": cost,
        "gains": signal.get("trader_gains", {}),
        "components": signal.get("trader_components", {}),
    }


def _apply_expedition(
    state: SimulationState,
    config: dict[str, Any],
    route: str,
    mode: str,
    expedition_options: dict[str, Any] | None,
) -> dict[str, Any]:
    result = resolve_expedition(config, route, mode, expedition_options)

    def mutation() -> None:
        grant_reward_once(
            state,
            config,
            "expedition:harbor_annex:primary",
            stocks=result["stocks"],
            components=result["components"],
        )
        state.expedition_state = copy.deepcopy(result)
        if result["optional_secured"]:
            state.signal_evidence += 1

    commit_once(state, "expedition:harbor_annex:resolve", mutation)
    return result


def _apply_juna(
    state: SimulationState,
    config: dict[str, Any],
    options: dict[str, Any],
    modifiers: dict[str, Any],
) -> dict[str, Any]:
    juna = config["juna"]
    mode = options.get("juna_mode", "delay")
    report: dict[str, Any] = {"mode": mode, "admitted": False, "work_available": 0.0}
    state.outside_contact = True
    if mode in {"admit_prepared", "admit_temporary"}:
        medicine_multiplier = modifiers.get("medicine_use_multiplier", 1.0)
        water_cost = juna["stabilization_water"]
        medicine_cost = juna["stabilization_medicine"] * medicine_multiplier
        if options.get("juna_long_recovery"):
            water_cost += juna["long_recovery_extra_water"]
            medicine_cost += juna["long_recovery_extra_medicine"] * medicine_multiplier
        consume_stock(state, "Clean Water", water_cost, "Juna stabilization")
        consume_stock(state, "Medicine", medicine_cost, "Juna stabilization")
        state.juna_admitted = True
        state.juna_state = "recovering"
        total_rest = state.rest_capacity + state.temporary_rest_capacity
        if "rest_capacity_override" in options:
            total_rest = int(options["rest_capacity_override"])
        prepared = total_rest >= juna["prepared_rest_capacity_required"]
        if mode == "admit_prepared" and not prepared:
            state.failures.append("Juna prepared admission lacks declared rest capacity")
        report.update(
            {
                "admitted": True,
                "prepared_rest": prepared,
                "rest_capacity": total_rest,
                "stabilization_water": rounded(water_cost),
                "stabilization_medicine": rounded(medicine_cost),
                "work_available": float(options.get("juna_work_day_7", juna["day_7_limited_work"])),
                "long_recovery": bool(options.get("juna_long_recovery")),
            }
        )
    else:
        aid = juna["delay_or_refusal_aid"]
        for stock, amount in aid.items():
            consume_stock(state, stock, amount, f"Juna {mode} aid")
        state.juna_state = "delayed_with_aid" if mode == "delay" else "refused_with_aid"
        report.update({"aid": aid, "viable_alternative": True})
    return report


def _derive_storm_profile(state: SimulationState, route: str) -> str:
    prepared_ids = {"storm_filter_prep", f"{route}_water_reserve" if route == "east" else "west_drain_isolation"}
    count = len(prepared_ids & state.completed_projects)
    if count >= 2:
        return "prepared"
    if count == 1:
        return "partial"
    return "unprepared"


def resolve_storm(
    state: SimulationState,
    config: dict[str, Any],
    route: str,
    signal_name: str,
    options: dict[str, Any],
    modifiers: dict[str, Any],
) -> dict[str, Any]:
    storm = config["storm"]
    profile_name = options.get("storm_profile") or _derive_storm_profile(state, route)
    profile = copy.deepcopy(storm["profiles"][profile_name])
    intensity = modifiers.get("storm_intensity_multiplier", 1.0)
    profile["response_work"] *= intensity
    profile["charge_use"] *= intensity
    profile["water_loss"] *= intensity
    strategy_name = options.get("storm_strategy", "filter_service")
    if strategy_name in storm["response_strategies"]:
        strategy = storm["response_strategies"][strategy_name]
        profile["response_work"] += strategy["response_work_delta"]
        profile["affected_systems"] += strategy["affected_systems_delta"]
        profile["charge_use"] += strategy["charge_delta"]
        profile["water_loss"] += strategy["water_loss_delta"]
    highball = options.get("highball")
    if highball and highball.get("context") == "emergency_repair":
        profile["response_work"] /= 1.0 + highball["benefit"]
    profile["response_work"] += modifiers.get("short_warning_extra_response_work", 0.0)
    affected = max(1, min(storm["maximum_affected_systems"], int(round(profile["affected_systems"]))))
    cascade = storm["cascade_order"][:affected]
    water_reduction = config["signals"][signal_name]["water_loss_reduction"]
    if route == "east" and "east_water_reserve" in state.completed_projects:
        water_reduction += 3.0
    if route == "west" and "west_drain_isolation" in state.completed_projects:
        water_reduction += 4.0
    water_loss = max(0.0, profile["water_loss"] - water_reduction)
    charge_requested = max(0.0, profile["charge_use"])
    max_discharge = config["stocks"]["Charge"]["discharge_limit_per_stage"] * affected
    charge_requested = min(charge_requested, max_discharge)
    discharge = utilities.discharge_charge(
        config,
        state.stocks["Charge"],
        charge_requested,
        branch_connected=True,
        stages=affected,
    )
    charge_use = discharge["stock_draw"]
    consume_stock(state, "Charge", charge_use, "storm Power deficit", critical=False)
    charge_shortfall = max(0.0, charge_requested - discharge["delivered"])
    if charge_shortfall > EPSILON:
        water_loss += charge_shortfall * 0.5
    consume_stock(state, "Clean Water", water_loss, "storm Water impairment")
    medicine_multiplier = modifiers.get("medicine_use_multiplier", 1.0)
    consume_stock(
        state,
        "Medicine",
        profile["medicine_use"] * medicine_multiplier,
        "storm respiratory treatment",
    )
    lead = max(
        0,
        storm["base_lead_stages"]
        + config["signals"][signal_name]["storm_lead_bonus"]
        - modifiers.get("storm_lead_reduction", 0),
    )
    stages = [
        {
            "system": system,
            **storm["plain_language_stages"][system],
            "interruption_point": index < affected,
        }
        for index, system in enumerate(cascade, start=1)
    ]
    result = {
        "profile": profile_name,
        "forecast_source": storm["forecast_source"],
        "confidence": storm["base_confidence"],
        "warning_lead_stages": lead,
        "initial_pressure": storm["initial_pressure"],
        "affected_system_count": affected,
        "cascade": cascade,
        "bounded": affected <= storm["maximum_affected_systems"],
        "major_crises": 1,
        "interruptible": True,
        "strategy": strategy_name,
        "response_work": rounded(profile["response_work"]),
        "charge_use": rounded(charge_use),
        "charge_requested_delivery": rounded(charge_requested),
        "charge_delivered": discharge["delivered"],
        "charge_conversion_loss": discharge["conversion_loss"],
        "water_loss": rounded(water_loss),
        "medicine_use": rounded(profile["medicine_use"] * medicine_multiplier),
        "next_day_capacity_loss": rounded(profile["next_day_capacity_loss"]),
        "recoverable": bool(profile["recoverable"]),
        "stages": stages,
        "physical_aftermath": "filter residue, load-shed rooms, water marks, and visible repair state",
        "human_aftermath": "Fatigue, treatment, promise repayment, and recovery work",
    }
    storm_incident = incidents.create_incident(
        config, f"day5:{route}:cinder", "air_contamination", section=route
    )
    storm_incident["cascade"] = copy.deepcopy(cascade)
    storm_incident["maximum_propagation_depth"] = storm["maximum_affected_systems"]
    storm_incident["current_stage"] = (
        "severe" if profile_name == "neglect" else "recovery"
    )
    storm_incident["status"] = "active" if profile_name == "neglect" else "resolved"
    storm_incident["transaction_ids"].extend(
        f"incident:day5:{route}:stage:{index}"
        for index in range(1, affected + 1)
    )
    state.incidents[storm_incident["incident_id"]] = storm_incident
    result["incident"] = copy.deepcopy(storm_incident)
    state.storm_state = copy.deepcopy(result)
    if not result["recoverable"]:
        state.failures.append("Extended storm neglect produced an unrecoverable slice state")
    return result


def _apply_highball_setup(
    state: SimulationState,
    config: dict[str, Any],
    selected_projects: dict[str, dict[str, Any]],
    options: dict[str, Any],
) -> tuple[dict[int, float], dict[str, Any] | None]:
    highball = options.get("highball")
    if not highball:
        return {}, None
    if state.highball_state:
        stored = copy.deepcopy(state.highball_state)
        return {
            int(day): float(value)
            for day, value in stored.get("capacity_losses", {}).items()
        }, stored
    worker = highball.get("resident", "Teo")
    medical_restriction = highball.get("medical_restriction", "none")
    if medical_restriction in config["highball"]["medical_ineligibility"]:
        report = {
            "uses": 0,
            "requested_uses": int(highball.get("uses", 1)),
            "candidate_benefit": float(
                highball.get("benefit", config["highball"]["baseline_candidate"])
            ),
            "provisional": True,
            "production_multiplier_selected": False,
            "resident": worker,
            "eligible": False,
            "rejection_reason": f"{worker} is medically restricted: {medical_restriction}",
            "work_saved": 0.0,
            "strain": 0,
            "hidden_random_risk": False,
        }
        state.highball_state = copy.deepcopy(report)
        return {}, report
    uses = int(highball.get("uses", 1))
    if uses > config["highball"]["maximum_consecutive_uses"]:
        state.failures.append("Highball requested beyond consecutive-use limit")
        uses = config["highball"]["maximum_consecutive_uses"]
    benefit = float(highball.get("benefit", config["highball"]["baseline_candidate"]))
    if benefit not in config["highball"]["candidate_benefits"]:
        state.failures.append(f"Highball benefit {benefit} was not a tested candidate")
    context = highball.get("context", "route_project")
    if context == "route_project":
        target_id = f"{options['route']}_reclaim"
        order_day = 2
        repayment_day = 5
    elif context == "storm_preparation":
        target_id = "storm_filter_prep"
        order_day = 4
        repayment_day = 6
    else:
        target_id = None
        order_day = 5
        repayment_day = 6
    saved = 0.0
    if target_id and target_id in selected_projects:
        original = selected_projects[target_id]["work"]
        selected_projects[target_id]["work"] = rounded(
            original / ((1.0 + benefit) ** uses)
        )
        progress = state.projects[target_id]
        progress.required_work = selected_projects[target_id]["work"]
        progress.remaining_work = selected_projects[target_id]["work"]
        saved = rounded(original - selected_projects[target_id]["work"])
    cost_breakdown = [
        highball_cost(config, use_number) for use_number in range(1, uses + 1)
    ]
    costs = {
        key: rounded(sum(item[key] for item in cost_breakdown))
        for key in cost_breakdown[0]
    }
    strain = int(costs.pop("strain"))
    equipment_condition = float(highball.get("equipment_condition", 1.0))
    if equipment_condition < config["highball"]["low_equipment_condition_threshold"]:
        strain += int(config["highball"]["low_equipment_extra_strain"])
    strain_name, strain_data = highball_strain_tier(config, strain)

    def commit_costs() -> None:
        consume_stock(state, "Charge", costs["charge_cost"], "Highball order")
        consume_stock(
            state, "Materials", costs["materials_wear"], "Highball material wear"
        )

    commit_once(state, "highball:order:costs", commit_costs)
    capacity_losses: dict[int, float] = {
        repayment_day: costs["fatigue_capacity_loss_next_day"]
        + float(strain_data["inspection_work"])
    }
    promise = highball.get("promise", "kept")
    if promise == "kept":
        capacity_losses[repayment_day] += costs["promised_rest_work"]
    else:
        breach = config["highball"]["promise_breach"]
        split = breach["capacity_loss_over_two_days"] / 2.0
        capacity_losses[repayment_day] += split
        capacity_losses[min(7, repayment_day + 1)] = split
    report = {
        "uses": uses,
        "candidate_benefit": benefit,
        "provisional": True,
        "production_multiplier_selected": False,
        "context": context,
        "resident": worker,
        "eligible": True,
        "order_day": order_day,
        "target_project": target_id,
        "work_saved": saved,
        "costs": costs,
        "cost_breakdown": cost_breakdown,
        "promise": promise,
        "capacity_losses": capacity_losses,
        "net_week_work_value": rounded(saved - sum(capacity_losses.values())),
        "strain": strain,
        "strain_tier": strain_name,
        "inspection_work": float(strain_data["inspection_work"]),
        "another_use_blocked": bool(strain_data["another_use_blocked"]),
        "equipment_condition": equipment_condition,
        "guaranteed_impairment_if_emergency_override": bool(
            strain_data["another_use_blocked"]
        ),
        "hidden_random_risk": False,
        "emotional_effects_are_placeholder": True,
        "refuses_next_highball": promise == "breached",
    }
    state.promises["highball_rest"] = {
        "resident": worker,
        "status": promise,
        "due_day": repayment_day,
        "work": costs["promised_rest_work"],
    }
    state.highball_state = copy.deepcopy(report)
    return capacity_losses, report


def _conditions_for(
    options: dict[str, Any], resident: str, day: int
) -> dict[str, str]:
    conditions = default_conditions()
    if resident == "Teo" and day == 1 and not options.get("treatment_delay"):
        conditions["health"] = "strained"
    if resident == "Teo" and options.get("treatment_delay") and day in {1, 2}:
        conditions["health"] = "impaired" if day == 2 else "strained"
    event = options.get("condition_event")
    if event and event.get("resident") == resident and day in event.get("days", []):
        for key in ["health", "hunger", "fatigue", "stress"]:
            if key in event:
                conditions[key] = event[key]
    return conditions


def _stress_band(config: dict[str, Any], points: int) -> str:
    bands = config["work"]["stress_point_bands"]
    if points < bands["steady_below"]:
        return "steady"
    if points < bands["elevated_below"]:
        return "elevated"
    if points < bands["high_below"]:
        return "high"
    return "acute"


def _daily_capacity(
    config: dict[str, Any], route: str, day: int, options: dict[str, Any], capacity_losses: dict[int, float], juna_report: dict[str, Any] | None
) -> dict[str, Any]:
    work = config["work"]
    modifiers = options.get("modifiers", {})
    global_multiplier = modifiers.get("work_capacity_multiplier", 1.0)
    availability = {name: 1.0 for name in ["Ash", "Imka", "Teo", "Maren"]}
    absence = options.get("absence")
    if absence and absence.get("day") == day:
        availability[absence["resident"]] = float(absence["availability"])
    restriction_map = copy.deepcopy(options.get("resident_medical_restrictions", {}))
    restriction_event = options.get("medical_restriction_event")
    if restriction_event and day in restriction_event.get("days", [restriction_event.get("day")]):
        restriction_map[restriction_event["resident"]] = restriction_event["restriction"]
    resident_profiles = {
        resident: calculate_resident_work_profile(
            config,
            resident,
            _conditions_for(options, resident, day),
            availability=availability[resident],
            global_multiplier=global_multiplier,
            medical_restriction=restriction_map.get(resident, "none"),
        )
        for resident in availability
    }
    resident_capacity = {
        resident: profile["productive_capacity"]
        for resident, profile in resident_profiles.items()
    }
    gross = sum(resident_capacity.values())
    if day >= 4:
        gross *= config["routes"][route]["work_capacity_multiplier_after_day_3"]
    juna_work = 0.0
    if day == 7 and juna_report and juna_report.get("admitted"):
        juna_work = float(juna_report.get("work_available", 0.0))
        gross += juna_work
    available_equivalents = sum(availability.values()) + (0.25 if juna_work > 0 else 0.0)
    personal = work["personal_overhead_per_available_resident"] * available_equivalents
    travel_profile = config["routes"][route]["travel_profile"]
    travel_multiplier = modifiers.get("travel_overhead_multiplier", 1.0)
    travel = gross * work["travel_profiles"][travel_profile] * travel_multiplier
    hauling = gross * work["hauling_rate"] * travel_multiplier
    emergency = survival.shelter_emergency_capacity(
        list(resident_profiles.values()),
        work["minimum_emergency_shelter_capacity"],
    )
    return {
        "available_residents": [name for name, fraction in availability.items() if fraction > 0],
        "resident_availability": availability,
        "resident_capacity": {key: rounded(value) for key, value in resident_capacity.items()},
        "resident_work_profiles": resident_profiles,
        "medically_restricted_residents": [
            name
            for name, profile in resident_profiles.items()
            if profile["current_work_restriction"]
            in {
                "critical_health",
                "collapse_risk",
                "medically_incapacitated",
                "critical_untreated_injury",
                "collapse",
                "unconscious",
                "severe_respiratory",
            }
        ],
        "shelter_emergency_capacity": emergency,
        "juna_limited_work": rounded(juna_work),
        "gross": rounded(gross),
        "personal_overhead": rounded(personal),
        "travel": rounded(travel),
        "hauling": rounded(hauling),
        "highball_or_promise_loss": rounded(capacity_losses.get(day, 0.0)),
    }


def _session_budget(config: dict[str, Any], day: int, expedition_mode: str, storm_response_work: float, options: dict[str, Any]) -> dict[str, Any]:
    phases = config["time"]["phases"]
    swelter = phases["swelter"]["baseline_minutes"]
    slack = phases["slack"]["baseline_minutes"]
    graymorn = phases["graymorn"]["baseline_minutes"]
    nightrun = 0.0
    decisions = 6
    if day == 3:
        if expedition_mode == "active":
            nightrun = phases["nightrun"]["active_baseline_minutes"]
            decisions += phases["nightrun"]["active_maximum_useful_decisions"]
        else:
            nightrun = phases["nightrun"]["delegated_baseline_minutes"]
            decisions += phases["nightrun"]["delegated_maximum_useful_decisions"]
    if day == 5:
        swelter += min(1.2, storm_response_work * 0.05)
        decisions += 2
    if day == 6:
        slack += 0.6
        decisions += 1
    total = swelter + slack + nightrun + graymorn
    return {
        "phase_minutes": {
            "swelter": rounded(swelter),
            "slack": rounded(slack),
            "nightrun": rounded(nightrun),
            "graymorn": rounded(graymorn),
        },
        "total_minutes": rounded(total),
        "maximum_useful_decisions": decisions,
        "reduced_motion_minutes": rounded(total * config["time"]["accessibility_timing"]["reduced_motion_camera_multiplier"]),
        "large_text_minutes": rounded(total * config["time"]["accessibility_timing"]["large_text_reading_multiplier"]),
        "combined_accessibility_minutes": rounded(total * config["time"]["accessibility_timing"]["combined_session_multiplier"]),
        "modeled_not_measured": True,
    }


def _ending_eligibility(
    state: SimulationState,
    config: dict[str, Any],
    storm_profile: str,
    survival_viable: bool,
    *,
    recovery_needed: bool = False,
) -> dict[str, bool]:
    req = config["ending_requirements"]

    def stocks_meet(requirements: dict[str, float]) -> bool:
        return all(state.stocks[name] + EPSILON >= amount for name, amount in requirements.items())

    prepare = (
        all(project in state.completed_projects for project in req["prepare_platform"]["required_projects"])
        and state.signal_evidence >= req["prepare_platform"]["minimum_signal_evidence"]
        and stocks_meet(req["prepare_platform"]["minimum_stocks"])
        and storm_profile != "neglect"
    )
    root = (
        state.functional_areas >= req["root_settlement"]["minimum_functional_areas"]
        and state.rest_capacity + state.temporary_rest_capacity >= req["root_settlement"]["minimum_rest_capacity"]
        and stocks_meet(req["root_settlement"]["minimum_stocks"])
        and state.storm_state.get("recoverable", True)
    )
    relay = (
        all(project in state.completed_projects for project in req["strengthen_relay"]["required_projects"])
        and state.signal_evidence >= req["strengthen_relay"]["minimum_signal_evidence"]
        and state.stocks["Charge"] >= req["strengthen_relay"]["minimum_charge"]
        and state.outside_contact
    )
    recover = survival_viable and (
        storm_profile != "prepared" or state.treatment_open or recovery_needed
    )
    return {
        "prepare_the_platform": prepare,
        "root_the_settlement": root,
        "strengthen_the_relay": relay,
        "recover_first": recover,
    }


def run_save_probe(state: SimulationState, config: dict[str, Any], probe: str | None) -> dict[str, Any] | None:
    if not probe:
        return None
    before = state.to_json()
    restored = SimulationState.from_json(before)
    roundtrip_equal = restored.to_json() == before
    reward_id = f"probe:{probe}:reward"
    first = grant_reward_once(restored, config, reward_id, stocks={"Materials": 1.0})
    after_first = restored.stocks["Materials"]
    second = grant_reward_once(restored, config, reward_id, stocks={"Materials": 1.0})
    duplicate_prevented = first and not second and math.isclose(restored.stocks["Materials"], after_first)
    paused = background_without_advancement(restored, elapsed_seconds=86400)
    offline_unchanged = paused.to_json() == restored.to_json()
    return {
        "probe": probe,
        "roundtrip_equal": roundtrip_equal,
        "duplicate_reward_prevented": duplicate_prevented,
        "offline_unchanged": offline_unchanged,
        "passed": roundtrip_equal and duplicate_prevented and offline_unchanged,
    }


def background_without_advancement(state: SimulationState, elapsed_seconds: int) -> SimulationState:
    del elapsed_seconds
    return SimulationState.from_json(state.to_json())


def simulate_scenario(config: dict[str, Any], scenario: dict[str, Any]) -> dict[str, Any]:
    route = scenario["route"]
    signal_name = scenario["signal"]
    options = copy.deepcopy(scenario.get("options", {}))
    options["route"] = route
    options["signal"] = signal_name
    modifiers = options.get("modifiers", {})
    selected_projects, omitted = _selected_projects(config, route, options)
    state = _initial_state(config, selected_projects, modifiers)
    if options.get("materials_shortage"):
        shortage = float(
            options.get(
                "materials_shortage_amount",
                config["resource_response_values"]["materials_shortage"]["loss"],
            )
        )
        consume_stock(
            state,
            "Materials",
            shortage,
            "forecast Materials shortage",
            critical=False,
        )
    capacity_losses, highball_report = _apply_highball_setup(
        state, config, selected_projects, options
    )
    construction_risk = resolve_construction_risk(options.get("construction_risk"))
    state.injury_state = construction_risk["injury"]
    day_reports: list[dict[str, Any]] = []
    expedition_mode = options.get("expedition_mode", "delegated")
    trader_report: dict[str, Any] | None = None
    expedition_report: dict[str, Any] | None = None
    juna_report: dict[str, Any] | None = None
    storm_report: dict[str, Any] | None = None
    relay_load_test_report: dict[str, Any] | None = None
    incident_case_report: dict[str, Any] | None = None
    total_project_capacity = 0.0
    total_project_used = 0.0
    total_essential = 0.0
    hunger_state = "fed"
    stress_points = 0
    consecutive_ration_days = 0

    for day in range(1, 8):
        state.day = day
        state.phase = "swelter"
        stocks_start = copy.deepcopy(state.stocks)
        day_warnings: list[str] = []

        if day == config["signals"][signal_name]["trader_day"]:
            trader_report = _apply_trader(state, config, signal_name)
        food_response = options.get("food_response", {})
        if (
            food_response.get("type") == "trader"
            and day == config["resource_response_values"]["food_trader"]["day"]
        ):
            response = config["resource_response_values"]["food_trader"]

            def food_trade_mutation() -> None:
                consume_stock(
                    state,
                    "Materials",
                    response["materials_cost"],
                    "Food pressure trader exchange",
                )
                grant_reward_once(
                    state,
                    config,
                    "resource_response:food_trader",
                    stocks={"Food": response["food_gain"]},
                )

            commit_once(state, "resource_response:food_trader:exchange", food_trade_mutation)
        if day == config["juna"]["arrival_day"]:
            juna_report = _apply_juna(state, config, options, modifiers)
        if day == config["relay_load_test"]["day"]:
            relay_response = options.get("relay_load_test_response", "shed_lighting")
            relay_load_test_report = apply_relay_load_test(
                state,
                config,
                relay_response,
                branch_connected=not options.get("relay_branch_disconnected", False),
            )
            if relay_load_test_report.get("warning_lead_delta", 0) < 0:
                modifiers["storm_lead_reduction"] = modifiers.get(
                    "storm_lead_reduction", 0
                ) + abs(relay_load_test_report["warning_lead_delta"])

        treatment_work = 0.0
        if day == 1 and not options.get("treatment_delay"):
            treatment = start_named_treatment(
                state,
                config,
                treatment_id="teo:respiratory:early",
                resident="Teo",
                condition="respiratory_exposure",
                severity="limited",
                medicine_multiplier=modifiers.get("medicine_use_multiplier", 1.0),
            )
            treatment_work += treatment["medical_work"]
            complete_named_treatment(
                state,
                treatment["treatment_id"],
                current_health=75.0,
                precondition_max_health=100.0,
            )
        if day == 2 and options.get("treatment_delay"):
            treatment = start_named_treatment(
                state,
                config,
                treatment_id="teo:respiratory:delayed",
                resident="Teo",
                condition="respiratory_exposure",
                severity="severe",
                medicine_multiplier=modifiers.get("medicine_use_multiplier", 1.0),
            )
            treatment_work += treatment["medical_work"]
        if day == 2 and construction_risk["injury"] != "none":
            serious = construction_risk["injury"] == "serious"
            condition = "serious_injury" if serious else "minor_injury"
            severity = "serious" if serious else "minor"
            treatment = start_named_treatment(
                state,
                config,
                treatment_id=f"construction:{condition}",
                resident="Ash",
                condition=condition,
                severity=severity,
                medicine_multiplier=modifiers.get("medicine_use_multiplier", 1.0),
            )
            treatment_work += treatment["medical_work"]
        if day == int(options.get("waterborne_illness_day", -1)):
            treatment = start_named_treatment(
                state,
                config,
                treatment_id="waterborne:case",
                resident=options.get("waterborne_resident", "Maren"),
                condition="waterborne_illness",
                severity=options.get("waterborne_severity", "moderate"),
                medicine_multiplier=modifiers.get("medicine_use_multiplier", 1.0),
            )
            treatment_work += treatment["medical_work"]
        if day == 3 and "teo:respiratory:delayed" in state.treatments:
            if options.get("treatment_interrupted"):
                interrupt_named_treatment(
                    state, "teo:respiratory:delayed", "Power shed during care"
                )
            else:
                complete_named_treatment(state, "teo:respiratory:delayed")
        if day == 3 and "construction:minor_injury" in state.treatments:
            complete_named_treatment(state, "construction:minor_injury")
        if day == 4 and "construction:serious_injury" in state.treatments:
            complete_named_treatment(state, "construction:serious_injury")
        if day == 4 and options.get("treatment_interrupted") and "teo:respiratory:delayed" in state.treatments:
            complete_named_treatment(state, "teo:respiratory:delayed")
        if day == int(options.get("waterborne_illness_day", -1)) + 1 and "waterborne:case" in state.treatments:
            complete_named_treatment(state, "waterborne:case")
        if day == 1:
            treatment_work += float(options.get("treatment_extra_work", 0.0))
            extra_medicine = float(options.get("treatment_extra_medicine", 0.0))
            if extra_medicine:
                consume_stock(state, "Medicine", extra_medicine, "backup treatment inefficiency")

        incident_work = 0.0
        if day == config["storm"]["day"]:
            storm_report = resolve_storm(
                state, config, route, signal_name, options, modifiers
            )
            incident_work = storm_report["response_work"]
            capacity_losses[6] = capacity_losses.get(6, 0.0) + storm_report["next_day_capacity_loss"]
        incident_probe = options.get("incident_probe")
        if incident_probe and day == int(options.get("incident_day", 4)):
            incident_case_report = resolve_incident_case(
                state,
                config,
                family=incident_probe["family"],
                response=incident_probe.get("response"),
                second_major_family=incident_probe.get("second_major_family"),
                queue_minor=incident_probe.get("queue_minor", False),
                isolate=incident_probe.get("isolate", False),
                evacuate=incident_probe.get("evacuate", False),
                recover=incident_probe.get("recover", True),
            )
        disruption = options.get("ordinary_disruption")
        if disruption and disruption.get("day") == day:
            incident_work += float(disruption.get("work", 0.0))
        for minor in options.get("minor_disruptions", []):
            if minor.get("day") == day:
                incident_work += float(minor.get("work", 0.0))

        capacity = _daily_capacity(
            config, route, day, options, capacity_losses, juna_report
        )
        essential_work = config["work"]["daily_essential_work"]
        incident_reserve = config["work"]["daily_incident_reserve"]
        incident_reserve_used = min(incident_reserve, incident_work)
        incident_reserve_unused = max(0.0, incident_reserve - incident_reserve_used)
        incident_overflow = max(0.0, incident_work - incident_reserve)
        if day == 3:
            essential_work += config["work"]["nightrun_preparation_work"]
        if day == 6:
            essential_work += config["work"]["visitor_processing_work"]
        if (
            day == 7
            and storm_report
            and storm_report["profile"] == "unprepared"
            and storm_report["recoverable"]
        ):
            essential_work -= 4.0
            day_warnings.append(
                "Recovery shift: four work units moved from noncritical routine operations to visible storm recovery"
            )
        extra_essential = options.get("essential_work_extra")
        if extra_essential and extra_essential.get("day") == day:
            essential_work += extra_essential.get("work", 0.0)
        mistake = options.get("construction_mistake")
        mistake_work = 0.0
        if mistake and mistake.get("day") == day:
            mistake_work = float(mistake.get("rework", 0.0))
            consume_stock(state, "Materials", mistake.get("materials_loss", 0.0), "construction mistake")
        risk_preparation_work = (
            float(options.get("risk_preparation_work", 0.0)) if day == 2 else 0.0
        )

        nonproject = (
            capacity["personal_overhead"]
            + capacity["travel"]
            + capacity["hauling"]
            + capacity["highball_or_promise_loss"]
            + essential_work
            + incident_reserve
            + treatment_work
            + incident_overflow
            + mistake_work
            + risk_preparation_work
        )
        project_capacity = max(0.0, capacity["gross"] - nonproject)
        total_project_capacity += project_capacity
        total_essential += essential_work + incident_reserve + treatment_work + incident_overflow + mistake_work
        total_essential += risk_preparation_work
        if not capacity["shelter_emergency_capacity"]["met"]:
            reason = (
                f"Day {day} shelter labor pool cannot supply minimum emergency survival work; "
                "incapacitated residents are not forced to work"
            )
            if options.get("outside_emergency_fallback"):
                day_warnings.append(reason + "; declared outside/manual fallback used")
                state.recovery_reasons.append(reason)
            elif reason not in state.failures:
                state.failures.append(reason)

        if options.get("cancel_optional_day") == day and options.get("optional_project") in state.projects:
            cancel_project(
                state, config, selected_projects, options["optional_project"]
            )
        project_used, project_work_log = _allocate_project_work(
            state, config, selected_projects, project_capacity, options
        )
        total_project_used += project_used
        project_work_by_tier = {
            "mandatory": 0.0,
            "route_mandatory": 0.0,
            "ambition": 0.0,
            "optional": 0.0,
        }
        for work_entry in project_work_log:
            tier = selected_projects[work_entry["project"]]["tier"]
            project_work_by_tier[tier] = rounded(
                project_work_by_tier[tier] + work_entry["work"]
            )

        for project_id, project in selected_projects.items():
            progress = state.projects[project_id]
            if project["tier"] == "optional":
                continue
            if project["deadline_day"] == day and progress.status != "completed":
                miss = f"{project_id} missed Day {day} target; carryover cost applies"
                if miss not in state.target_misses:
                    state.target_misses.append(miss)
                    state.warnings.append(miss)
            hard_deadline = project.get("hard_deadline_day", project["deadline_day"])
            if hard_deadline == day and progress.status != "completed":
                miss = f"{project_id} missed hard Day {day} deadline"
                if miss not in state.deadline_misses:
                    state.deadline_misses.append(miss)

        if day == 3:
            expedition_report = _apply_expedition(
                state,
                config,
                route,
                expedition_mode,
                options.get("expedition"),
            )
            if food_response.get("type") == "expedition":
                response = config["resource_response_values"]["food_expedition_choice"]

                def food_expedition_mutation() -> None:
                    consume_stock(
                        state,
                        "Materials",
                        response["materials_opportunity_cost"],
                        "Food expedition carry opportunity",
                    )
                    grant_reward_once(
                        state,
                        config,
                        "resource_response:food_expedition",
                        stocks={"Food": response["food_gain"]},
                    )

                commit_once(
                    state,
                    "resource_response:food_expedition:choice",
                    food_expedition_mutation,
                )

        resident_count = 4 + int(state.juna_admitted)
        food_multiplier = modifiers.get("food_consumption_multiplier", 1.0)
        water_multiplier = modifiers.get("water_consumption_multiplier", 1.0)
        ration_days = set(food_response.get("days", []))
        food_issue_type = "restricted" if day in ration_days else "normal"
        food_plan = survival.food_issue(
            config, resident_count, issue=food_issue_type
        )
        if food_issue_type == "restricted":
            consecutive_ration_days += 1
        else:
            consecutive_ration_days = 0
        ration_effect = survival.ration_consequence(
            config, consecutive_ration_days
        )
        hunger_state = ration_effect["hunger_band"]
        stress_points += ration_effect["stress_points"]
        consume_stock(
            state,
            "Food",
            food_plan["amount"] * food_multiplier,
            f"Day {day} {food_issue_type} ration",
        )
        water_response = options.get("water_response", {})
        water_days = set(water_response.get("days", []))
        water_issue_type = "restricted" if day in water_days else "normal"
        water_plan = survival.water_issue(
            config, resident_count, issue=water_issue_type
        )
        stress_points += water_plan["stress_points"]
        consume_stock(
            state,
            "Clean Water",
            water_plan["amount"] * water_multiplier,
            f"Day {day} {water_issue_type} water issue",
        )
        stress_band = _stress_band(config, stress_points)
        for resident, profile in capacity["resident_work_profiles"].items():
            resident_conditions = copy.deepcopy(profile["conditions"])
            resident_conditions["hunger"] = hunger_state
            resident_conditions["stress"] = stress_band
            state.resident_conditions[resident] = resident_conditions
        signature_id = config["routes"][route]["signature_project"]
        if signature_id in state.completed_projects:
            add_stock(
                state,
                config,
                "Clean Water",
                config["routes"][route]["daily_water_production_after_signature_room"],
            )
        if day == 7 and juna_report and juna_report.get("admitted") and juna_report.get("work_available", 0.0) > 0:
            add_stock(state, config, "Clean Water", config["juna"]["day_7_water_contribution_if_recovered"])
            state.juna_state = "limited_help"

        storm_systems = storm_report["affected_system_count"] if day == 5 and storm_report else 0
        power = calculate_power(
            config,
            state.completed_projects,
            storm_affected_systems=storm_systems,
            demand_multiplier=modifiers.get("power_demand_multiplier", 1.0),
        )
        active_storm_profile = storm_report["profile"] if day == 5 and storm_report else None
        air = calculate_air(
            config,
            state.completed_projects,
            resident_count,
            storm_profile=active_storm_profile,
            filter_condition_multiplier=modifiers.get("filter_condition_multiplier", 1.0),
        )
        water = calculate_water_utility(
            config,
            route,
            state.completed_projects,
            resident_count,
            impaired=bool(day == 5 and storm_report and "Water" in storm_report["cascade"]),
        )
        structure = calculate_structure(route, state.completed_projects, state.injury_state)
        session = _session_budget(
            config,
            day,
            expedition_mode,
            incident_work,
            options,
        )
        stock_forecasts = {
            name: forecast_stock(
                config, name, value, resident_count=resident_count
            )
            for name, value in state.stocks.items()
        }
        day_buffer = rounded(project_capacity - project_used)
        exact_day_reason = None
        if project_capacity <= EPSILON:
            exact_day_reason = "No project capacity after essential work and interruptions"
        elif state.deadline_misses:
            exact_day_reason = state.deadline_misses[-1]
        elif state.target_misses:
            exact_day_reason = state.target_misses[-1]
        open_deadline_slack = [
            int(project.get("hard_deadline_day", project["deadline_day"])) - day
            for project_id, project in selected_projects.items()
            if project["tier"] in {"mandatory", "route_mandatory", "ambition"}
            and project_id not in state.completed_projects
        ]
        phase_critical_path_slack = min(open_deadline_slack) if open_deadline_slack else 0
        emergency_actions_available = list(config["emergency_actions"])
        phases = [
            {
                "phase": "swelter",
                "project_capacity": rounded(project_capacity),
                "project_work": rounded(project_used),
                "safe_save": True,
                "autosave_points": ["entry", "each project transaction", "stable incident stage", "exit"],
            },
            {
                "phase": "slack",
                "signal": signal_name,
                "decision_pause": True,
                "safe_save": True,
                "autosave_points": ["signal commitment", "loadout", "exit"],
            },
            {
                "phase": "nightrun",
                "mode": expedition_mode if day == 3 else "none",
                "state": expedition_report if day == 3 else {"committed_no_run": True},
                "safe_save": True,
                "autosave_points": expedition_report["save_points"] if day == 3 else ["no-run commit"],
            },
            {
                "phase": "graymorn",
                "stocks_end": copy.deepcopy(state.stocks),
                "ledger_committed": True,
                "safe_save": True,
                "autosave_points": ["before ledger", "after treatment", "accepted ledger"],
            },
        ]
        phase_utility_snapshot = {
            "Power": {"headroom": power["headroom"], "condition": power["condition"]},
            "Air": {"headroom": air["headroom"], "state": air["state"]},
            "Water": {
                "headroom": water["headroom"],
                "condition": water["contamination_state"],
                "failing_link": water["failing_link"],
            },
            "Structure": {
                "condition": structure["state"],
                "access_open": structure["access_open"],
            },
        }
        for phase in phases:
            phase.update(
                {
                    "available_residents": capacity["available_residents"],
                    "productive_capacity": capacity["gross"],
                    "medically_restricted_residents": capacity[
                        "medically_restricted_residents"
                    ],
                    "essential_operation_work": rounded(
                        essential_work if phase["phase"] == "swelter" else 0.0
                    ),
                    "incident_reserve": rounded(
                        incident_reserve if phase["phase"] == "swelter" else 0.0
                    ),
                    "critical_path_slack_days": phase_critical_path_slack,
                    "stocks": copy.deepcopy(state.stocks),
                    "condition_summary": {
                        "hunger": hunger_state,
                        "fatigue_restrictions": capacity[
                            "medically_restricted_residents"
                        ],
                        "stress": stress_band,
                        "health_contexts": sorted(state.contextual_conditions),
                    },
                    "utilities": copy.deepcopy(phase_utility_snapshot),
                    "forecast_status": {
                        name: card["status"] for name, card in stock_forecasts.items()
                    },
                    "emergency_actions_available": emergency_actions_available,
                    "active_promises": copy.deepcopy(state.promises),
                    "outcome_status": "IN_PROGRESS",
                }
            )
        day_reports.append(
            {
                "day": day,
                "available_residents": capacity["available_residents"],
                "resident_availability": capacity["resident_availability"],
                "work": {
                    **capacity,
                    "essential": rounded(essential_work),
                    "essential_operation_requirement": rounded(essential_work),
                    "incident_reserve": rounded(incident_reserve),
                    "incident_reserve_used": rounded(incident_reserve_used),
                    "incident_reserve_unused": rounded(incident_reserve_unused),
                    "incident_overflow": rounded(incident_overflow),
                    "treatment_and_rest": rounded(treatment_work + capacity["highball_or_promise_loss"]),
                    "incident_response": rounded(incident_work),
                    "mistake_rework": rounded(mistake_work),
                    "risk_preparation": rounded(risk_preparation_work),
                    "project_capacity": rounded(project_capacity),
                    "project_used": rounded(project_used),
                    "mandatory_shared_project_work": project_work_by_tier["mandatory"],
                    "mandatory_route_project_work": project_work_by_tier["route_mandatory"],
                    "optional_project_work": project_work_by_tier["optional"],
                    "ambition_project_work": project_work_by_tier["ambition"],
                    "buffer": day_buffer,
                    "daily_uncommitted": rounded(day_buffer + incident_reserve_unused),
                    "minimum_phase_slack": rounded(incident_reserve_unused),
                },
                "project_work_log": project_work_log,
                "projects_completed": sorted(
                    project_id
                    for project_id, progress in state.projects.items()
                    if progress.completion_day == day
                ),
                "stocks_start": stocks_start,
                "stocks_end": copy.deepcopy(state.stocks),
                "minimum_stock_to_date": copy.deepcopy(state.stock_minima),
                "stock_forecasts": stock_forecasts,
                "resident_conditions": copy.deepcopy(state.resident_conditions),
                "condition_summary": {
                    "hunger": hunger_state,
                    "stress": stress_band,
                    "stress_points": stress_points,
                    "ration_consequence": ration_effect,
                },
                "food_issue": food_plan,
                "water_issue": water_plan,
                "medical_conditions": copy.deepcopy(state.contextual_conditions),
                "treatments": copy.deepcopy(state.treatments),
                "utilities": {
                    "Power": power,
                    "Air": air,
                    "Water": water,
                    "Structure": structure,
                },
                "charge_consumer": "storm Power deficit" if day == 5 and storm_report and storm_report["charge_use"] > 0 else None,
                "relay_load_test": copy.deepcopy(relay_load_test_report) if day >= 4 else None,
                "signal_state": {
                    "committed": signal_name,
                    "confidence": config["storm"]["base_confidence"],
                    "expiry_resolved": day >= config["signals"][signal_name]["trader_day"],
                },
                "expedition_state": expedition_report if day == 3 else None,
                "incident_stage": (
                    storm_report
                    if day == 5
                    else (
                        copy.deepcopy(incident_case_report)
                        if incident_case_report and day >= int(options.get("incident_day", 4))
                        else None
                    )
                ),
                "warning_lead": storm_report["warning_lead_stages"] if day == 5 and storm_report else None,
                "recovery_work": incident_work if day == 5 else (project_used if day >= 6 else 0.0),
                "juna_state": copy.deepcopy(juna_report) if day >= 6 else None,
                "session": session,
                "phases": phases,
                "buffer_or_deficit": day_buffer,
                "exact_failure_reason": exact_day_reason,
                "warnings": day_warnings,
                "emergency_actions_available": emergency_actions_available,
                "active_promises": copy.deepcopy(state.promises),
            }
        )

    selected_required = {
        project_id
        for project_id, project in selected_projects.items()
        if project["tier"] in {"mandatory", "route_mandatory"}
    }
    incomplete_required = sorted(selected_required - state.completed_projects)
    force_proof_incomplete = bool(options.get("force_proof_incomplete"))
    for project_id in incomplete_required:
        progress = state.projects[project_id]
        reason = progress.block_reason or f"{progress.remaining_work:.2f} work remains"
        gap = f"required project {project_id} incomplete: {reason}"
        state.proof_gaps.append(gap)
        if "missing component" in reason:
            force_proof_incomplete = True
        else:
            state.recovery_reasons.append(
                f"Recover First preserves survival while {project_id} remains incomplete"
            )
    if state.functional_areas < 8 or state.functional_areas > 10:
        state.proof_gaps.append(
            f"ending functional areas {state.functional_areas} outside required 8..10"
        )
        force_proof_incomplete = True
    for stock_name, stock_data in config["stocks"].items():
        if state.stocks[stock_name] + EPSILON < stock_data["minimum_viable_reserve"]:
            state.failures.append(
                f"{stock_name} ending reserve {state.stocks[stock_name]:.2f} below minimum {stock_data['minimum_viable_reserve']:.2f}"
            )
    if state.deadline_misses:
        for miss in state.deadline_misses:
            if miss not in state.proof_gaps:
                state.proof_gaps.append(miss)
                state.recovery_reasons.append(
                    f"Recover First absorbs missed critical path: {miss}"
                )
    day7_available_for_hope = day_reports[-1]["work"]["daily_uncommitted"]
    state.hope_state = resolve_hope_beat(
        config,
        state.completed_projects,
        available_work=day7_available_for_hope,
        force_minimal=bool(options.get("force_minimal_hope")),
    )
    full_hope_id = config["hope_beats"]["full_project"]
    if state.hope_state["type"] != "full":
        state.proof_gaps.append(f"full authored hope setup {full_hope_id} not completed")
        if state.hope_state["supports_recover_first"]:
            state.recovery_reasons.append(
                f"minimal earned hope beat {state.hope_state['id']} supports Recover First"
            )
        else:
            force_proof_incomplete = True
    if options.get("major_ambition_missed"):
        state.proof_gaps.append("major Day 7 ambition deliberately deferred")
        state.recovery_reasons.append(
            "Recover First chosen instead of an unsafe ambitious direction"
        )
    if consecutive_ration_days >= 3:
        state.recovery_reasons.append(
            "repeated rationing leaves prolonged Hunger requiring recovery"
        )
    if options.get("force_recover_first"):
        state.recovery_reasons.append(str(options["force_recover_first"]))

    survival_before_outcome = not state.failures
    final_storm_profile = storm_report["profile"] if storm_report else "prepared"
    endings = _ending_eligibility(
        state,
        config,
        final_storm_profile,
        survival_before_outcome,
        recovery_needed=bool(state.recovery_reasons),
    )
    if survival_before_outcome and not any(endings.values()):
        state.proof_gaps.append("no ending direction is eligible")
        force_proof_incomplete = True
    save_probe = run_save_probe(state, config, options.get("save_probe"))
    if save_probe and not save_probe["passed"]:
        state.invariant_errors.append(f"save probe {save_probe['probe']} failed")

    prompt3_evidence = build_prompt3_case_evidence(
        state, config, options, day_reports
    )
    outcome = derive_outcome_class(
        config,
        invariant_errors=state.invariant_errors,
        shelter_failures=state.failures,
        proof_gaps=state.proof_gaps,
        recover_first_reasons=state.recovery_reasons,
        ending_eligibility=endings,
        force_proof_incomplete=force_proof_incomplete,
    )

    total_buffer = rounded(total_project_capacity - total_project_used)
    capacity_margin = (
        100.0 * total_buffer / total_project_capacity
        if total_project_capacity > EPSILON
        else 0.0
    )
    resilience = calculate_schedule_resilience(
        state,
        selected_projects,
        day_reports,
        total_project_capacity=total_project_capacity,
        total_project_used=total_project_used,
    )
    for day_report in day_reports:
        day_report["ending_eligibility"] = (
            copy.deepcopy(endings) if day_report["day"] == 7 else {}
        )
        day_report["outcome_status"] = (
            outcome["outcome_class"] if day_report["day"] == 7 else "IN_PROGRESS"
        )
        for phase in day_report["phases"]:
            phase["outcome_status"] = day_report["outcome_status"]
    expected_outcome = scenario.get(
        "expected_outcome_class",
        "FULL_PROOF" if scenario["expected_viable"] else "SHELTER_FAILURE",
    )
    result = {
        "scenario_id": scenario["id"],
        "name": scenario["name"],
        "category": scenario["category"],
        "route": route,
        "signal": signal_name,
        "expected_viable": scenario["expected_viable"],
        "expected_outcome_class": expected_outcome,
        "mandatory": scenario["mandatory"],
        "outcome_class": outcome["outcome_class"],
        "survival_viable": outcome["survival_viable"],
        "slice_proof_complete": outcome["slice_proof_complete"],
        "ending_directions_available": outcome["ending_directions_available"],
        "recover_first_available": outcome["recover_first_available"],
        "invariant_valid": outcome["invariant_valid"],
        "exact_limiting_fact": outcome["exact_limiting_fact"],
        "viable": outcome["viable"],
        "expectation_met": outcome["outcome_class"] == expected_outcome,
        "days": day_reports,
        "final": {
            "stocks": copy.deepcopy(state.stocks),
            "minimum_stocks": copy.deepcopy(state.stock_minima),
            "components": copy.deepcopy(state.components),
            "functional_areas": state.functional_areas,
            "rest_capacity": state.rest_capacity,
            "temporary_rest_capacity": state.temporary_rest_capacity,
            "completed_projects": sorted(state.completed_projects),
            "incomplete_required_projects": incomplete_required,
            "deadline_misses": list(state.deadline_misses),
            "target_misses": list(state.target_misses),
            "ending_eligibility": endings,
            "outcome": outcome,
            "hope_beat": copy.deepcopy(state.hope_state),
            "proof_gaps": list(dict.fromkeys(state.proof_gaps)),
            "recovery_reasons": list(dict.fromkeys(state.recovery_reasons)),
            "invariant_errors": list(dict.fromkeys(state.invariant_errors)),
            "work_capacity_after_overhead": rounded(total_project_capacity),
            "project_work_used": rounded(total_project_used),
            "usable_buffer": total_buffer,
            "usable_buffer_percent": rounded(capacity_margin),
            "essential_and_incident_work": rounded(total_essential),
            "schedule_resilience": resilience,
            "failure_reasons": list(dict.fromkeys(state.failures)),
            "warnings": list(dict.fromkeys(state.warnings)),
            "exact_failure_reason": (
                outcome["exact_limiting_fact"]
                if outcome["outcome_class"]
                in {"SHELTER_FAILURE", "INVARIANT_ERROR", "PROOF_INCOMPLETE"}
                else None
            ),
            "exact_limiting_fact": outcome["exact_limiting_fact"],
        },
        "construction_risk": construction_risk,
        "medical_tutorial": {
            "path": options.get("medical_tutorial_path", "teo_exposure"),
            "teo_examination_available": True,
            "new_injury_required": False,
            "new_injury_occurred": construction_risk["injury"] != "none",
        },
        "highball": highball_report,
        "relay_load_test": relay_load_test_report,
        "trader": trader_report,
        "expedition": expedition_report,
        "storm": storm_report,
        "juna": juna_report,
        "save_probe": save_probe,
        "prompt3_evidence": prompt3_evidence,
        "provisional": True,
        "model_limits": [
            "No exact pathfinding or footstep simulation",
            "No measured player comprehension or enjoyment",
            "No camera comfort, visual readability, or emotional-impact evidence",
            "No final resident AI or relationship simulation",
        ],
    }
    return result


def run_scenarios(
    config: dict[str, Any], scenarios: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    return [simulate_scenario(config, scenario) for scenario in scenarios]


def scenario_by_id(scenarios: list[dict[str, Any]], scenario_id: str) -> dict[str, Any]:
    for scenario in scenarios:
        if scenario["id"] == scenario_id:
            return scenario
    raise KeyError(scenario_id)
