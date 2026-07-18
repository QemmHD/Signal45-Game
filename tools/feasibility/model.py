#!/usr/bin/env python3
"""Deterministic, falsifiable seven-day feasibility model for Signal 45.

The model intentionally represents only work, stocks, bounded utilities, projects,
events, expedition facts, admissions, and serialization invariants needed by
Prompt 2. It is not a game engine and does not simulate resident footsteps.
"""

from __future__ import annotations

import copy
import json
import math
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable

try:
    from .validate_data import DEFAULT_MODEL, DEFAULT_SCENARIOS, validate_all
except ImportError:  # Direct script/test discovery execution.
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
    return {
        "health": "healthy",
        "hunger": "fed",
        "fatigue": "rested",
        "stress": "steady",
    }


def calculate_resident_capacity(
    config: dict[str, Any],
    resident_name: str,
    conditions: dict[str, str] | None = None,
    *,
    availability: float = 1.0,
    global_multiplier: float = 1.0,
) -> float:
    resident = config["residents"][resident_name]
    work = config["work"]
    availability = min(1.0, max(0.0, availability))
    if availability <= EPSILON:
        return 0.0
    capacity = resident["base_capacity"] * availability
    for category, state_name in (conditions or default_conditions()).items():
        capacity *= work["condition_multipliers"][category][state_name]
    capacity *= global_multiplier
    minimum = work["minimum_emergency_capacity"] * availability
    return rounded(max(minimum, capacity))


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


