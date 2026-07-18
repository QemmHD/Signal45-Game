# 25 — NAVIGATION AND LAYOUT EFFECTS

**Stage:** Prompt 4. **Status:** LOCKED at structural level; values PROVISIONAL (D-046). The navigation model is executable: `tools/spatial_model.py` walks the same cells the layouts are saved in.

---

## 1. The navigation model

A **cell-graph hybrid**: within a section, residents path over walkable cells (4-neighbor BFS — the same cells placement uses, per 21 §1's no-divergence rule); between sections, travel crosses **portal and vertical-link edges** (entries, stairs, ladders, the lift), each gated by state (open/closed/blocked/jammed/operational) and, for the airlock, by door state. The graph understands: closed doors · isolated sections · hazards (a hazard closes its cells or its portal) · flooding (the West Gallery is unpathable until drained) · structural closure (an unstable bay closes access — 18 §5) · occupancy (destination reservation) · work destinations (interaction cells) · temporary construction obstacles (an active site's cells) · evacuation targets (safe areas + the muster point) · vertical travel · lift availability · resident restrictions (a barred resident refuses hazard cells — 17 §2).

**Resident movement rules:** destinations reserve their interaction cell (no permanent overlap — two residents queue, never stack); access changes trigger repath; a blocked route degrades gracefully (wait → repath → abandon task with a *named* reason: "Teo can't reach the bench — the aisle is barricaded"); teleporting never occurs in normal behavior (interruption rewinds are save-semantics, not movement); threatened rooms evacuate to the muster point or nearest safe area. Failed access always self-explains in the task's own words — the same anti-lie rule as materials.

**Placement warnings (validator-enforced, 24 §5):** before confirming anything that blocks the only path, a required interaction point, emergency access, a utility service point, or vertical circulation, the player is warned with the specific consequence — and the two severe classes (sever-shelter, strand-equipment) demand explicit confirmation or are refused.

## 2. Travel time (matters, never dominates)

Base walk ~1 cell/sim-minute at Normal (PROVISIONAL); vertical costs: stairs ×2 per level, ladder ×3, lift ×1 but queued and failable; carrying ×1.5 (hauling); injury per condition card; congestion adds queue delay at portals only (no per-cell crowd sim); door delays only at state-gated doors. Layout strategy comes from **summaries, not meters**: rooms report *good access · long route · congested · no emergency path · far from storage · isolated* — the advanced inspect layer holds actual path details. Route caching is an engine concern recorded for R-15, not design surface.

**Honesty boundary (binding):** the feasibility model's 0.85 efficiency factor is where travel/interface overhead currently hides (15 §1); **no precise travel numbers are retrofitted into it**. First-playable revalidation gates (new, D-046): measured average resident travel share, material-hauling overhead, vertical-navigation delay, portal congestion frequency, hauling-trip counts, and build-session interaction time — any of these diverging >20% from the model's implied overhead forces re-derivation of the efficiency factor (the D-041 trigger pattern).

## 3. Adjacency effects (nine, closed list, all visible)

The slice's meaningful adjacencies — each previewed before confirm, iconed afterward, explained in words, and reversible through ADAPT: **storage↔workshop** (hauling distance — the metrics' storage-to-work path) · **medical↔gate** (emergency treatment distance — entrance-to-medical path) · **rest↔noisy utility** (the canonical railcar/Flywheel sleep tension, mandatory slice content) · **food↔contaminated water link** (contamination vector, 19's incident) · **air module↔affected branch** (response quality) · **second passage** (evacuation alternates — the emergency-path metric) · **security barrier↔gate** (intrusion response, full game, D-044-compatible) · **community↔private sleep** (noise, full game) · **backup charge↔critical room** (the battery-bank object extends a room's emergency operation). **No hidden percentages:** every effect is a physical fact a player can see (a path, a noise source, a pipe link) — never an unexplained +5%.

## 4. Incidents and layout (section/adjacency propagation, no fluid sim)

Layout answers incidents exactly as Prompt 3 specified, now with executable geometry: closing a door slows air contamination (portal state gates the 3-phase degrade's spread); a second route prevents entrapment (emergency-path alternates); a local battery protects a clinic (backup-charge adjacency); the drain channel protects lower rooms (flood propagates along authored channels, not simulated water); a reinforced bay halts structural spread (18 §5); an isolated branch stops electrical propagation (CONNECT's isolate verb); storage siting changes emergency delivery distance (metrics). The Prompt-3 cascade gains its layout hooks: the seal-bulkhead choice decides which side of the station the storm's air spread threatens, and shedding order is visible room by room (comfort lighting dims first — by location, not abstractly).

## 5. Debug and validation requirements

The validator's checks are the debug surface's spec: path/reachability queries per room, emergency-path + alternates per room, metrics (average path, longest essential path, storage→work, entrance→medical), and the no-sever/no-strand guards. First playable must expose the same queries live (a path-debug overlay behind a developer flag). **None of these proxies prove gameplay feel** — they prove the station cannot be broken by placement.
