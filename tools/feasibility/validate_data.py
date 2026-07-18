#!/usr/bin/env python3
"""Validate the canonical Signal 45 feasibility inputs."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict, deque
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DEFAULT_MODEL = ROOT / "data" / "model.json"
DEFAULT_SCENARIOS = ROOT / "data" / "scenarios.json"


class DataValidationError(ValueError):
    """Raised when canonical feasibility data is malformed."""


def load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            value = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise DataValidationError(f"{path}: {exc}") from exc
    if not isinstance(value, dict):
        raise DataValidationError(f"{path}: root must be an object")
    return value


def _require_keys(value: dict[str, Any], keys: set[str], context: str) -> None:
    missing = sorted(keys - value.keys())
    if missing:
        raise DataValidationError(f"{context}: missing keys {missing}")


def _validate_project_graph(projects: list[dict[str, Any]]) -> None:
    ids = [project.get("id") for project in projects]
    if len(ids) != len(set(ids)):
        raise DataValidationError("projects: IDs must be unique")
    project_ids = set(ids)
    indegree = {project_id: 0 for project_id in project_ids}
    edges: dict[str, list[str]] = defaultdict(list)
    for project in projects:
        for dependency in project.get("dependencies", []):
            if dependency not in project_ids:
                raise DataValidationError(
                    f"project {project['id']}: unknown dependency {dependency}"
                )
            edges[dependency].append(project["id"])
            indegree[project["id"]] += 1
    queue = deque(project_id for project_id, degree in indegree.items() if degree == 0)
    visited = 0
    while queue:
        current = queue.popleft()
        visited += 1
        for dependent in edges[current]:
            indegree[dependent] -= 1
            if indegree[dependent] == 0:
                queue.append(dependent)
    if visited != len(project_ids):
        raise DataValidationError("projects: dependency graph contains a cycle")


def validate_model(model: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    try:
        _require_keys(
            model,
            {
                "schema_version",
                "metadata",
                "time",
                "teaching_budget",
                "work",
                "residents",
                "stocks",
                "components",
                "utilities",
                "routes",
                "projects",
                "signals",
                "expedition",
                "storm",
                "highball",
                "juna",
                "initial_shelter",
                "ending_requirements",
                "transactions",
            },
            "model",
        )
        if model["schema_version"] != 1:
            raise DataValidationError("model: unsupported schema_version")
        if model["metadata"].get("title") != "Signal 45":
            raise DataValidationError("model: title must be Signal 45")
        if model["metadata"].get("provisional") is not True:
            raise DataValidationError("model: all Prompt 2 balance must be provisional")

        expected_stocks = {"Food", "Clean Water", "Medicine", "Materials", "Charge"}
        if set(model["stocks"]) != expected_stocks:
            raise DataValidationError("stocks: must contain exactly the five locked stocks")
        expected_utilities = {"power", "air", "water", "structure"}
        if set(model["utilities"]) != expected_utilities:
            raise DataValidationError("utilities: must contain exactly Power, Air, Water, Structure")
        expected_residents = {"Ash", "Imka", "Teo", "Maren", "Juna Malek"}
        if set(model["residents"]) != expected_residents:
            raise DataValidationError("residents: locked cast is incomplete or changed")
        expected_routes = {"east", "west"}
        if set(model["routes"]) != expected_routes:
            raise DataValidationError("routes: must contain East and West only")

        for stock_name, stock in model["stocks"].items():
            _require_keys(
                stock,
                {"start", "capacity", "minimum_viable_reserve", "comfortable_reserve", "warning_threshold"},
                f"stock {stock_name}",
            )
            if not 0 <= stock["start"] <= stock["capacity"]:
                raise DataValidationError(f"stock {stock_name}: start must fit capacity")
            if stock["minimum_viable_reserve"] > stock["comfortable_reserve"]:
                raise DataValidationError(f"stock {stock_name}: reserve thresholds reversed")

        work = model["work"]
        if work["minimum_emergency_capacity"] <= 0:
            raise DataValidationError("work: minimum emergency capacity must be positive")
        if work["minimum_emergency_capacity"] >= work["base_capacity_per_resident_day"]:
            raise DataValidationError("work: emergency capacity must remain below base capacity")
        for class_name, project_class in work["project_classes"].items():
            if project_class["max_workers"] != len(project_class["worker_efficiency"]):
                raise DataValidationError(f"project class {class_name}: worker efficiency length mismatch")
            if any(value <= 0 for value in project_class["worker_efficiency"]):
                raise DataValidationError(f"project class {class_name}: worker efficiencies must be positive")

        projects = model["projects"]
        if not isinstance(projects, list) or not projects:
            raise DataValidationError("projects: must be a nonempty array")
        _validate_project_graph(projects)
        component_ids = set(model["components"])
        project_classes = set(work["project_classes"])
        for project in projects:
            _require_keys(
                project,
                {
                    "id",
                    "route",
                    "tier",
                    "class",
                    "available_day",
                    "deadline_day",
                    "work",
                    "materials",
                    "components",
                    "role",
                    "dependencies",
                    "benefits",
                    "highball_eligible",
                    "save_checkpoints",
                },
                f"project {project.get('id', '<unknown>')}",
            )
            if project["route"] not in {"all", "east", "west"}:
                raise DataValidationError(f"project {project['id']}: invalid route")
            if project["class"] not in project_classes:
                raise DataValidationError(f"project {project['id']}: invalid class")
            low, high = work["project_classes"][project["class"]]["work_range"]
            if not low <= project["work"] <= high:
                raise DataValidationError(
                    f"project {project['id']}: work {project['work']} outside class range {low}..{high}"
                )
            if project["available_day"] > project["deadline_day"]:
                raise DataValidationError(f"project {project['id']}: available after deadline")
            hard_deadline = project.get("hard_deadline_day", project["deadline_day"])
            if hard_deadline < project["deadline_day"] or hard_deadline > 7:
                raise DataValidationError(
                    f"project {project['id']}: hard deadline must be between target and Day 7"
                )
            unknown_components = set(project["components"]) - component_ids
            if unknown_components:
                raise DataValidationError(
                    f"project {project['id']}: unknown components {sorted(unknown_components)}"
                )
            if project["max_workers"] > work["project_classes"][project["class"]]["max_workers"]:
                raise DataValidationError(f"project {project['id']}: exceeds class worker limit")

        storm = model["storm"]
        if storm["maximum_affected_systems"] > 3:
            raise DataValidationError("storm: cascade may affect no more than three systems")
        if len(storm["cascade_order"]) > storm["maximum_affected_systems"]:
            raise DataValidationError("storm: cascade_order exceeds bound")
        if len(set(storm["cascade_order"])) != len(storm["cascade_order"]):
            raise DataValidationError("storm: cascade systems must be unique")
        for profile_name, profile in storm["profiles"].items():
            if profile["affected_systems"] > storm["maximum_affected_systems"]:
                raise DataValidationError(f"storm profile {profile_name}: exceeds cascade bound")

        candidates = model["highball"]["candidate_benefits"]
        if model["highball"]["baseline_candidate"] not in candidates:
            raise DataValidationError("highball: baseline candidate must be sensitivity-tested")
        if sorted(candidates) != candidates or any(not 0 < value < 1 for value in candidates):
            raise DataValidationError("highball: candidates must be ascending fractions")

        if model["expedition"].get("exclusive_rewards") is not False:
            raise DataValidationError("expedition: mode-exclusive rewards are prohibited")
        if model["initial_shelter"].get("functional_areas") != 4:
            raise DataValidationError("initial shelter: functional areas must remain four")
        if len(model["initial_shelter"].get("room_families", [])) != 7:
            raise DataValidationError("initial shelter: slice must retain seven room families")

        teaching = model["teaching_budget"]
        if set(teaching) != {"practiced", "demonstrated", "teased", "withheld"}:
            raise DataValidationError("teaching budget: all four classifications are required")
        if len(teaching["practiced"]) > 6 or len(teaching["demonstrated"]) > 4:
            raise DataValidationError("teaching budget: opening practice/demonstration is overloaded")

        transaction_ids = [item["id"] for item in model["transactions"]]
        if len(transaction_ids) != len(set(transaction_ids)):
            raise DataValidationError("transactions: IDs must be unique")
        for transaction in model["transactions"]:
            _require_keys(
                transaction,
                {
                    "id",
                    "save_before",
                    "commit_after",
                    "reversible",
                    "resume",
                    "idempotency",
                    "mid_animation",
                },
                f"transaction {transaction.get('id', '<unknown>')}",
            )
            if not transaction["idempotency"]:
                raise DataValidationError(
                    f"transaction {transaction['id']}: idempotency rule is required"
                )
        required_transactions = {
            "project_activation",
            "material_reservation",
            "partial_construction",
            "project_completion",
            "project_cancellation",
            "highball_confirmation",
            "signal_commitment",
            "expedition_irreversible_action",
            "trader_transaction",
            "juna_admission",
            "incident_escalation",
            "treatment_start",
            "phase_transition",
            "end_of_day_ledger",
        }
        if not required_transactions.issubset(transaction_ids):
            raise DataValidationError("transactions: required serialization boundaries missing")
    except (DataValidationError, KeyError, TypeError, ValueError) as exc:
        errors.append(str(exc))
    return errors


def validate_scenarios(scenario_data: dict[str, Any], model: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    try:
        _require_keys(scenario_data, {"schema_version", "scenarios"}, "scenarios")
        if scenario_data["schema_version"] != 1:
            raise DataValidationError("scenarios: unsupported schema_version")
        scenarios = scenario_data["scenarios"]
        if not isinstance(scenarios, list) or len(scenarios) < 64:
            raise DataValidationError("scenarios: at least 64 deterministic scenarios are required")
        ids = [scenario.get("id") for scenario in scenarios]
        if len(ids) != len(set(ids)):
            raise DataValidationError("scenarios: IDs must be unique")
        required_ids = {f"S{number:02d}" for number in range(1, 65)}
        missing_required = required_ids - set(ids)
        if missing_required:
            raise DataValidationError(
                f"scenarios: missing required IDs {sorted(missing_required)}"
            )
        input_signatures: dict[str, str] = {}
        for scenario in scenarios:
            _require_keys(
                scenario,
                {"id", "name", "category", "route", "signal", "expected_viable", "mandatory", "options"},
                f"scenario {scenario.get('id', '<unknown>')}",
            )
            if scenario["route"] not in model["routes"]:
                raise DataValidationError(f"scenario {scenario['id']}: invalid route")
            if scenario["signal"] not in model["signals"]:
                raise DataValidationError(f"scenario {scenario['id']}: invalid signal")
            if not isinstance(scenario["expected_viable"], bool) or not isinstance(scenario["mandatory"], bool):
                raise DataValidationError(f"scenario {scenario['id']}: expected/mandatory must be boolean")
            if scenario["id"] in required_ids and not scenario["mandatory"]:
                raise DataValidationError(
                    f"scenario {scenario['id']}: required scenario must be mandatory"
                )
            signature = json.dumps(
                {"route": scenario["route"], "signal": scenario["signal"], "options": scenario["options"]},
                sort_keys=True,
            )
            if signature in input_signatures:
                raise DataValidationError(
                    f"scenario {scenario['id']}: exact input duplicate of {input_signatures[signature]}"
                )
            input_signatures[signature] = scenario["id"]
        required_categories = {
            "base_routes",
            "signal_variation",
            "imperfect_play",
            "resident_availability",
            "storm",
            "injury_treatment",
            "nightrun",
            "juna",
            "save_reload",
            "sensitivity",
        }
        categories = {scenario["category"] for scenario in scenarios}
        if not required_categories.issubset(categories):
            raise DataValidationError(
                f"scenarios: missing categories {sorted(required_categories - categories)}"
            )
    except (DataValidationError, KeyError, TypeError, ValueError) as exc:
        errors.append(str(exc))
    return errors


def validate_all(model_path: Path = DEFAULT_MODEL, scenarios_path: Path = DEFAULT_SCENARIOS) -> tuple[dict[str, Any], dict[str, Any]]:
    model = load_json(model_path)
    scenarios = load_json(scenarios_path)
    errors = validate_model(model) + validate_scenarios(scenarios, model)
    if errors:
        raise DataValidationError("\n".join(errors))
    return model, scenarios


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--scenarios", type=Path, default=DEFAULT_SCENARIOS)
    args = parser.parse_args(argv)
    try:
        model, scenarios = validate_all(args.model, args.scenarios)
    except DataValidationError as exc:
        print(f"INVALID\n{exc}", file=sys.stderr)
        return 1
    print(
        f"VALID model_schema={model['schema_version']} "
        f"projects={len(model['projects'])} scenarios={len(scenarios['scenarios'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
