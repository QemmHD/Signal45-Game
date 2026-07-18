"""Shared, confidence-aware forecast cards for Signal 45 Prompt 3."""

from __future__ import annotations

from typing import Any


FORECAST_CLASSES = {
    "FACT",
    "PROJECTION",
    "ESTIMATE",
    "SIGNAL_INTELLIGENCE",
    "UNKNOWN",
}


def rounded(value: float) -> float:
    return round(float(value) + 0.0, 3)


def build_forecast_card(
    *,
    subject: str,
    classification: str,
    current: float | str | None,
    committed_use: float = 0.0,
    expected_gain: float = 0.0,
    confidence: str = "measured",
    main_source: str | None = None,
    main_drain: str | None = None,
    failing_link: str | None = None,
    next_consequence: str | None = None,
    responses: list[str] | None = None,
    horizon: str = "next ledger",
    unknown_reason: str | None = None,
) -> dict[str, Any]:
    if classification not in FORECAST_CLASSES:
        raise ValueError(f"unknown forecast classification {classification}")
    if classification == "UNKNOWN" and not unknown_reason:
        raise ValueError("UNKNOWN forecast requires a missing-information reason")
    projected = None
    if isinstance(current, (int, float)):
        projected = rounded(float(current) - committed_use + expected_gain)
    return {
        "subject": subject,
        "classification": classification,
        "current": current,
        "committed_use": rounded(committed_use),
        "expected_gain": rounded(expected_gain),
        "projected": projected,
        "horizon": horizon,
        "confidence": confidence,
        "main_source": main_source,
        "main_drain": main_drain,
        "failing_link": failing_link,
        "likely_next_consequence": next_consequence,
        "recommended_responses": list(responses or []),
        "unknown_reason": unknown_reason,
        "false_precision_avoided": classification in {"ESTIMATE", "SIGNAL_INTELLIGENCE", "UNKNOWN"},
        "overview_tap_depth": 2 if failing_link else 1,
    }


def stock_forecast_card(
    config: dict[str, Any], stock: str, amount: float, *, resident_count: int = 4
) -> dict[str, Any]:
    data = config["stocks"][stock]
    if amount < data["minimum_viable_reserve"]:
        status = "critical"
    elif amount < data["warning_threshold"]:
        status = "warning"
    elif amount < data["comfortable_reserve"]:
        status = "tight"
    else:
        status = "comfortable"
    per_day = float(data.get("normal_per_resident_day", 0.0)) * resident_count
    person_days = None
    if per_day > 0:
        person_days = rounded(amount / per_day)
    card = build_forecast_card(
        subject=stock,
        classification="PROJECTION",
        current=amount,
        confidence="committed-ledger",
        main_source=data.get("primary_sources", [None])[0],
        main_drain=data.get("primary_sinks", [None])[0],
        next_consequence=data.get("critical_consequence"),
        responses=data.get("ordinary_responses", []),
    )
    card.update(
        {
            "amount": rounded(amount),
            "status": status,
            "minimum_viable_reserve": data["minimum_viable_reserve"],
            "comfortable_reserve": data["comfortable_reserve"],
            "operating_days_at_current_issue": person_days,
        }
    )
    return card
