# Signal 45 — Reclamation, Construction, and Placement

Status: Prompt 4 deterministic construction geometry and transaction contract.

## Reclamation targets

| Target | Section | Relevant stages | Unlock | Visible/preventable danger |
|---|---|---|---|---|
| Central stabilization | Central Platform | Survey, reinforce, inspect | Safe starting work and route information | Strained support; stabilize or accept a forecast risk |
| East obstruction | East Staff Wing | Survey, clear, reinforce, connect | Staff-wing cells, two portals, East nodes | Rubble shift is warned; brace/protection prevents injury |
| West flooded access | West Pump Gallery | Survey, isolate, drain, clear, inspect | Pump Gallery cells, two portals, Water nodes | Water/electrical contact is visible; isolate and drain first |
| East utility connection | East Staff Wing | Connect, inspect, activate | East Power/Air/Water reserve service | Disconnected branch cannot operate or accept Charge |
| West utility connection | West Pump Gallery | Connect, inspect, activate | Pump, treatment, drain and branch controls | Pump access remains serviceable after activation |
| Vertical route jam | Vertical Shaft | Inspect only in slice | Future expansion information | Cannot unlock or become pathable during The First Count |
| Optional service clearance | Authored service bay | Clear, salvage | Optional staging/storage flexibility | Never a hidden mandatory dependency |

Every target records occupied cells, obstacle and access state, survey state, hazards, work-order IDs, Materials/components, access/equipment/utility requirements, stage sequence, cells and portals unlocked, nodes exposed, salvage, preventable injury path, save boundaries, and acceptance condition.

## Construction lifecycle

1. **Preview** — local, spends nothing, claims nothing.
2. **Saved inactive blueprint** — persists but reserves no stock or labor.
3. **Activated project** — validates access/space and reserves Materials/components once.
4. **Delivery** — moves reserved value to the project once; delivered state persists.
5. **Resident construction** — consumes Work Units and retains exact partial progress.
6. **Equipment installation** — used only when the class needs it.
7. **Inspection/activation** — commits navigation, utility, and room capability once.
8. **Operational** — celebration animation may follow but is never authoritative.

Short objects skip unnecessary ceremony. Major reclamation may have multiple authored work orders. Interruptions preserve reservation, delivery, stage, and progress. Project dependencies are machine-checked.

## Reservation, cancellation, and deconstruction

- Activation has a transaction ID and reserves stock exactly once.
- Delivery has a separate transaction ID and cannot duplicate after reload.
- Cancellation returns only permitted undelivered value and records the refund.
- Delivered or consumed value is not magically restored.
- Deconstruction needs valid access, removes capability and connections, and grants bounded salvage once.
- The salvage fraction is capped; rebuild/deconstruct cycles cannot create profit.

These rules preserve Prompt 2 and Prompt 3 transaction semantics.

## Placement validation

Validation returns a structured result containing a code, plain-language message, highlighted cells, suggested correction, and non-color accessibility indicator. It never returns only `false`.

Supported failures are:

- `outside_buildable_area`
- `overlaps_fixed_architecture`
- `overlaps_room`
- `overlaps_object`
- `blocks_required_portal`
- `blocks_only_route`
- `strands_resident`
- `strands_essential_room`
- `blocks_emergency_path`
- `blocks_interaction_point`
- `insufficient_clearance`
- `unsupported_rotation`
- `incompatible_room_family`
- `incompatible_section`
- `missing_socket`
- `missing_utility_node`
- `disconnected_branch`
- `structure_unsupported`
- `hazard_present`
- `project_space_reserved`
- `module_parent_invalid`
- `module_capacity_exceeded`

The validator checks the full layout after each proposed blocking placement, so several individually legal objects cannot combine unnoticed to strand a room. The same protection is applied to portal closure.

## Severe-placement policy

The First Count refuses a placement or closure that blocks the only shelter route, strands any resident or essential facility, closes the Main Gate, removes the only treatment or safe-area route, blocks all interaction points, prevents patient transport or evacuation, or makes a route-critical service node inaccessible. There is no override in the slice.

The full game may later support deliberate emergency isolation only after committed evacuation, explicit consequence preview, and a valid recovery path. That capability is not implemented here.

## Recovery from poor layout

Legal objects can be moved, stored, repurposed, or deconstructed. An inactive blueprint can be moved or canceled freely. Active projects retain material/progress semantics. Removing a valid blocker causes deterministic repathing. The `poor_valid` layout proves that inefficiency is survivable without pretending it is optimal: its coordinate factor is 12% travel and 7% hauling versus canonical East’s 8% and 4%.

## Construction-state presentation contract

| State | Geometry/material requirement | UI/accessibility requirement | Resident/audio/effect requirement |
|---|---|---|---|
| Unreclaimed | Full obstacle and cold/damaged shell | Name hazard and blocked access | No work activity beyond survey |
| Surveyed | Marked hazard and discovered edges | Symbol + text forecast | Inspection activity |
| Cleared | Removed bulk obstacle, unfinished surface | Remaining requirements | Debris/haul feedback |
| Blueprint | Ghost footprint and clearance | Cost, work, validity; pattern beyond color | No simulation benefit |
| Reserved | Claimed footprint | Reserved stock and cancel terms | Await delivery |
| Delivery | Visible staged materials | Delivery checkpoint | Carry activity and placement sound |
| Under construction | Progressive geometry | Exact stage/progress | Work activity, bounded particles |
| Installed | Complete geometry, not yet live | Activation requirement | Inspection activity |
| Operational | Functional material/light state | Capability and forecast effect | Normal use loop and sound |
| Impaired/damaged/critical | Readable wear, damage, warning silhouette | Cause, next consequence, timer/WU | Repair behavior; particles never sole warning |
| Isolated | Closed boundary and dead connection | Rooms/residents affected and recovery | Shutdown sound and clear symbol |
| Under repair | Access and repair staging | Required work/materials | Repair activity |
| Upgraded | Modified existing geometry | Same area/circuit unless explicitly split | Changed use/presentation |
| Repurposed | Retained shell with new interior cues | Old/new function and disruption | Move/install activity |

These are logical presentation requirements, not final asset production.