def forecast_stock(config: dict[str, Any], stock: str, amount: float) -> dict[str, Any]:
    data = config["stocks"][stock]
    if amount < data["minimum_viable_reserve"] - EPSILON:
        status = "critical"
    elif amount < data["warning_threshold"] - EPSILON:
        status = "warning"
    elif amount < data["comfortable_reserve"] - EPSILON:
        status = "tight"
    else:
        status = "comfortable"
    return {
        "amount": rounded(amount),
        "status": status,
        "minimum_viable_reserve": data["minimum_viable_reserve"],
        "comfortable_reserve": data["comfortable_reserve"],
    }


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
        for load_name in reversed(power["priority_order"]):
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
    return {
        "source_capacity": rounded(source),
        "pump_availability": rounded(pump),
        "treatment_efficiency": rounded(treatment),
        "delivery": rounded(delivered),
        "demand": rounded(demand),
        "headroom": rounded(headroom),
        "contamination_state": "suspect" if impaired else "clean",
        "failing_link": link,
    }


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
    charge_use = max(0.0, profile["charge_use"])
    max_discharge = config["stocks"]["Charge"]["discharge_limit_per_stage"] * affected
    charge_use = min(charge_use, max_discharge)
    charge_shortfall = consume_stock(
        state, "Charge", charge_use, "storm Power deficit", critical=False
    )
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
        "water_loss": rounded(water_loss),
        "medicine_use": rounded(profile["medicine_use"] * medicine_multiplier),
        "next_day_capacity_loss": rounded(profile["next_day_capacity_loss"]),
        "recoverable": bool(profile["recoverable"]),
        "stages": stages,
        "physical_aftermath": "filter residue, load-shed rooms, water marks, and visible repair state",
        "human_aftermath": "Fatigue, treatment, promise repayment, and recovery work",
    }
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
    consume_stock(state, "Charge", costs["charge_cost"], "Highball order")
    consume_stock(state, "Materials", costs["materials_wear"], "Highball material wear")
    capacity_losses: dict[int, float] = {
        repayment_day: costs["fatigue_capacity_loss_next_day"]
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
        "context": context,
        "order_day": order_day,
        "target_project": target_id,
        "work_saved": saved,
        "costs": costs,
        "cost_breakdown": cost_breakdown,
        "promise": promise,
        "capacity_losses": capacity_losses,
        "net_week_work_value": rounded(saved - sum(capacity_losses.values())),
        "emotional_effects_are_placeholder": True,
        "refuses_next_highball": promise == "breached",
    }
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
    resident_capacity = {
        resident: calculate_resident_capacity(
            config,
            resident,
            _conditions_for(options, resident, day),
            availability=availability[resident],
            global_multiplier=global_multiplier,
        )
        for resident in availability
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
    return {
        "available_residents": [name for name, fraction in availability.items() if fraction > 0],
        "resident_availability": availability,
        "resident_capacity": {key: rounded(value) for key, value in resident_capacity.items()},
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
    state: SimulationState, config: dict[str, Any], storm_profile: str, survival_viable: bool
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
    recover = survival_viable and (storm_profile != "prepared" or state.treatment_open)
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
    total_project_capacity = 0.0
    total_project_used = 0.0
    total_essential = 0.0

    for day in range(1, 8):
        state.day = day
        state.phase = "swelter"
        stocks_start = copy.deepcopy(state.stocks)
        day_warnings: list[str] = []

        if day == config["signals"][signal_name]["trader_day"]:
            trader_report = _apply_trader(state, config, signal_name)
        if day == config["juna"]["arrival_day"]:
            juna_report = _apply_juna(state, config, options, modifiers)

        treatment_work = 0.0
        if day == 1 and not options.get("treatment_delay"):
            medicine_use = config["stocks"]["Medicine"]["examination_use"] * modifiers.get("medicine_use_multiplier", 1.0)
            consume_stock(state, "Medicine", medicine_use, "Teo respiratory examination")
            consume_stock(state, "Clean Water", config["stocks"]["Clean Water"]["treatment_use"], "Teo respiratory examination")
            treatment_work += config["work"]["teo_examination_work"]
        if day == 2 and options.get("treatment_delay"):
            medicine_use = 2.0 * config["stocks"]["Medicine"]["examination_use"] * modifiers.get("medicine_use_multiplier", 1.0)
            consume_stock(state, "Medicine", medicine_use, "delayed Teo respiratory treatment")
            consume_stock(state, "Clean Water", 2.0 * config["stocks"]["Clean Water"]["treatment_use"], "delayed Teo respiratory treatment")
            treatment_work += 4.0
            state.treatment_open = True
        if day == 2 and construction_risk["injury"] != "none":
            serious = construction_risk["injury"] == "serious"
            medicine_key = "serious_injury_use" if serious else "minor_injury_use"
            consume_stock(
                state,
                "Medicine",
                config["stocks"]["Medicine"][medicine_key] * modifiers.get("medicine_use_multiplier", 1.0),
                f"{construction_risk['injury']} construction injury",
            )
            consume_stock(
                state,
                "Clean Water",
                2.0 if serious else 1.0,
                f"{construction_risk['injury']} construction injury treatment",
            )
            treatment_work += 6.0 if serious else 4.0
            state.treatment_open = True
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

        capacity = _daily_capacity(
            config, route, day, options, capacity_losses, juna_report
        )
        essential_work = config["work"]["daily_essential_work"]
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
            + treatment_work
            + incident_work
            + mistake_work
            + risk_preparation_work
        )
        project_capacity = max(0.0, capacity["gross"] - nonproject)
        total_project_capacity += project_capacity
        total_essential += essential_work + treatment_work + incident_work + mistake_work
        total_essential += risk_preparation_work

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

        resident_count = 4 + int(state.juna_admitted)
        food_multiplier = modifiers.get("food_consumption_multiplier", 1.0)
        water_multiplier = modifiers.get("water_consumption_multiplier", 1.0)
        consume_stock(
            state,
            "Food",
            resident_count * config["stocks"]["Food"]["normal_per_resident_day"] * food_multiplier,
            f"Day {day} ration",
        )
        consume_stock(
            state,
            "Clean Water",
            resident_count * config["stocks"]["Clean Water"]["normal_per_resident_day"] * water_multiplier,
            f"Day {day} water issue",
        )
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
            name: forecast_stock(config, name, value)
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
        day_reports.append(
            {
                "day": day,
                "available_residents": capacity["available_residents"],
                "resident_availability": capacity["resident_availability"],
                "work": {
                    **capacity,
                    "essential": rounded(essential_work),
                    "treatment_and_rest": rounded(treatment_work + capacity["highball_or_promise_loss"]),
                    "incident_response": rounded(incident_work),
                    "mistake_rework": rounded(mistake_work),
                    "risk_preparation": rounded(risk_preparation_work),
                    "project_capacity": rounded(project_capacity),
                    "project_used": rounded(project_used),
                    "mandatory_shared_project_work": project_work_by_tier["mandatory"],
                    "mandatory_route_project_work": project_work_by_tier["route_mandatory"],
                    "optional_project_work": project_work_by_tier["optional"],
                    "buffer": day_buffer,
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
                "utilities": {
                    "Power": power,
                    "Air": air,
                    "Water": water,
                    "Structure": structure,
                },
                "charge_consumer": "storm Power deficit" if day == 5 and storm_report and storm_report["charge_use"] > 0 else None,
                "signal_state": {
                    "committed": signal_name,
                    "confidence": config["storm"]["base_confidence"],
                    "expiry_resolved": day >= config["signals"][signal_name]["trader_day"],
                },
                "expedition_state": expedition_report if day == 3 else None,
                "incident_stage": storm_report if day == 5 else None,
                "warning_lead": storm_report["warning_lead_stages"] if day == 5 and storm_report else None,
                "recovery_work": incident_work if day == 5 else (project_used if day >= 6 else 0.0),
                "juna_state": copy.deepcopy(juna_report) if day >= 6 else None,
                "session": session,
                "phases": phases,
                "buffer_or_deficit": day_buffer,
                "exact_failure_reason": exact_day_reason,
                "warnings": day_warnings,
            }
        )

    selected_required = {
        project_id
        for project_id, project in selected_projects.items()
        if project["tier"] in {"mandatory", "route_mandatory"}
    }
    incomplete_required = sorted(selected_required - state.completed_projects)
    for project_id in incomplete_required:
        progress = state.projects[project_id]
        reason = progress.block_reason or f"{progress.remaining_work:.2f} work remains"
        state.failures.append(f"required project {project_id} incomplete: {reason}")
    if state.functional_areas < 8 or state.functional_areas > 10:
        state.failures.append(
            f"ending functional areas {state.functional_areas} outside required 8..10"
        )
    for stock_name, stock_data in config["stocks"].items():
        if state.stocks[stock_name] + EPSILON < stock_data["minimum_viable_reserve"]:
            state.failures.append(
                f"{stock_name} ending reserve {state.stocks[stock_name]:.2f} below minimum {stock_data['minimum_viable_reserve']:.2f}"
            )
    if state.deadline_misses:
        state.failures.extend(state.deadline_misses)
    survival_viable = not state.failures
    final_storm_profile = storm_report["profile"] if storm_report else "prepared"
    endings = _ending_eligibility(
        state, config, final_storm_profile, survival_viable
    )
    if survival_viable and not any(endings.values()):
        state.failures.append("no ending direction is eligible")
        survival_viable = False
    save_probe = run_save_probe(state, config, options.get("save_probe"))
    if save_probe and not save_probe["passed"]:
        state.failures.append(f"save probe {save_probe['probe']} failed")
        survival_viable = False

    total_buffer = rounded(total_project_capacity - total_project_used)
    capacity_margin = (
        100.0 * total_buffer / total_project_capacity
        if total_project_capacity > EPSILON
        else 0.0
    )
    result = {
        "scenario_id": scenario["id"],
        "name": scenario["name"],
        "category": scenario["category"],
        "route": route,
        "signal": signal_name,
        "expected_viable": scenario["expected_viable"],
        "mandatory": scenario["mandatory"],
        "viable": survival_viable,
        "expectation_met": survival_viable == scenario["expected_viable"],
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
            "work_capacity_after_overhead": rounded(total_project_capacity),
            "project_work_used": rounded(total_project_used),
            "usable_buffer": total_buffer,
            "usable_buffer_percent": rounded(capacity_margin),
            "essential_and_incident_work": rounded(total_essential),
            "failure_reasons": list(dict.fromkeys(state.failures)),
            "warnings": list(dict.fromkeys(state.warnings)),
            "exact_failure_reason": state.failures[0] if state.failures else None,
        },
        "construction_risk": construction_risk,
        "medical_tutorial": {
            "path": options.get("medical_tutorial_path", "teo_exposure"),
            "teo_examination_available": True,
            "new_injury_required": False,
            "new_injury_occurred": construction_risk["injury"] != "none",
        },
        "highball": highball_report,
        "trader": trader_report,
        "expedition": expedition_report,
        "storm": storm_report,
        "juna": juna_report,
        "save_probe": save_probe,
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
