# Signal 45 — Spatial Model and Coordinates

Status: Prompt 4 concept and deterministic validation contract. All dimensions, traversal costs, and camera bounds remain provisional until a graybox measures them.

## Authority boundary

The gameplay address is `section_id + level + x + lane`. Integer logical cells are the single authority for placement, navigation, utilities, incidents, and saves. A renderer derives 3D transforms from those cells. A render transform, animation object, screen projection, or path cache can never decide whether a room exists or a project completed.

The hierarchy is:

```text
Station
└─ Section
   └─ Bay
      └─ Cell
```

- **Station** is the authored interchange.
- **Section** is a reclamation, access, hazard, and utility unit.
- **Bay** is an architectural span: column interval, staff-room shell, platform segment, machinery zone, or service recess.
- **Cell** is the atomic placement, path, interaction, utility-service, hazard, and save address.

## Coordinate schema

An address is:

```json
{"section_id":"central_platform","level":0,"x":6,"lane":1}
```

`x` is section-local horizontal position, `level` is the authored floor, and `lane` is one of a small number of allowed depth lanes. Depth lanes do not create free 3D movement. They allow passing, equipment staging, foreground/background activity, and carry clearance where the shell explicitly supports them.

The provisional renderer conversion is 2.0 world units per cell horizontally, 3.2 per level, and 1.25 per lane. The validator executes local/global conversion, logical/world conversion, nearest-cell conversion, rotation, occupied footprints, interaction offsets, portal endpoints, utility-node addresses, and camera bounds. These conversions are covered by failing tests.

## Authoritative sections

| Section | Global X | Level | Lanes | Spatial identity | Slice state |
|---|---:|---:|---|---|---|
| West Pump Gallery | 0–7 | 0 | 0–1 | Drain channel, fixed pump machinery, wet service recesses | Flooded on Day 1; route-selectively reclaimed |
| Main Gate | 8–9 | 0 | 0–1 | Surface threshold, gate control, arrival stabilization | Operational but vulnerable |
| Central Platform | 10–23 | 0 | 0–2 | Platform edge, track lane, columns, camp, kiosk, service and concession shells | Starting inhabited core |
| East Staff Wing | 24–33 | 0 | 0–1 | Quiet staff shells and first-aid spaces | Rubble-blocked on Day 1; route-selectively reclaimed |
| Vertical Shaft | 34–36 | 0–1 | 0 | Jammed stair/lift volume and future utility riser | Visible and inspectable, never usable in the slice |

Every section records its origin, dimensions, bays, fixed architecture, buildable and walkable cells, portals, trunks, nodes, hazards, safe cells, occupancy ceiling, camera bounds, occlusion groups, selection volume, save fields, discovery condition, and possible story reveal.

## Fixed architecture and adaptation

Architecture is classified as follows:

- **Hard fixed:** tunnel walls, track bed, platform edge, structural columns, drainage channel, major machinery, shaft.
- **State-gated:** rubble, flooded access, jammed door, sealed shaft, damaged branch, unstable support.
- **Convertible shell:** staff room, kiosk, concession cage, platform bay, maintenance recess.
- **Player-placed:** beds, cots, cabinets, benches, utility modules, lights, barriers, emergency equipment, comfort and story objects.

Hard-fixed cells are rejected for ordinary placement. Authored work may change a state-gated feature. A convertible shell retains its railway geometry while accepting different room functions. This keeps the station recognizable and gives players interior freedom without freehand excavation.

## Portals and vertical links

Every portal has source and destination cells, type, width, permitted path classes, state, traversal cost, closure behavior, isolation behavior, utility relationship, hazard boundary, and save representation. States are `open`, `closed`, `locked`, `blocked`, `damaged`, `sealed`, `isolated`, or `under_repair`.

The Day 1 East and West portals are blocked. A chosen route opens both its primary and service portals. The East shaft link remains sealed and the upper lift remains blocked in every slice layout. Navigation never uses them, while the selection region `vertical_route_jam` keeps the future expansion inspectable.

Portal closure is previewed against resident locations, essential rooms, the safe area, affected utilities, and the recovery method. The slice refuses closure when it would trap a resident or remove required evacuation.

## Camera bounds

The shelter overview covers global X 0–36, levels 0–1, and lanes 0–2. Each room stores a focus target, minimum and maximum focus bounds, local pan allowance, occlusion group, fade targets, default selection, and return framing. These are presentation data derived from the same logical footprint; they do not fork the simulation.

## Save contract

Persist:

- section and reclamation state;
- portal state;
- room instance, family, footprint, rotation, and function;
- object and module logical address, parent, state, and connection;
- inactive and active blueprints, delivery and construction progress;
- utility-node connection and branch isolation;
- hazards and temporary conversions;
- hope-anchor state and the Platform Work Lamp;
- resident location placeholder;
- optional camera framing, Room Focus, and occlusion preference.

Do not persist engine components, render-object references, delegates/functions, transient animation handles, or derived path caches. Completion state commits before its celebration animation. Save/reload reconstructs identical logical geometry.

## Executed, recorded, and provisional fields

| Status | Fields |
|---|---|
| Executed by validator | Origins, levels, widths, lanes, buildable/walkable/fixed cells, room/object footprints, portals, paths, nodes, service points, safety paths, counts, save equality |
| Recorded for later runtime | Narrative identity, environmental presentation, selection volumes, occlusion art groups, story reveals, detailed audiovisual state |
| Provisional pending graybox | World scale, path-to-time mapping, occupancy limits, camera bounds, touch padding, gesture thresholds, congestion cost |

The model proves logical consistency and can reject invalid layouts. It does not prove camera comfort, mobile tactility, resident movement quality, visual readability, or device performance.
