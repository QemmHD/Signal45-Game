#!/usr/bin/env python3
"""Run deterministic Signal 45 Prompt 3 scenarios and emit canonical reports."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

try:
    from .model import load_inputs, run_scenarios
    from .validate_data import DataValidationError
except ImportError:
    from model import load_inputs, run_scenarios
    from validate_data import DataValidationError


ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT = ROOT / "reports" / "scenario_results.json"
DEFAULT_SUMMARY = ROOT / "reports" / "scenario_summary.md"
VIABLE_CLASSES = {"FULL_PROOF", "RECOVER_FIRST"}
OUTCOME_CLASSES = {
    "FULL_PROOF",
    "RECOVER_FIRST",
    "PROOF_INCOMPLETE",
    "SHELTER_FAILURE",
    "INVARIANT_ERROR",
}


def _quality_errors(results: list[dict[str, Any]]) -> list[str]:
    """Return unexpected defects; expected adverse outcomes are evidence, not errors."""
    errors: list[str] = []
    by_id = {result["scenario_id"]: result for result in results}
    for result in results:
        scenario_id = result["scenario_id"]
        if result["mandatory"] and not result["expectation_met"]:
            errors.append(
                f"{scenario_id}: expected {result['expected_outcome_class']} "
                f"but got {result['outcome_class']}"
            )
        if result["outcome_class"] not in OUTCOME_CLASSES:
            errors.append(f"{scenario_id}: unknown outcome class {result['outcome_class']}")
        if result["viable"] != (result["outcome_class"] in VIABLE_CLASSES):
            errors.append(f"{scenario_id}: viability is not derived from outcome class")
        if result["survival_viable"] != (
            result["outcome_class"] not in {"SHELTER_FAILURE", "INVARIANT_ERROR"}
        ):
            errors.append(f"{scenario_id}: survival viability conflicts with outcome class")
        if result["slice_proof_complete"] != (result["outcome_class"] == "FULL_PROOF"):
            errors.append(f"{scenario_id}: proof-complete flag conflicts with outcome class")
        for day in result["days"]:
            negatives = {
                name: amount
                for name, amount in day["stocks_end"].items()
                if amount < 0
            }
            if negatives:
                errors.append(f"{scenario_id}: illegal negative stocks {negatives}")
        if (
            result["outcome_class"] == "FULL_PROOF"
            and result["final"]["incomplete_required_projects"]
        ):
            errors.append(
                f"{scenario_id}: FULL_PROOF with incomplete projects "
                f"{result['final']['incomplete_required_projects']}"
            )
        probe = result.get("save_probe")
        if probe and not probe["passed"]:
            errors.append(f"{scenario_id}: save probe failed")
        if result["expected_outcome_class"] != "INVARIANT_ERROR" and not result["invariant_valid"]:
            errors.append(f"{scenario_id}: unexpected invariant error")

    for scenario_id in ["S01", "S02"]:
        if scenario_id in by_id:
            result = by_id[scenario_id]
            if result["outcome_class"] != "FULL_PROOF" or result["highball"] is not None:
                errors.append(f"{scenario_id}: competent base route requires or uses Highball")
    if "S31" in by_id and "S32" in by_id:
        active = by_id["S31"]["expedition"]
        delegated = by_id["S32"]["expedition"]
        if not active["required_secured"] or not delegated["required_secured"]:
            errors.append("active/delegated expedition required objective mismatch")
        if active["exclusive_reward"] or delegated["exclusive_reward"]:
            errors.append("expedition mode-exclusive reward detected")
    return errors


def _payload(
    config: dict[str, Any],
    results: list[dict[str, Any]],
    errors: list[str],
    deterministic: bool,
) -> dict[str, Any]:
    counts = Counter(result["outcome_class"] for result in results)
    expected_invariants = sum(
        result["outcome_class"] == "INVARIANT_ERROR"
        and result["expected_outcome_class"] == "INVARIANT_ERROR"
        for result in results
    )
    return {
        "schema_version": 2,
        "model_stage": "Prompt 3 survival systems",
        "generated_from_source_commit": config["metadata"]["source_commit"],
        "provisional": True,
        "deterministic_repeat_equal": deterministic,
        "model_claims": [
            "internal consistency",
            "bounded progression",
            "recovery logic",
            "outcome classification",
            "resource arithmetic",
            "utility causality",
            "save idempotency",
        ],
        "model_does_not_claim": [
            "enjoyment",
            "comprehension",
            "tactile response",
            "forecast readability",
            "camera readability",
            "incident tension",
            "measured player-session pacing",
        ],
        "summary": {
            "scenarios": len(results),
            "expectations_met": sum(result["expectation_met"] for result in results),
            "outcome_counts": {name: counts.get(name, 0) for name in sorted(OUTCOME_CLASSES)},
            "survival_viable": sum(result["survival_viable"] for result in results),
            "slice_proof_complete": sum(result["slice_proof_complete"] for result in results),
            "expected_invariant_detections": expected_invariants,
            "unexpected_quality_errors": len(errors),
        },
        "quality_errors": errors,
        "results": results,
    }


def _markdown_summary(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Signal 45 Prompt 3 — Generated Survival Scenario Summary",
        "",
        "> Generated from canonical JSON. Values are provisional; this model does not prove fun, comprehension, or measured pacing.",
        "",
        "## Run summary",
        "",
        f"- Scenarios: {summary['scenarios']}",
        f"- Expectations met: {summary['expectations_met']}",
        f"- Deterministic repeat equal: {str(payload['deterministic_repeat_equal']).lower()}",
        f"- Full proof: {summary['outcome_counts']['FULL_PROOF']}",
        f"- Recover First: {summary['outcome_counts']['RECOVER_FIRST']}",
        f"- Proof incomplete: {summary['outcome_counts']['PROOF_INCOMPLETE']}",
        f"- Shelter failure: {summary['outcome_counts']['SHELTER_FAILURE']}",
        f"- Expected invariant detections: {summary['expected_invariant_detections']}",
        f"- Unexpected quality errors: {summary['unexpected_quality_errors']}",
        "",
        "## Scenario matrix",
        "",
        "| ID | Route | Category | Expected class | Actual class | Survival | Proof | Min daily slack | Critical-path slack | Exact limiting fact |",
        "|---|---|---|---|---|---:|---:|---:|---:|---|",
    ]
    for result in payload["results"]:
        resilience = result["final"]["schedule_resilience"]
        reason = result["exact_limiting_fact"].replace("|", "\\|")
        lines.append(
            f"| {result['scenario_id']} | {result['route'].title()} | {result['category']} | "
            f"{result['expected_outcome_class']} | {result['outcome_class']} | "
            f"{str(result['survival_viable']).lower()} | {str(result['slice_proof_complete']).lower()} | "
            f"{resilience['minimum_daily_uncommitted_work']:.1f} WU | "
            f"{resilience['minimum_critical_path_slack_days']:.1f} d | {reason} |"
        )

    lines.extend(["", "## Baseline route evidence", ""])
    result_map = {result["scenario_id"]: result for result in payload["results"]}
    for scenario_id in ["S01", "S02"]:
        if scenario_id not in result_map:
            continue
        result = result_map[scenario_id]
        resilience = result["final"]["schedule_resilience"]
        lines.append(
            f"- **{scenario_id} {result['route'].title()}:** {result['outcome_class']}; "
            f"areas={result['final']['functional_areas']}; aggregate unused="
            f"{resilience['aggregate_weekly_unused_work']:.1f} WU; minimum daily slack="
            f"{resilience['minimum_daily_uncommitted_work']:.1f} WU; incident reserve unused="
            f"{resilience['incident_response_reserve_unused']:.1f} WU; Highball used="
            f"{result['highball'] is not None}."
        )

    lines.extend(["", "## Expected adverse outcomes", ""])
    for result in payload["results"]:
        if result["outcome_class"] != "FULL_PROOF" and result["expectation_met"]:
            lines.append(
                f"- **{result['scenario_id']} — {result['name']}:** "
                f"{result['outcome_class']} — {result['exact_limiting_fact']}"
            )
    lines.extend(
        [
            "",
            "The machine-readable report includes day/phase work, stocks, conditions, utilities, forecasts, incidents, treatment, promises, outcome classification, schedule-resilience metrics, and save evidence.",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", action="append", help="Run only this scenario ID; may repeat")
    parser.add_argument("--category", help="Run only one category")
    parser.add_argument("--mandatory", action="store_true", help="Run scenarios marked mandatory")
    parser.add_argument("--check-determinism", action="store_true", help="Run selected cases twice and compare")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--no-write", action="store_true", help="Validate without changing reports")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)
    try:
        config, scenarios = load_inputs()
    except DataValidationError as exc:
        print(f"DATA INVALID: {exc}", file=sys.stderr)
        return 2

    selected = scenarios
    if args.scenario:
        requested = set(args.scenario)
        selected = [scenario for scenario in selected if scenario["id"] in requested]
        missing = requested - {scenario["id"] for scenario in selected}
        if missing:
            print(f"Unknown scenario IDs: {sorted(missing)}", file=sys.stderr)
            return 2
    if args.category:
        selected = [scenario for scenario in selected if scenario["category"] == args.category]
    if args.mandatory:
        selected = [scenario for scenario in selected if scenario["mandatory"]]
    if not selected:
        print("No scenarios selected", file=sys.stderr)
        return 2

    results = run_scenarios(config, selected)
    deterministic = True
    if args.check_determinism:
        deterministic = results == run_scenarios(config, selected)
    errors = _quality_errors(results)
    if not deterministic:
        errors.append("deterministic repeat differs")
    payload = _payload(config, results, errors, deterministic)
    if not args.no_write:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.summary.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )
        args.summary.write_text(_markdown_summary(payload), encoding="utf-8")

    if not args.quiet:
        for result in results:
            status = "PASS" if result["expectation_met"] else "FAIL"
            slack = result["final"]["schedule_resilience"]["minimum_daily_uncommitted_work"]
            print(
                f"{status} {result['scenario_id']} {result['route']} "
                f"{result['outcome_class']} survival={result['survival_viable']} "
                f"proof={result['slice_proof_complete']} min_daily_slack={slack:.1f} "
                f"{result['exact_limiting_fact']}"
            )
        print(
            f"SUMMARY scenarios={len(results)} expectations_met="
            f"{payload['summary']['expectations_met']} deterministic={deterministic} "
            f"unexpected_quality_errors={len(errors)}"
        )
    if errors:
        for error in errors:
            print(f"ERROR {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
