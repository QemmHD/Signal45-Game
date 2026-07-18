# 21 — SPATIAL AND STATION MODEL

**Stage:** Prompt 4. **Status:** LOCKED at structural level; geometry values PROVISIONAL in `tools/data/station_sections.json` (D-046). Validation: `tools/spatial_model.py` + `tools/validate_station_layouts.py` + `tools/test_spatial_model.py` (64 checks).

---

## 1. One logical source of truth: SECTION → BAY → CELL

The station is addressed by exactly one coordinate model, chosen as a **bay-anchored coarse cell grid** (the hybrid of D-038's structural bays and a logical grid):

- **Section** — the authored unit of reclamation (10 §2): platforms, galleries, vaults, the signal box. Each carries the full schema mandated this stage: id, display name, story identity, world origin + level, grid size, bays, fixed architecture, buildable zones, entries, vertical links, utility node, initial hazards, reclamation class/requirements, max occupancy, environment (noise/temperature/air), camera framing, unlock condition, and story reveal — all in `station_sections.json`.
- **Bay** — the span between roof columns (~6 m), **4 cells wide**: the atomic *construction* unit. Bays are derived from the grid (columns are fixed cells), not a second coordinate system.
- **Cell** — ~1.5 m square, section-local `[x, y]`: the atomic unit of **placement, footprints, furniture, interaction points, navigation, hazard propagation, and save data**. World position = section origin + level elevation; nothing stores world coordinates.

**Why this over the alternatives:** pure navigation polygons put placement and save data in float space (fragile on mobile, awkward to validate); pure socketed zones kill the interior freedom Pillar 6 promises; a fine grid invites pixel-fiddling that phones punish. The coarse bay-anchored grid gives reliable tap-sized targets (a cell at room zoom comfortably exceeds the 48 dp floor), exact save semantics, cheap validation, and honest footprint variety.

**The no-divergence rule (binding):** visual placement, collision, room ownership, utilities, navigation, and save data all reference section/cell addresses. A future renderer converts cells to world transforms *at draw time* (origin + level + cell × size) and persists nothing of its own; navigation runs on the same cells (§25); the save file stores the layout dict the validator round-trips today. Conversion boundaries the engine will own: cell→world transform, camera framing per section (`camera_bounds`), and interpolation of residents *between* cells — presentation only, never authority.

## 2. Fixed architecture in data

Fixed features carry `walkable_when`: **never** (columns, track beds, the cistern main, machine housings — neither walkable nor buildable), **always** (decon channel, cable gallery — walkable circulation, unbuildable), **open** (the airlock doors — state-gated), **interior** (convertible shells: railcars, kiosks, the fitters' bay — walkable *and claimable by rooms*, the found-architecture conversion rule of 10 §5). Buildable zones declare `except_fixed`: shells count as buildable where a section's identity is conversion (the East Concourse), and hard architecture never does.

## 3. Vertical structure and links

Three levels (upper / platform / service vaults — 09 B.1's one-screen composition). Vertical links are first-class data (stair, ladder, lift) with their own cells on both ends and a state (`operational` / `jammed` / `closed`); the freight lift is the slice's gated link (jammed until the Depot-9 tools + Connect order — 10 §15). Link cells are protected: no blocking object may ever occupy one (validator-enforced).

## 4. The slice complex (eight sections)

Scrubber Gate (upper; airlock + decon; the only surface door) · Central Platform (the Camp's home; 4 bays; both blocked portals; the muster point) · Signal Box (elevated; the Listening Post's found home) · Flywheel Vault (service level; the noisy heart) · East Concourse (4 bays; two railcar shells + kiosk row; behind rubble) · West Gallery (4 bays; cistern main + arch hotspot; flooded) · Deep Service (fitters' bay + parts racks; behind the jammed lift) · plus the surface entry itself. Trunks: `trunk_core` (live Day 1) serving gate/platform/signal/flywheel/deep nodes; `trunk_east` / `trunk_west` dark until extended (a CONNECT works order, 6 WU + 3 materials — PROVISIONAL, from the labor model's trunk cost).

## 5. Enforcement honesty (what the validator executes vs. records)

D-048's boundary, stated plainly: the validator **executes** buildable zones, fixed-architecture collision (overlapping fixed features are a load-time error — silent shadowing is impossible), link-cell protection, object overlap, interaction clearance and reachability, room compatibility and socket budgets, module attachment (no chains), feature anchors, trunk service, hard placement restrictions, door/portal/link state navigation, the no-sever/no-strand flood-fill guard, and the reservation ledger. It **records for later stages** (data present, consumed by design prose and future systems, not by checks): bay counts as narrative structure (bays derive from column cells), environment temperature, camera frames, max occupancy, damage-state ladders, and reclamation labor forecasts (the labor model owns labor arithmetic). Docs may cite recorded fields as design intent, never as validated facts.

## 6. Save representation

One layout dict (rooms with their area labels, objects, portal/link/trunk/door states — placed doors carry open/closed state, the seal bulkhead records its portal — berth assignment) — the same object the validator loads, mutates, and round-trips (`test_layout_save_reload_roundtrip_and_after_move`). Partial construction saves as ledger state (project stage fractions — §23); both round-trip through JSON byte-identically. This slots into the single world-state object (R-10) unchanged.

## 7. Engine requirements recorded (for the selection stage, R-15)

Cell-addressed 2.5D placement over authored section data; per-section camera framing; three-level parallax composition; state-gated portal/link traversal; ≤ 20 agents pathing on cell graphs (trivial scale); layout serialization identical to this model's dict. Nothing here demands a specific engine; everything here is testable without one.
