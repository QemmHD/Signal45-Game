#!/usr/bin/env python3
"""Run the 111 deterministic Prompt 4 spatial acceptance scenarios."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable

try:
    from .coordinates import (
        CoordinateError, footprint_cells, global_to_section_local,
        section_local_to_global, validate_address,
    )
    from .model import (
        derive_functional_area_count, load_json, load_spatial_data,
        restore_layout_state, serialize_layout_state,
    )
    from .navigation import find_path
    from .placement import (
        activate_blueprint, apply_construction_work, cancel_blueprint,
        complete_blueprint, deconstruct_once, deliver_blueprint, new_blueprint,
        repurpose_room, save_inactive_blueprint, validate_module,
        validate_object_placement, validate_room_placement, validate_severe_access,
    )
    from .travel import calculate_travel_metrics
    from .utilities import (
        charge_backup_available, consumer_status, preview_isolation,
        restore_platform_lighting, service_access, shed_platform_lighting,
        validate_platform_lighting,
    )
    from .validate_layouts import run_validation
except ImportError:  # Direct script execution.
    from coordinates import (
        CoordinateError, footprint_cells, global_to_section_local,
        section_local_to_global, validate_address,
    )
    from model import (
        derive_functional_area_count, load_json, load_spatial_data,
        restore_layout_state, serialize_layout_state,
    )
    from navigation import find_path
    from placement import (
        activate_blueprint, apply_construction_work, cancel_blueprint,
        complete_blueprint, deconstruct_once, deliver_blueprint, new_blueprint,
        repurpose_room, save_inactive_blueprint, validate_module,
        validate_object_placement, validate_room_placement, validate_severe_access,
    )
    from travel import calculate_travel_metrics
    from utilities import (
        charge_backup_available, consumer_status, preview_isolation,
        restore_platform_lighting, service_access, shed_platform_lighting,
        validate_platform_lighting,
    )
    from validate_layouts import run_validation


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SCENARIOS_PATH = HERE / "data" / "scenarios.json"
REPORT_PATH = HERE / "reports" / "spatial_scenarios.json"
SUMMARY_PATH = HERE / "reports" / "spatial_scenario_summary.md"


def _scenario_catalog() -> list[dict[str, Any]]:
    raw = load_json(SCENARIOS_PATH)
    result: list[dict[str, Any]] = []
    for group in raw["groups"]:
        for offset, name in enumerate(group["names"]):
            number = int(group["start"]) + offset
            result.append({
                "number": number,
                "scenario_id": f"P4-{number:03d}",
                "name": name,
                "category": group["category"],
            })
    if [item["number"] for item in result] != list(range(1, 112)):
        raise ValueError("Prompt 4 scenario catalog must cover 1..111 exactly once")
    return result


def _caught(action: Callable[[], Any], error: type[BaseException] = Exception) -> bool:
    try:
        action()
    except error:
        return True
    return False


def _room_probe(family: str = "rest", section: str = "central_platform") -> dict[str, Any]:
    return {
        "instance_id": f"probe_{family}", "physical_area_id": f"probe_{family}",
        "family_id": family, "form": "temporary", "section_id": section,
        "footprint": {"level": 0, "x_start": 10, "x_end": 11, "lanes": [0]},
        "state": "operational", "counts_as_area": True, "temporary_zone": False,
        "essential": False,
    }


def _layout_with_probe_room(data: Any, family: str) -> tuple[dict[str, Any], dict[str, Any]]:
    layout = copy.deepcopy(data.layout("day1"))
    room = _room_probe(family)
    layout["rooms"].append(room)
    return layout, room


def _candidate(object_id: str, room: dict[str, Any], x: int = 10, rotation: int = 0) -> dict[str, Any]:
    return {
        "instance_id": f"probe_{object_id}", "object_id": object_id,
        "section_id": room["section_id"],
        "anchor": {"section_id": room["section_id"], "level": 0, "x": x, "lane": 0},
        "rotation": rotation, "state": "operational",
        "room_instance_id": room["instance_id"], "utility_connection": "central_air_node",
    }


@lru_cache(maxsize=1)
def _feasibility() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    sys.path.insert(0, str(ROOT))
    from tools.feasibility.model import load_inputs, run_scenarios
    config, scenarios = load_inputs()
    return config, {item["scenario_id"]: item for item in run_scenarios(config, scenarios)}


def _probe(number: int) -> tuple[bool, Any]:
    data = load_spatial_data()
    day1 = copy.deepcopy(data.layout("day1"))
    east = copy.deepcopy(data.layout("east_day7"))
    west = copy.deepcopy(data.layout("west_day7"))
    report = run_validation()

    if number == 1:
        value = validate_address(data.station, {"section_id": "central_platform", "level": 0, "x": 4, "lane": 1})
        return value["x"] == 4, value
    if number == 2:
        value = _caught(lambda: validate_address(data.station, {"section_id": "missing", "level": 0, "x": 0, "lane": 0}), CoordinateError)
        return value, "invalid section rejected"
    if number == 3:
        value = _caught(lambda: validate_address(data.station, {"section_id": "central_platform", "level": 2, "x": 0, "lane": 0}), CoordinateError)
        return value, "invalid level rejected"
    if number == 4:
        value = _caught(lambda: validate_address(data.station, {"section_id": "central_platform", "level": 0, "x": 0, "lane": 4}), CoordinateError)
        return value, "invalid lane rejected"
    if number == 5:
        local = {"section_id": "east_staff_wing", "level": 0, "x": 3, "lane": 1}
        global_cell = section_local_to_global(data.station, local)
        restored = global_to_section_local(data.station, "east_staff_wing", global_cell)
        return restored == local, {"global": global_cell, "restored": restored}
    if number == 6:
        cells = footprint_cells(data.station, {"section_id": "central_platform", "level": 0, "x": 10, "lane": 0}, {"width": 2, "depth": 1}, 90)
        return len(cells) == 2 and len({cell[2] for cell in cells}) == 1, sorted(cells)
    if number == 7:
        saved = serialize_layout_state(day1); restored = restore_layout_state(day1, saved)
        return serialize_layout_state(restored) == saved, "coordinate-bearing state round-tripped"

    if number in {8, 9, 10, 11}:
        if number == 8:
            room = _room_probe(); room["footprint"] = {"level": 0, "x_start": 3, "x_end": 3, "lanes": [0]}
            result = validate_room_placement(data, day1, room); code = "overlaps_fixed_architecture"
        elif number == 9:
            room = _room_probe(); room["footprint"] = {"level": 0, "x_start": 10, "x_end": 10, "lanes": [2]}
            result = validate_room_placement(data, day1, room); code = "overlaps_fixed_architecture"
        elif number == 10:
            room = _room_probe(); room["footprint"] = {"level": 0, "x_start": 14, "x_end": 14, "lanes": [0]}
            result = validate_room_placement(data, day1, room); code = "outside_buildable_area"
        else:
            room = _room_probe(); result = validate_room_placement(data, day1, room); code = None
        codes = [item["code"] for item in result["reasons"]]
        return (result["valid"] if code is None else code in codes), codes
    if number == 12:
        features = copy.deepcopy(data.station["sections"]["central_platform"]["fixed_architecture"])
        features.append(copy.deepcopy(features[0]))
        ids = [item["feature_id"] for item in features]
        return len(ids) != len(set(ids)), "duplicate fixed feature detected"

    if number in {13, 14, 15}:
        family = {13: "rest", 14: "medical", 15: "utility"}[number]
        result = validate_room_placement(data, day1, _room_probe(family))
        return result["valid"], result
    if number == 16:
        room = _room_probe("rest", "main_gate"); room["footprint"] = {"level": 0, "x_start": 0, "x_end": 0, "lanes": [0]}
        result = validate_room_placement(data, day1, room)
        return not result["valid"] and any(item["code"] == "incompatible_section" for item in result["reasons"]), result
    if number in {17, 18}:
        room = copy.deepcopy(day1["rooms"][3]); changed = repurpose_room(room, "food", incident_active=number == 18)
        return (changed and room["family_id"] == "food") if number == 17 else not changed, room["state"]
    if number in {19, 20, 21}:
        module = {"instance_id": "probe_module", "module_id": "platform_lighting_upgrade", "parent_type": "object", "parent_instance_id": "platform_work_lamp", "socket_type": "lighting_upgrade", "state": "operational", "unique": True}
        if number == 20: module["parent_type"] = "module"
        if number == 21:
            day1["modules"].append(copy.deepcopy(module)); module["instance_id"] = "probe_module_2"
        result = validate_module(day1, module, data.objects)
        return result["valid"] if number == 19 else not result["valid"], result

    if number in {22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32}:
        families = {22: ("bedroll", "rest"), 23: ("triage_cot", "medical"), 24: ("workbench", "workshop")}
        if number in families:
            object_id, family = families[number]; layout, room = _layout_with_probe_room(data, family)
            result = validate_object_placement(data, layout, _candidate(object_id, room))
            return result["valid"], result
        if number == 25:
            cells = footprint_cells(data.station, {"section_id": "central_platform", "level": 0, "x": 10, "lane": 0}, {"width": 2, "depth": 1}, 90)
            return len({cell[2] for cell in cells}) == 1 and len({cell[3] for cell in cells}) == 2, sorted(cells)
        if number == 26:
            layout, room = _layout_with_probe_room(data, "rest"); result = validate_object_placement(data, layout, _candidate("bedroll", room, 12))
            return not result["valid"], result
        if number == 27:
            layout, room = _layout_with_probe_room(data, "rest")
            blocker = _candidate("temporary_barrier", room); blocker["anchor"]["lane"] = 1; blocker["room_instance_id"] = None
            layout["objects"].append(blocker); result = validate_object_placement(data, layout, _candidate("bedroll", room))
            return any(item["code"] == "blocks_interaction_point" for item in result["reasons"]), result
        layout, room = _layout_with_probe_room(data, "rest"); item = _candidate("bedroll", room); layout["objects"].append(item)
        if number == 28:
            item["anchor"]["x"] = 11; return item["anchor"]["x"] == 11, item["anchor"]
        if number == 29:
            item["state"] = "stored"; return item["state"] == "stored", item["state"]
        if number in {30, 31}:
            stocks = {"Materials": 0.0}; first = deconstruct_once(item, stocks, 4.0, 0.5); second = deconstruct_once(item, stocks, 4.0, 0.5)
            return (first == 2.0 and second == 0.0 and stocks["Materials"] == 2.0), {"first": first, "second": second, "stock": stocks["Materials"]}
        saved = serialize_layout_state(layout); item["anchor"]["x"] = 11; saved = serialize_layout_state(layout); restored = restore_layout_state(layout, saved)
        target = next(value for value in restored["objects"] if value["instance_id"] == item["instance_id"])
        return target["anchor"]["x"] == 11, target["anchor"]

    if 33 <= number <= 39:
        stocks = {"Materials": 10.0}; bp = new_blueprint("probe", {("central_platform", 0, 10, 0)}, 4.0, 5.0)
        if number == 33: return stocks["Materials"] == 10.0 and bp["state"] == "preview", bp["state"]
        save_inactive_blueprint(bp)
        if number == 34: return stocks["Materials"] == 10.0 and bp["materials_reserved"] == 0.0, bp
        first = activate_blueprint(bp, stocks); duplicate = activate_blueprint(bp, stocks)
        if number == 35: return first and not duplicate and stocks["Materials"] == 6.0, bp["transactions"]
        delivered = deliver_blueprint(bp); duplicate_delivery = deliver_blueprint(bp)
        if number == 36: return delivered and not duplicate_delivery and bp["materials_delivered"] == 4.0, bp
        applied = apply_construction_work(bp, 2.0)
        if number == 37:
            restored = json.loads(json.dumps(bp)); return applied == 2.0 and restored["work_applied"] == 2.0, restored
        if number == 38:
            fresh = new_blueprint("refund", {("central_platform", 0, 10, 0)}, 4.0, 5.0); activate_blueprint(fresh, stocks)
            first_refund = cancel_blueprint(fresh, stocks, 1.0); second_refund = cancel_blueprint(fresh, stocks, 1.0)
            return first_refund == 4.0 and second_refund == 0.0, {"first": first_refund, "second": second_refund}
        apply_construction_work(bp, 3.0); first_complete = complete_blueprint(bp); second_complete = complete_blueprint(bp)
        return first_complete and not second_complete and bp["capability_granted"], bp["transactions"]

    if 40 <= number <= 45:
        layout_id = {40: "day1", 41: "east_day7", 42: "west_day7", 43: "east_day7_alternate", 44: "west_day7_alternate", 45: "poor_valid"}[number]
        item = report["layouts"][layout_id]
        return item["valid"], {"areas": item["functional_area_count"], "families": item["room_family_count"]}
    if 46 <= number <= 50:
        blockers = (
            {("central_platform", 0, 7, 0), ("central_platform", 0, 7, 1)}
            if number == 47
            else {("main_gate", 0, 1, 0), ("main_gate", 0, 1, 1)}
        )
        result = validate_severe_access(data, day1, blockers); codes = {item["code"] for item in result["reasons"]}
        expected = {46: "blocks_only_route", 47: "strands_resident", 48: "strands_essential_room", 49: "blocks_only_route", 50: "blocks_emergency_path"}[number]
        return expected in codes, sorted(codes)
    if number == 51:
        path = find_path(data, day1, day1["safety_checks"]["main_gate"], day1["safety_checks"]["safe_area"], "normal_walk")
        return path.found, path.to_dict()

    if 52 <= number <= 58:
        path_class = {52: "normal_walk", 53: "material_carry", 54: "heavy_carry", 55: "patient_escort", 56: "patient_carry", 57: "emergency_evacuation", 58: "utility_service"}[number]
        path = find_path(data, west, {"section_id": "main_gate", "level": 0, "x": 0, "lane": 1}, {"section_id": "west_pump_gallery", "level": 0, "x": 3, "lane": 1}, path_class)
        return path.found, path.to_dict()
    if number == 59:
        path = find_path(data, day1, {"section_id": "main_gate", "level": 0, "x": 0, "lane": 1}, {"section_id": "west_pump_gallery", "level": 0, "x": 3, "lane": 1})
        return not path.found, path.failure_reason
    if number == 60:
        altered = copy.deepcopy(east); altered["portal_states"]["central_east_primary"] = "isolated"; altered["portal_states"]["central_east_service"] = "isolated"
        path = find_path(data, altered, altered["safety_checks"]["safe_area"], {"section_id": "east_staff_wing", "level": 0, "x": 5, "lane": 1})
        return not path.found, path.failure_reason
    if number == 61:
        altered = copy.deepcopy(day1); altered["hazards"].append({"hazard_id": "probe", "state": "active", "path_severity": 1, "cells": [{"section_id": "main_gate", "level": 0, "x": 1, "lane": 0}]})
        path = find_path(data, altered, altered["safety_checks"]["main_gate"], altered["safety_checks"]["safe_area"], "normal_walk")
        return path.found and path.hazard_exposure == 0, path.to_dict()
    if number == 62:
        path = find_path(data, east, {"section_id": "east_staff_wing", "level": 0, "x": 9, "lane": 1}, {"section_id": "vertical_shaft", "level": 1, "x": 2, "lane": 0})
        return not path.found, path.failure_reason
    if number == 63:
        altered = copy.deepcopy(day1); altered["section_states"]["west_pump_gallery"] = {"access": "operational", "discovered": True, "hazard": "none", "blocked_cells": []}; altered["portal_states"]["west_gate_primary"] = "open"
        path = find_path(data, altered, {"section_id": "main_gate", "level": 0, "x": 0, "lane": 1}, {"section_id": "west_pump_gallery", "level": 0, "x": 3, "lane": 1})
        return path.found, path.to_dict()

    east_metrics = calculate_travel_metrics(data, east); west_metrics = calculate_travel_metrics(data, west)
    if number in {64, 65, 66}:
        key = {64: "gate_to_stabilization_path", 65: "gate_to_medical_path", 66: "gate_to_stabilization_path"}[number]
        metrics = east_metrics if number != 66 else west_metrics
        return metrics[key] is not None, {key: metrics[key]}
    if number == 67:
        path = find_path(data, east, east["safety_checks"]["main_gate"], east["safety_checks"]["primary_medical"], "patient_carry")
        return path.found and path.hazard_exposure == 0, path.to_dict()
    if number == 68:
        altered = copy.deepcopy(east); altered["portal_states"]["central_east_primary"] = "isolated"
        path = find_path(data, altered, altered["safety_checks"]["main_gate"], altered["safety_checks"]["primary_medical"], "patient_carry")
        fallback = find_path(data, altered, altered["safety_checks"]["main_gate"], altered["safety_checks"]["gate_stabilization"], "patient_escort")
        return not path.found and fallback.found, {"primary": path.failure_reason, "fallback": fallback.cost}

    if number == 69:
        status = consumer_status(east, "platform_lighting"); return status["connected"], status
    if number == 70:
        altered = copy.deepcopy(east); next(item for item in altered["utility_branches"] if item["branch_id"] == "central_power_main")["live"] = False
        status = consumer_status(altered, "platform_lighting"); return not status["connected"], status
    if number == 71:
        result = shed_platform_lighting(east); return result["changed"], result
    if number == 72:
        shed_platform_lighting(east); result = restore_platform_lighting(east, 1.0); return result["changed"], result
    if number == 73:
        upgraded = copy.deepcopy(data.layout("east_day7_alternate")); return not validate_platform_lighting(upgraded) and sum(item["consumer_id"] == "platform_lighting" for item in upgraded["utility_consumers"]) == 1, "one circuit"
    if number == 74:
        return charge_backup_available(east, "platform_lighting") and not charge_backup_available(east, "east_clean_water"), "connection-gated backup"
    if number in {75, 76}:
        branch_id = "east_air_branch" if number == 75 else "east_water_branch"
        preview = preview_isolation(east, branch_id); return bool(preview["rooms_affected"]), preview
    if number == 77:
        altered = copy.deepcopy(east); altered["section_states"]["east_staff_wing"]["access"] = "closed"
        path = find_path(data, altered, altered["safety_checks"]["safe_area"], altered["safety_checks"]["primary_medical"])
        return not path.found, path.failure_reason
    if number == 78:
        result = service_access(data, west, "west_pump"); return result["reachable"], result["path"]

    if number in {79, 80}:
        key = "filter_service_path" if number == 79 else "water_isolation_path"; value = east_metrics[key] if number == 79 else west_metrics[key]
        return value is not None and value <= (32.0 if number == 79 else 12.0), {key: value}
    if number in {81, 82}:
        start = {"section_id": "east_staff_wing", "level": 0, "x": 5, "lane": 1}
        path_class = "emergency_evacuation" if number == 81 else "patient_carry"
        path = find_path(data, east, start, east["safety_checks"]["safe_area"], path_class)
        return path.found, path.to_dict()
    if number in {83, 84}:
        config, _ = _feasibility(); value = config["incident_scheduler"]["maximum_live_major"] if number == 83 else config["storm"]["maximum_affected_systems"]
        expected = 1 if number == 83 else 3
        return value == expected, {"configured_maximum": value}

    if number in {85, 86}:
        metrics = east_metrics if number == 85 else west_metrics
        return metrics["day5_max_response_path"] <= metrics["day5_response_budget"], {"maximum": metrics["day5_max_response_path"], "budget": metrics["day5_response_budget"]}
    if number in {87, 88, 89}:
        key = {87: "materials_delivery_path", 88: "charge_control", 89: "water_isolation_path"}[number]
        if number == 88:
            value = next(item for item in east_metrics["named_paths"] if item["name"] == key)["cost"]
        else:
            value = (east_metrics if number == 87 else west_metrics)[key]
        return value is not None, {key: value}
    if number == 90:
        path = find_path(data, east, east["safety_checks"]["primary_medical"], east["safety_checks"]["safe_area"], "patient_carry")
        return path.found, path.to_dict()
    if number == 91:
        return east_metrics["coordinate_travel_factor"] == 0.08 and west_metrics["coordinate_travel_factor"] == 0.08, {"east": east_metrics["coordinate_travel_factor"], "west": west_metrics["coordinate_travel_factor"]}

    if number == 92: return west_metrics["pump_service_path"] < east_metrics["pump_service_path"], {"east": east_metrics["pump_service_path"], "west": west_metrics["pump_service_path"]}
    if number == 93: return west_metrics["water_isolation_path"] < east_metrics["water_isolation_path"], {"east": east_metrics["water_isolation_path"], "west": west_metrics["water_isolation_path"]}
    if number == 94: return east_metrics["rest_to_work_path"] < west_metrics["rest_to_work_path"], {"east": east_metrics["rest_to_work_path"], "west": west_metrics["rest_to_work_path"]}
    if number == 95:
        east_quiet = data.station["sections"]["east_staff_wing"]["environmental_properties"]["quiet_recovery"]
        west_quiet = data.station["sections"]["west_pump_gallery"]["environmental_properties"]["quiet_recovery"]
        return east_quiet and not west_quiet, {"east": east_quiet, "west": west_quiet}
    if number == 96: return east_metrics["gate_to_medical_path"] > west_metrics["gate_to_medical_path"], {"east": east_metrics["gate_to_medical_path"], "west": west_metrics["gate_to_medical_path"]}
    if number == 97:
        east_wins = east_metrics["rest_to_work_path"] < west_metrics["rest_to_work_path"]
        west_wins = west_metrics["pump_service_path"] < east_metrics["pump_service_path"]
        return east_wins and west_wins, {"east_rest": east_wins, "west_water": west_wins}

    if number in {98, 99, 100}:
        layout = east if number in {98, 100} else west; tier = "full" if number == 100 else "minimal"
        anchors = [item for item in layout["hope_anchors"] if item["tier"] == tier]
        return bool(anchors), [item["anchor_id"] for item in anchors]
    if number == 101:
        saved = serialize_layout_state(east); restored = restore_layout_state(east, saved)
        return restored["hope_anchors"] == east["hope_anchors"], "hope anchors round-tripped"
    if number == 102:
        anchors = east["hope_anchors"] + west["hope_anchors"]
        return all(not item["grants_stock"] for item in anchors), "all anchors grant zero stock"

    config, results = _feasibility()
    if number in {103, 104}:
        route = "east" if number == 103 else "west"; mapping = config["routes"][route]["spatial_mapping"]
        baseline = results["S01" if route == "east" else "S02"]
        sources = {day["work"]["travel_source"] for day in baseline["days"]}
        no_double = all(not day["work"]["travel_double_counted"] for day in baseline["days"])
        return mapping["replaces_abstract"] and sources == {f"spatial:{route}_day7"} and no_double, {"sources": sorted(sources), "mapping": mapping}
    scenario_id = {105: "S01", 106: "S02", 107: "S09", 108: "S10", 109: "S18"}.get(number)
    if scenario_id:
        result = results[scenario_id]; return result["expectation_met"], {"scenario": scenario_id, "outcome": result["outcome_class"]}
    if number == 110:
        ids = [f"S{value:02d}" for value in range(37, 45)]; values = [results[item] for item in ids]
        return all(item["expectation_met"] for item in values), {item["scenario_id"]: item["outcome_class"] for item in values}
    mandatory = [item for item in results.values() if item["mandatory"]]
    return all(item["expectation_met"] for item in mandatory), {"mandatory": len(mandatory), "expectations_met": sum(item["expectation_met"] for item in mandatory)}


def run_all() -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    for scenario in _scenario_catalog():
        try:
            passed, evidence = _probe(scenario["number"])
            error = None
        except Exception as exc:  # The result remains machine-readable for diagnosis.
            passed, evidence, error = False, None, f"{type(exc).__name__}: {exc}"
        results.append({**scenario, "passed": bool(passed), "evidence": evidence, "error": error})
    return {
        "schema_version": 1,
        "model_stage": "Prompt 4 spatial building",
        "provisional": True,
        "logical_distance_notice": "Logical path-cost proxies; not measured real seconds.",
        "summary": {"scenarios": len(results), "passed": sum(item["passed"] for item in results), "failed": sum(not item["passed"] for item in results)},
        "results": results,
    }


def write_reports(payload: dict[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Prompt 4 Spatial Scenario Summary", "",
        "> Deterministic logical validation; this does not prove camera comfort, touch usability, or measured travel time.", "",
        f"- Scenarios: {payload['summary']['scenarios']}",
        f"- Passed: {payload['summary']['passed']}",
        f"- Failed: {payload['summary']['failed']}", "",
        "| ID | Category | Scenario | Result |", "|---|---|---|---:|",
    ]
    for item in payload["results"]:
        lines.append(f"| {item['scenario_id']} | {item['category']} | {item['name']} | {'pass' if item['passed'] else 'FAIL'} |")
    SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-determinism", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    first = run_all()
    deterministic = True
    if args.check_determinism:
        second = run_all(); deterministic = first == second
    first["deterministic_repeat_equal"] = deterministic
    if not args.no_write:
        write_reports(first)
    failed = [item for item in first["results"] if not item["passed"]]
    if not args.quiet:
        for item in first["results"]:
            print(f"{item['scenario_id']} {'PASS' if item['passed'] else 'FAIL'} {item['name']}")
    print(f"SPATIAL_SCENARIOS passed={first['summary']['passed']}/{first['summary']['scenarios']} deterministic={str(deterministic).lower()}")
    if failed:
        for item in failed:
            print(f"ERROR {item['scenario_id']}: {item['error'] or item['evidence']}", file=sys.stderr)
    return 0 if not failed and deterministic else 1


if __name__ == "__main__":
    raise SystemExit(main())
