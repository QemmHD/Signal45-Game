#!/usr/bin/env python3
"""Run deterministic Signal 45 Prompt 2 scenarios and emit reports."""

from __future__ import annotations

import argparse
import json
import sys
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


def _invariant_errors(results: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    by_id = {result["scenario_id"]: result for result in results}
    for result in results:
        if result["mandatory"] and not result["expectation_met"]:
            errors.append(
                f"{result['scenario_id']}: expected viable={result['expected_viable']} "
                f"but got {result['viable']}"
            )
        for day in result["days"]:
            negatives = {
                name: amount
                for name, amount in day["stocks_end"].items()
                if amount < 0
            }
            if negatives:
                errors.append(f"{result['scenario_id']}: illegal negative stocks {negatives}")
        if result["expected_viable"] and result["final"]["incomplete_required_projects"]:
            errors.append(
                f"{result['scenario_id']}: required projects incomplete "
                f"{result['final']['incomplete_required_projects']}"
            )
        probe = result.get("save_probe")
        if probe and not probe["passed"]:
            errors.append(f"{result['scenario_id']}: save probe failed")
    for scenario_id in ["S01", "S02"]:
        if scenario_id in by_id:
            result = by_id[scenario_id]
            if not result["viable"] or result["highball"] is not None:
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
    config: dict[str, Any], results: list[dict[str, Any]], errors: list[str]
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "generated_from_source_commit": config["metadata"]["source_commit"],
        "provisional": True,
        "model_claims": [
            "internal consistency",
            "schedule feasibility",
            "route viability",
            "recovery margin",
            "serialization logic",
            "sensitivity",
        ],
        "model_does_not_claim": [
            "enjoyment",
            "comprehension",
            "tactility",
            "camera comfort",
            "visual readability",
            "emotional impact",
            "measured player-session pacing",
        ],
        "summary": {
            "scenarios": len(results),
            "expectations_met": sum(result["expectation_met"] for result in results),
            "viable_outcomes": sum(result["viable"] for result in results),
            "expected_infeasible_outcomes": sum(
                result["expectation_met"] and not result["viable"] for result in results
            ),
            "invariant_errors": len(errors),
        },
        "invariant_errors": errors,
        "results": results,
    }


def _markdown_summary(payload: dict[str, Any]) -> str:
    lines = [
        "# Signal 45 Prompt 2 — Generated Scenario Summary",
        "",
        "> Generated from the canonical JSON model. All values are provisional and do not prove fun or measured pacing.",
        "",
        "## Run summary",
        "",
        f"- Scenarios: {payload['summary']['scenarios']}",
        f"- Expectations met: {payload['summary']['expectations_met']}",
        f"- Viable outcomes: {payload['summary']['viable_outcomes']}",
        f"- Expected infeasible outcomes detected: {payload['summary']['expected_infeasible_outcomes']}",
        f"- Invariant errors: {payload['summary']['invariant_errors']}",
        "",
        "## Scenario matrix",
        "",
        "| ID | Route | Category | Expected | Actual | Buffer | Areas | Exact failure or limiting fact |",
        "|---|---|---|---:|---:|---:|---:|---|",
    ]
    for result in payload["results"]:
        reason = result["final"]["exact_failure_reason"] or "—"
        reason = reason.replace("|", "\\|")
        lines.append(
            f"| {result['scenario_id']} | {result['route'].title()} | {result['category']} | "
            f"{str(result['expected_viable']).lower()} | {str(result['viable']).lower()} | "
            f"{result['final']['usable_buffer_percent']:.1f}% | "
            f"{result['final']['functional_areas']} | {reason} |"
        )
    lines.extend(
        [
            "",
            "## Baseline route evidence",
            "",
        ]
    )
    result_map = {result["scenario_id"]: result for result in payload["results"]}
    for scenario_id in ["S01", "S02"]:
        if scenario_id not in result_map:
            continue
        result = result_map[scenario_id]
        lines.append(
            f"- **{scenario_id} {result['route'].title()}:** "
            f"viable={result['viable']}; areas={result['final']['functional_areas']}; "
            f"usable buffer={result['final']['usable_buffer_percent']:.1f}%; "
            f"Food={result['final']['stocks']['Food']:.1f}; "
            f"Clean Water={result['final']['stocks']['Clean Water']:.1f}; "
            f"Highball used={result['highball'] is not None}."
        )
    lines.extend(
        [
            "",
            "## Expected failures that falsify favorable assumptions",
            "",
        ]
    )
    for result in payload["results"]:
        if not result["viable"] and result["expectation_met"]:
            lines.append(
                f"- **{result['scenario_id']} — {result['name']}:** "
                f"{result['final']['exact_failure_reason']}"
            )
    lines.extend(
        [
            "",
            "The machine-readable file contains daily and phase-level work, stock, utility, project, incident, expedition, admission, save, ending, buffer, and failure data for every scenario.",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", action="append", help="Run only this scenario ID; may repeat")
    parser.add_argument("--category", help="Run only one category")
    parser.add_argument("--mandatory", action="store_true", help="Run scenarios marked mandatory")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
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
    errors = _invariant_errors(results)
    payload = _payload(config, results, errors)
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
            outcome = "viable" if result["viable"] else "infeasible"
            reason = result["final"]["exact_failure_reason"] or "baseline gates met"
            print(
                f"{status} {result['scenario_id']} {result['route']} {outcome} "
                f"buffer={result['final']['usable_buffer_percent']:.1f}% {reason}"
            )
        print(
            f"SUMMARY scenarios={len(results)} expectations_met="
            f"{payload['summary']['expectations_met']} invariant_errors={len(errors)}"
        )
    if errors:
        for error in errors:
            print(f"ERROR {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
