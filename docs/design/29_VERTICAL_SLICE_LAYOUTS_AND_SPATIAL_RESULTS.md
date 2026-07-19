# Signal 45 — Vertical-Slice Layouts and Spatial Results

Status: Prompt 4 machine-data results. Generated diagrams are authoritative views of JSON, not separately maintained plans.

## Generated layouts

- [Day 1 diagram](../../tools/spatial/reports/diagrams/day1.md)
- [East Day 7 diagram](../../tools/spatial/reports/diagrams/east_day7.md)
- [East alternate diagram](../../tools/spatial/reports/diagrams/east_day7_alternate.md)
- [West Day 7 diagram](../../tools/spatial/reports/diagrams/west_day7.md)
- [West alternate diagram](../../tools/spatial/reports/diagrams/west_day7_alternate.md)
- [Utility topology](../../tools/spatial/reports/diagrams/utility_topology.md)
- [Emergency routes](../../tools/spatial/reports/diagrams/emergency_routes.md)
- [Camera focus regions](../../tools/spatial/reports/diagrams/camera_focus_regions.md)

## Day 1

Derived physical areas: **4**. Active families: Rest, Operations, Utility, Storage.

The Main Gate connects to the Central Platform. Platform Camp, Relay Kiosk, Service Alcove, and Concession Cage are the four physical areas. The triage cot supplies temporary Medical capability inside the camp and adds no area. The Platform Work Lamp, Food/Water access, starting storage, Power source, Air filter, Water equipment, safe area, blocked East/West portals, sealed vertical route, trunks/nodes, camera bounds, occlusion and selection regions are all explicit.

## East Day 7

Derived physical areas: **10**. Families: all seven.

The canonical layout retains the four central areas and adds central Workshop and Stores plus East entry Storage, treatment room, quiet berths, and utility/reserve room. It includes the Forecast Board, storm repair, gate stabilization, Juna berth state, Platform Work Lamp, reserve tank, isolation control, communal meal point, blocked West, and sealed vertical route.

Spatial identity:

- quiet Rest and primary Medical are close together;
- Rest-to-work is 3.0 logical cost;
- gate-to-primary-Medical is deliberately long at 28.8;
- gate stabilization remains 1.25;
- Water isolation is long at 21.6;
- canonical coordinate mapping is 8% travel and 4% hauling.

The alternate East layout moves Workshop, Storage, Rest, Medical, and utility arrangements inside the wing. It remains valid at ten areas/seven families but maps to 10% travel, showing a meaningful efficiency cost without invalidating player freedom.

## West Day 7

Derived physical areas: **10**. Families: all seven.

The canonical layout retains the central four areas and central Workshop, then opens the drained-access, pump, treatment, rough Medical, and Water-service Stores areas. Dedicated pump/treatment/storage/isolation nodes sit inside the gallery. It contains Forecast Board, storm repair, gate stabilization, Juna rough berth state, Platform Work Lamp, communal meal point, blocked East, and sealed vertical route.

Spatial identity:

- pump service is 6.0 and Water isolation 8.4;
- Materials delivery to Water work is 5.75;
- gate-to-Medical is 4.8;
- Rest-to-work is 7.0, with damp/noisy recovery;
- coordinate evidence is 8% travel and 4% hauling;
- the feasibility model conservatively retains 10% travel until a graybox measures damp-floor movement and congestion.

The alternate West layout moves primary Medical to the central platform, service Stores beside the pump, and Workshop to the gallery entrance. It remains valid while increasing gate-to-Medical to 19.2 and changing work/service routes.

## Metric summary

All values are logical-distance proxies, not seconds.

| Layout | Areas | Families | Avg | P95 | Longest essential | Materials | Heavy | Gate→Medical | Evacuation | Coord travel/haul |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Day 1 | 4 | 4 | 7.0 | 8.0 | 4.8 | 3.45 | 11.6 | 4.8 | 3.6 | 8% / 4% |
| East canonical | 10 | 7 | 7.0 | 12.0 | 28.8 | 11.5 | 34.8 | 28.8 | 9.9 | 8% / 4% |
| East alternate | 10 | 7 | 6.8 | 15.0 | 33.6 | 8.05 | 24.65 | 33.6 | 12.6 | 10% / 4% |
| West canonical | 10 | 7 | 7.6 | 13.0 | 10.8 | 5.75 | 8.7 | 4.8 | 9.0 | 8% / 4% |
| West alternate | 10 | 7 | 8.75 | 18.0 | 19.2 | 3.45 | 7.25 | 19.2 | 9.0 | 8% / 4% |
| Poor-valid East | 10 | 7 | 8.75 | 19.0 | 33.6 | 19.55 | 24.65 | 33.6 | 20.7 | 12% / 7% |

## Hope anchors

Every Day 7 layout contains an operational minimal anchor. The Platform Work Lamp can support a relit-platform beat; East also has quiet berths/reserve state, and West has the clean-water treatment skid. Full setup references the placed communal meal point. Anchors are earned project/object states, serialize with the layout, grant no stock, and clear no repair or treatment consequence.

## Travel integration

Coordinate travel replaces the abstract computation; the code selects either spatial factors or legacy factors, never both. East’s selected factors are 8% travel/4% hauling. West’s coordinate result is 8%/4%, but selected travel remains the previous conservative 10% until wet-surface and congestion measurement. The `poor_valid` result demonstrates that the mapping can increase burden.

No resident base capacity changed from 12 WU. No extra Day 5 project work was added. Prepositioning and project stages already represent heavy delivery, so heavy-carry distance has a bounded 20% weight in the hauling factor rather than being charged a second time.

## Feasibility rerun

- all **176** mandatory Prompt 2/3 scenarios match their expected outcome classes;
- competent East and West remain **Full Proof**, no Highball, ten areas;
- East/West common mistakes remain recoverable;
- prepared storm and all eight Juna cases retain expectations;
- Recover First remains distinct from proof failure after physical area semantics were corrected;
- Day 5 retains zero uncommitted WU and zero phase slack, with no hidden spatial WU.

Spatial validation: **6/6 layouts valid**. Spatial scenarios: **111/111 pass** and deterministic. Spatial unit tests: **71 pass**. Prompt 2/3 unit tests: **144 pass**.

## Invalid layouts and exploits rejected

The validator rejected column/track/outside-shell overlap, room/object overlap, blocked interactions, missing utility service, module chains/overflow, duplicate reservation/delivery/refund/completion, deconstruction profit, stranded residents/rooms, only-route and emergency-path blockage, unsafe portal closure, early vertical use, disconnected Charge backup, duplicate lighting loads, and save divergence.

The red-team pass also corrected an alternate-route metric that had counted irrelevant portals. It now counts only alternatives to portals used by the baseline evacuation path.

## Model limits

This proves geometry, access, topology, logical travel proxies, transaction/save consistency, and cross-model agreement. A playable graybox must still prove build tactility, selection comfort, camera comfort, actual travel seconds, congestion, resident avoidance, Room Focus readability, visual growth, device performance, and whether different layouts feel creatively satisfying.
