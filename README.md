# Signal 45

Mobile-first survival management, railway shelter construction, community simulation, narrative strategy, and supporting scavenging expeditions.

## Development status

Prompt 4 adds an engine-independent station grid, machine-readable Day 1/East/West layouts, room/object footprints, reclamation, portals, utility nodes, placement safety, navigation, evacuation, Room Focus bounds, spatial travel proxies, and cross-model validation. Both competent routes still reach Full Proof without Highball. This is not evidence that building is fun, camera/touch controls are comfortable, travel timing is measured, the game is production-ready, or the project is legally cleared.

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
19. [Survival Resource Model](docs/design/18_SURVIVAL_RESOURCE_MODEL.md)
20. [Resident Conditions and Medical](docs/design/19_RESIDENT_CONDITIONS_AND_MEDICAL.md)
21. [Utility Networks and Forecasts](docs/design/20_UTILITY_NETWORKS_AND_FORECASTS.md)
22. [Weather, Incidents, Emergency Actions, and Highball](docs/design/21_WEATHER_INCIDENTS_AND_EMERGENCY_ACTIONS.md)
23. [Survival Simulation Results](docs/design/22_SURVIVAL_SIMULATION_RESULTS.md)
24. [Prompt 3 Decisions](docs/design/23_PROMPT_3_DECISIONS.md)
25. [Spatial Model and Coordinates](docs/design/24_SPATIAL_MODEL_AND_COORDINATES.md)
26. [Room Families and Placeable Objects](docs/design/25_ROOM_FAMILIES_AND_PLACEABLE_OBJECTS.md)
27. [Reclamation, Construction, and Placement](docs/design/26_RECLAMATION_CONSTRUCTION_AND_PLACEMENT.md)
28. [Mobile Build Mode and Camera](docs/design/27_MOBILE_BUILD_MODE_AND_CAMERA.md)
29. [Navigation, Utilities, and Evacuation](docs/design/28_NAVIGATION_UTILITIES_AND_EVACUATION.md)
30. [Vertical-Slice Layouts and Spatial Results](docs/design/29_VERTICAL_SLICE_LAYOUTS_AND_SPATIAL_RESULTS.md)
31. [Prompt 4 Decisions](docs/design/30_PROMPT_4_DECISIONS.md)

## Feasibility model

Python 3.12 and the standard library are sufficient.

```powershell
python tools/feasibility/validate_data.py
python -m unittest discover -s tools/feasibility/tests -v
python tools/feasibility/run_scenarios.py --mandatory --check-determinism
python tools/spatial/validate_layouts.py --write-reports
python -m unittest discover -s tools/spatial/tests -v
python tools/spatial/run_spatial_scenarios.py --check-determinism
python tools/spatial/generate_diagrams.py --check
```

`tools/feasibility/data/model.json` remains the canonical survival/work source. `tools/spatial/data/` is authoritative for coordinates, shells, rooms, objects, reclamation, and layouts. Generated feasibility and spatial reports are checked for deterministic cleanliness in CI.

Current evidence: 176/176 mandatory feasibility scenarios, 111/111 spatial scenarios, 144 feasibility tests, and 71 spatial tests pass locally. Prompt 5 is the next boundary; it must not reinterpret logical paths as full resident AI.
