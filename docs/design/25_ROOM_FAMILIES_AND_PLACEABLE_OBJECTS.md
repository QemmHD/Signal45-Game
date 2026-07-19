# Signal 45 — Room Families and Placeable Objects

Status: Prompt 4 reusable spatial architecture. The vertical slice uses exactly seven room families; the full-game 20–24 figure remains a ceiling, not a target.

## Functional-area semantics

- **Area:** one physically identifiable, usable station bay or shell.
- **Room family:** reusable simulation behavior such as Rest or Medical.
- **Room instance:** one placed or adapted implementation of a family.
- **Function:** a capability supplied by a room or equipment.
- **Equipment:** a functional object with footprint and interaction points.
- **Module:** a bounded attachment to a valid parent socket.
- **Upgrade:** a state improvement to an existing instance.
- **Specialization:** a meaningful direction within one family.
- **Temporary zone:** a provisional capability inside an existing area.

Area count is derived from operational room instances and unique `physical_area_id` values. A triage cot inside Platform Camp supplies Medical functionality but does not create another physical area. A repurpose changes function without incrementing the count. An upgrade adds an area only when it makes a separately bounded shell usable.

The executable correction to Prompt 3 is therefore:

- `triage_cot_install`: temporary Medical function, no area increment;
- `concession_repurpose`: same concession area, no increment;
- route utility connection: makes one distinct route area usable;
- `triage_upgrade`: makes one distinct treatment area usable.

Competent East and West still derive ten areas.

## Seven room families

| Family | Purpose | Temporary form | Permanent form | Typical footprint | Required access/utilities | Slice development |
|---|---|---|---|---|---|---|
| Rest | Sleep, Fatigue recovery, quiet recovery | Bedroll camp | Bunks or quiet berths | 1–3 bays | Walk path; Air | Capacity, privacy module, quiet specialization |
| Medical | Examine, stabilize, treat, observe | Triage cot or gate zone | Treatment room | 1–3 bays | Patient-compatible path, Water; optional Power | Cot → treatment bench; respiratory/arrival specialization |
| Food | Issue and share meals | Ration table | Repurposed concession point | 1–2 bays | Walk path; storage access | Cold issue → shared-meal point |
| Storage | Reserve stocks and component delivery | Crates/cabinet | Fitted stores | 1–2 bays | Material-carry path | General, medical, or Water-service specialization |
| Utility | Shared shell for Power, Air, Water, Structure support | Service rack/module | Source, treatment, reserve, or control bay | 1–3 bays | Service path and correct branch | Power/Air/Water specialization without new families |
| Workshop | Repair, fabrication, project preparation | Tool station | Workbench bay | 1–2 bays | Material path; Power optional/normal | Mechanical or pump-service specialization |
| Operations | Listening, forecasts, coordination | Improvised relay kiosk | Forecast/relay room | 1–2 bays | Walk path; Power essential when active | Forecast Board and later relay specialization |

Each family definition includes compatible section types, supported footprints, resident and socket capacity, interaction points, noise/environment/comfort/medical effects, incident interactions, generated work, construction and damage states, upgrade and specialization paths, and save representation.

## Room acceptance rules

A room instance is valid only when:

- every footprint cell exists and is buildable or an explicitly authored machinery shell;
- it does not overlap another counted physical room;
- its family is compatible with the section type;
- required access and at least one interaction point are reachable;
- required utility nodes and service paths exist;
- it does not reserve or block an essential portal or evacuation path;
- its camera focus contract is present;
- its physical area is counted once.

Temporary zones may overlap a parent area only when explicitly marked and never silently add area count.

## Object behavior families

The slice reuses these behavior families: `workstation`, `rest_point`, `medical_point`, `storage`, `utility_module`, `lighting`, `barrier`, `access_control`, `comfort`, `emergency_equipment`, `decoration`, and `story_object`.

The catalog is intentionally bounded. Representative objects are the Platform Work Lamp, bedroll, quiet bunk, triage cot, medical bench, ration/meal table, storage cabinet, service rack, forecast board, workbench, reserve tank, treatment skid, pump console, isolation controls, battery control, emergency cabinet, repaired sign, repair brace, and temporary barrier.

Every object definition provides:

- ID, display name, behavior family;
- footprint, rotation options, and anchor rule;
- occupied, interaction, approach, and clearance cells;
- blocking rule and carry class;
- utility requirement and compatible rooms/sections;
- socket requirement and module capacity;
- use behavior and capacity;
- construction class, Materials cost, and component blocker;
- upgrade, damage, storage, and bounded deconstruction states;
- selection bounds, Room Focus target, and save fields.

Decorations do not each receive bespoke simulation. A story object can hold identity without becoming a new production system.

## Modules

A module stores its parent type and instance, socket type, adjacency or utility requirement, capacity effect, visual effect, state, uniqueness, and save representation. The validator rejects:

- a missing, stored, or destroyed parent;
- a module parented to another module;
- placement outside parent bounds where adjacency is required;
- an incompatible or full socket;
- duplicate unique modules;
- benefits remaining after parent destruction.

The Platform Lighting Upgrade attaches to the Platform Work Lamp’s `lighting_upgrade` socket. It changes fixture geometry, warmth, and comfort presentation but adds no second Power consumer.

## Player freedom proof

East and West each have canonical and alternate Day 7 layouts. Alternates move multiple functional rooms and equipment—not decoration—while preserving seven families, ten areas, essential access, utility service, evacuation, and route identity. The `poor_valid` layout deliberately lengthens Materials trips yet remains legal. This demonstrates flexible interior adaptation inside the same authored railway shell.

## Scope ceiling

Prompt 4 does not add freehand walls, unlimited excavation, user-drawn wires or pipes, advanced decoration mode, dozens of furniture behaviors, exterior construction, direct resident control, combat pathfinding, final art, or another station map. Every additional object later must justify its code, art, animation, audio, UI, localization, and test cost.
