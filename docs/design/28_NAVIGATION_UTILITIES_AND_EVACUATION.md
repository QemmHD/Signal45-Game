# Signal 45 — Navigation, Utilities, and Evacuation

Status: Prompt 4 deterministic graph and service-access contract. It is not resident task-selection AI.

## Navigation graph

Walkable cells create horizontal and bounded lane edges. Portals add authored cross-section or vertical edges when state, width, and path-class rules permit. Dijkstra is used because lane changes, portals, carrying, and hazards have unequal costs. The result includes path cells, normalized cost, failure reason, required portals, hazard exposure, vertical transitions, and carry restrictions.

Closed sections, installed blockers, active hazards, construction zones, and isolated portals update the graph deterministically. Navigation caches may exist later for performance but are never authoritative save data.

## Path classes

| Class | Width | Relative carry cost | Main restrictions | Use |
|---|---:|---:|---|---|
| Normal walk | 1 | 1.00 | Avoid unsafe hazard cells | Routine resident movement |
| Material carry | 1 | 1.15 | Avoid unsafe hazards | Components and ordinary deliveries |
| Heavy carry | 2 | 1.45 | No ladder/narrow portal | Machinery and major debris |
| Patient escort | 1 | 1.25 | No ladder | Conscious assisted patient |
| Patient carry/stretcher | 2 | 1.60 | No ladder or narrow service door | Restricted resident transport |
| Emergency evacuation | 1 | 0.90 | Safest available route | Rapid movement to safe area |
| Utility service | 1 | 1.20 | Requires service endpoint | Filter, pump, valve, breaker and support repair |

All seven classes are executed in tests. Prompt 4 does not select tasks, form schedules, or implement local collision avoidance.

## Destinations and interaction points

Rooms and usable objects have at least one reachable interaction point: bed/cot side, workbench front, filter or pump service position, cabinet access, relay console, isolation control, medical position, construction approach, or door control. Validation rejects an interaction outside its room, through a wall, inside a permanent blocker, or unreachable by its required path class.

## Portals and closure

Portal closure previews residents, essential rooms, utility relationships, hazard boundary, evacuation effect, and recovery behavior. The slice refuses a change that traps anyone or removes required safe/treatment access. Restoring a portal produces deterministic repathing.

The layouts retain one identified gate-to-safe single point of failure; that is explicit risk, not hidden redundancy. Because the service passage is partly occupied in the starting camp, the primary gate passage may not be isolated until an alternate is actually clear. This is enforced, not merely warned.

## Utility topology

Utilities connect at section level; the player never draws individual wires or pipes.

### Power

Source → distribution bus → section branch → consumer. Consumers retain Prompt 3 priority. The Platform Work Lamp is the only Optional slice lighting consumer. Charge backup requires a live compatible node and cannot bridge a disconnected branch.

### Air

Filter/source → section node → served rooms. Doors and section adjacency define contamination boundaries. Isolation, filter service, evacuation and protection use explicit cells and paths.

### Water

Source → pump → treatment → delivery/storage. East adds a reserve but services Water through the distant central equipment. West adds direct pump, treatment, clean storage and drain/isolation access in one gallery.

### Structure

Local support zones connect to closure boundaries. State remains Safe, Strained, Unstable, Critical, or Closed. A closure removes local cells/portals and creates evacuation and recovery requirements; it does not propagate as realistic engineering simulation.

A room/object operates only when its section is served, its node and branch are live, capacity exists in the Prompt 3 model, and its service point remains reachable.

## Incident mapping

| Incident | Spatial authority |
|---|---|
| Power instability | Source/bus, affected branch and consumer, shed object, service route |
| Air contamination | Affected/adjacent sections, seal boundary, safe section, filter and evacuation routes |
| Water contamination | Failing source/pump/treatment/storage location, isolation control, clean alternate storage |
| Structural instability | Local cells, support zone, closure boundary, evacuation path |
| Equipment breakdown | Object, interaction/service point, Materials destination |
| Medical emergency | Resident placeholder, gate stabilization, primary Medical destination and patient path |

The incident scheduler and maximum Air → Power → Water depth remain controlled by Prompt 3. No fluid, gas, smoke, or structural particle simulation is introduced.

## East gate Medical audit

Canonical East logical costs:

- gate → stabilization: 1.25;
- gate → primary Medical by patient carry: 28.8;
- patient-carry route: valid through the two-cell primary East door;
- isolated primary East door: primary carry fails, but gate stabilization remains available;
- concurrent storm warning: the declared route avoids active hazard cells; stabilization can occur before a later transfer.

East is intentionally inconvenient from the gate, but it is not a wrong route. Immediate stabilization exists at the threshold, and the long transfer buys better treatment space and quiet recovery.

## West Water geometry audit

Canonical West versus East:

| Metric | East | West | Advantage |
|---|---:|---:|---|
| Water-service/pump path | 7.2 | 6.0 | West |
| Water isolation path | 21.6 | 8.4 | West |
| routine Materials delivery | 11.5 | 5.75 | West |
| direct pump/treatment nodes | central service only + reserve | dedicated pump + treatment + clean storage | West |
| drain/isolation control | reserve branch | dedicated drain and treatment branches | West |
| Rest-to-work path | 3.0 | 7.0 | East |
| quiet recovery | yes | no | East |

West also has better post-storm Water repair access. East retains stored reserve, better Rest and care space, and longer Water service routes. Neither dominates all spatial metrics.

## Day 5 spatial response

All canonical paths fit their declared 32-cost proxy budget:

- East filter service 7.2; Water isolation 21.6; Charge control 1.2; evacuation 9.9.
- West filter service 10.8; Water isolation 8.4; Charge control 10.8; evacuation 9.0.

Filter Materials have a valid carry route. The lamp and Power controls are reachable without added project WU. Charge only supports a connected consumer. Isolation previews lost Water service and traps nobody. Both routes support patient carry/evacuation. Temporary bypass installation has a service point and retains its later repair obligation.

These costs calibrate the existing travel allowance; they are not added as new Day 5 labor.
