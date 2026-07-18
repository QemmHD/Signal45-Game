# Signal 45

Mobile-first survival management, railway shelter construction, community simulation, narrative strategy, and supporting scavenging expeditions.

## Development status

Prompt 2 adds a deterministic seven-day feasibility model on top of the Prompt 1 design foundation. At provisional inputs, both routes pass without Highball and expected adverse cases fail. This is not evidence that the game is fun, balanced in play, production-ready, technically validated on devices, or legally cleared.

## Design foundation

1. [Concept Lock](docs/design/00_CONCEPT_LOCK.md)
2. [Design Pillars](docs/design/01_DESIGN_PILLARS.md)
3. [Core Loop and Campaign](docs/design/02_CORE_LOOP_AND_CAMPAIGN.md)
4. [Scope Matrix](docs/design/03_SCOPE_MATRIX.md)
5. [Originality Boundaries](docs/design/04_ORIGINALITY_BOUNDARIES.md)
6. [Visual and Camera Contract](docs/design/05_VISUAL_AND_CAMERA_CONTRACT.md)
7. [Base-Building Direction](docs/design/06_BASE_BUILDING_DIRECTION.md)
8. [Vertical Slice — The First Count](docs/design/07_VERTICAL_SLICE.md)
9. [Production Risk Register](docs/design/08_RISK_REGISTER.md)
10. [Decision Log](docs/design/09_DECISION_LOG.md)
11. [Next-Stage Requirements](docs/design/10_NEXT_STAGE_REQUIREMENTS.md)
12. [Session and Phase Timing](docs/design/11_SESSION_AND_PHASE_TIMING.md)
13. [Work and Construction Model](docs/design/12_WORK_AND_CONSTRUCTION_MODEL.md)
14. [Resource and Utility Feasibility](docs/design/13_RESOURCE_AND_UTILITY_FEASIBILITY.md)
15. [Seven-Day Feasibility](docs/design/14_SEVEN_DAY_FEASIBILITY.md)
16. [First Session and Safe Stops](docs/design/15_FIRST_SESSION_AND_SAFE_STOPS.md)
17. [Sensitivity and Revalidation](docs/design/16_SENSITIVITY_AND_REVALIDATION.md)
18. [Prompt 2 Decisions](docs/design/17_PROMPT_2_DECISIONS.md)

## Feasibility model

Python 3.12 and the standard library are sufficient.

```powershell
python tools/feasibility/validate_data.py
python -m unittest discover -s tools/feasibility/tests -v
python tools/feasibility/run_scenarios.py --mandatory
```

`tools/feasibility/data/model.json` is the single canonical balance source. `tools/feasibility/reports/scenario_results.json` contains day/phase-level machine-readable results; `scenario_summary.md` is the concise matrix. The CI workflow runs validation, all tests, and every mandatory scenario.

Prompt 3 is deliberately not started.
