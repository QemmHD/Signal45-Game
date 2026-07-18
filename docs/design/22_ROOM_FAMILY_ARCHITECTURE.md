# 22 — ROOM FAMILY ARCHITECTURE

**Stage:** Prompt 4 (amended by the D-048 red-team pass). **Status:** LOCKED at structural level; family values PROVISIONAL in `tools/data/room_families.json` and `placeable_objects.json` (D-047). Schema fields the validator executes vs. records-for-later are listed honestly in 21 §7.

---

## 1. The vocabulary (one ladder, eight terms)

- **AREA** — a named functional location the player counts ("8–10 areas by Day 7"). An area is a room instance *or* a temporary zone; areas are presentation, not systems.
- **ROOM FAMILY** — a foundational simulation system (schema, work tasks, risks, save shape). The scarce resource; everything below rides on one.
- **ROOM INSTANCE** — a placed room of a family: footprint + form + state + equipment.
- **EQUIPMENT** — socketed placeable objects (beds, benches, pumps) carrying the actual behavior via **nine object behavior families** (workstation · rest point · storage · utility module · comfort object · barrier · decoration · emergency object · story object) — objects are data, behavior families are code.
- **MODULE** — a bay-adjacent extension of an existing instance (the Expand verb; pantry onto Canteen, filtration onto Cistern Works). Must touch its parent, and the parent must be a full instance — **module chains are refused** (validator-enforced, D-048); never a separate system.
- **SPECIALIZATION** — a committed sub-role within a family (utility→power/air/water; operations→listening post/staging; storage→cold/equipment).
- **UPGRADE** — a tier change within an instance (improvised→wired LP; partial→stabilized Flywheel; bedroll→bunk→berth).
- **TEMPORARY ZONE** — a family instance without a shell (the Camp's bedroll ring, the cook ring, supply stacks). Same family, lower quality, zero construction ceremony — and the reason Day 1 has four *areas* on two-ish real systems.

## 2. The seven slice families (and why not eight)

**REST · MEDICAL · FOOD · STORAGE · UTILITY (power/air/water specializations) · WORKSHOP · OPERATIONS (listening post/staging specializations).** The suggested POWER/AIR/WATER triple is one family: machine rooms share their whole pattern (equipment sockets, maintenance tasks, noise, low occupancy, cascade participation) and differ only in what the utility module produces — three foundational systems there would be theater. RADIO/OPERATIONS absorbs the Staging Room (both are "infrastructure the station thinks with"). Every full schema field mandated this stage (footprints, architecture, utilities, capacity, sockets, access rules, tasks, outputs, risks, noise, heat, comfort, medical, incidents, upgrade path, specializations, temporary/permanent forms, damage states, visual stages, save, acceptance) is in `room_families.json`.

**Slice arithmetic:** Day 7's 8–10 areas decompose as — east: rest (Sleeper Car) + medical (Aid Car) + food (Canteen+pantry) + storage (Cold Store, Equipment Locker) + utility (Gate, Flywheel) + workshop (Fitters') + operations (LP, Staging) = 10 areas, 7 families; west: medical becomes the **triage-bench corner beside Staging** (temporary — the D-039 bench venue, in the layout data with its placed bench), food becomes the canteen corner (temporary), the Aid Car and Equipment Locker drop out, and utility/water ×2 arrive (Cistern Works+filtration, Pump Room) = 10 areas, 7 families. **Areas ≠ systems — proven by construction and validator-asserted on both routes (a medical venue with treatment equipment is a Day-7 battery check, D-048).**

## 3. The full-game target: 22 families (from ~40 rooms)

The 10 §6 catalog maps onto **22 families** (list in config): the slice seven + farm · fabrication · recycling · community · education · family quarters · memorial · sanitation (if earned, 16 §1) · quarantine · climate · structure · security (D-044-compatible) · trade · signals analysis · circulation (CONNECT's domain, not a buildable room). Every catalog room is an instance or specialization — the Long Table is community, the Spore Beds are farm, the Isolation Berth is quarantine. **Forty independent room systems is formally retired (D-047)**; a new room type in production costs an instance definition (data + art), not a system.

## 4. Object behavior families (nine, closed for the slice)

All simulation logic lives in the nine families (§1); `placeable_objects.json` defines ~26 slice objects as pure data: footprint, interaction cells, blocking, rotation, utility requirement, room compatibility, restrictions, upgrade/damage states, store/deconstruct results, save shape. Adding an object never adds *behavior* code — and the restriction vocabulary is honest about enforcement (D-048): hard restrictions (placement anchors, section locks, carer clearance, never-deconstruct, and the reachability pair `must_stay_reachable`/`never_seals_last_path` — executed globally by the flood-fill guard) run in the validator; three advisory strings (`not_against_interaction_side`, `wants_partition_adjacent`, `open_zone_ok`) are UI hints, labeled as such in the config. Socket budgets are enforced (behavior family must be socketed; storage counts against `storage_sockets`). Story objects (the kiosk chalk, the shift log — placed in both Day-7 layouts — and the timetable board) are placeable anchors for 10 §15's authored reveals and can never be deconstructed (executed). **Defaults carry the player:** every room ships working defaults (auto-assigned staff, auto-proposed footprints, sane priorities); configuration is optional depth, never a toll.

## 5. Temporary → permanent (the growth grammar)

The Camp *is* the tutorial for this: bedroll ring (rest, temporary) → Sleeper Car / west bunks (rest, permanent) → the Camp repurposes to Staging (operations). Temporary zones cost placement only (0 WU task class); permanent forms take the construction flow (23); quality differences are mechanical (rough-sleep pricing already in the labor model, bench-vs-Aid-Car penalty in 17). The housing ladder (bedroll→bunk→berth) is an object upgrade path, not new rooms.

## 6. Scope controls

No room family ships without: a temporary or found-architecture form, ≥2 interactions from the 10 §7 functional vocabulary, a damage-state set, and a visual-stage delta. The slice adds **zero** families beyond the seven; the full game adds families only at stage gates with this document amended. Anti-pillar 6's spam test applies per instance: a room whose connections to utilities/access/behavior/structure/human ledger could be deleted without change does not ship.
