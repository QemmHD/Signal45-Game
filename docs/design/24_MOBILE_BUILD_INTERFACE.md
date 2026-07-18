# 24 — MOBILE BUILD INTERFACE

**Stage:** Prompt 4. **Status:** LOCKED at interaction-grammar level; pixel values are design targets for the UI stage (D-046). Extends 09 A.6/A.9 and 10 §16 — those rules stand; this document completes them.

---

## 1. The five workflows (the only top level, verbatim contents)

**Workflow-bar behavior (D-048):** tapping a workflow filters the context panel to that workflow's commands for the current selection (second tap deselects; the active workflow underlines); the bar never places anything itself — commands still flow through verb cards and ghosts, so there is exactly one interaction grammar. Two previously-undefined OPERATE commands, defined: *room policy* = a room's standing defaults (door state, access, priority tier) on one card; *utility priority* = the load-board shortcut for the selected room's load class. The five workflows surface ~30 contextual sub-commands built from the sixteen internal verbs — a filter, not a new vocabulary. **BUILD additionally carries "Start construction"** — the blueprint card's committing verb (23 §2): the only tap that spends.

**RECLAIM** — survey · clear · drain · reinforce · remove hazard · salvage. **CONNECT** — open passage · restore door · restore stairs/ladder · restore lift · extend section access · connect utility node · isolate branch. **BUILD** — room blueprint · equipment · furniture · partition · door (where valid) · utility module · decoration. **OPERATE** — staff · priority · supply · repair · maintenance · utility priority · room policy. **ADAPT** — upgrade · add module · specialize · move equipment · repurpose · store · deconstruct. Only contextually legal commands appear (a blocked section shows RECLAIM; a functional room shows OPERATE/ADAPT); the sixteen internal verbs are never a flat vocabulary (07 §17 audits). Verb cards stay two-tier: 2–4 ranked actions + the "all works…" expander; Repurpose/Deconstruct ≤ 2 taps from any built room's card.

## 2. Screen regions (landscape, both thumb zones)

Top edge: resource HUD + clock (suppressed in full-screen allocation views). Left thumb corner: crew strip. Right thumb corner cluster: build-lens toggle · engineer's-overlay toggle · zoom button. Bottom center-right: the **workflow bar** (build lens only — five buttons, the lens's mode frame anchors it). Context panel: slides from the right on selection (never covers the selected object); confirm/cancel pinned to its bottom corners, ≥ 48 dp, cancel always left of confirm. Simulation controls (pause/speed) top-right under the clock. All interactive chrome inside platform safe areas; the lens's fixed exit affordance in the named right corner (10 §16).

**Design-target viewports:** 844×390 and 932×430 (primary), tablet landscape (relaxed), with 390×844 / 430×932 portrait showing the friendly rotate-device card (portrait remains cut — 03). Minimum targets: **48 dp primary / 28 dp secondary, ≥ 8 dp spacing** (09 A.6's platform-neutral spec, unchanged); every build-lens target ≥ 48 dp at every zoom where it is live (overview = section-granularity only). **Small sections get enlarged invisible hit areas** (D-048): the Signal Box's drawn footprint sits under 48 dp at overview — its hit area expands to the floor, with the §4 chooser resolving any overlap the expansion creates. No drawn size is ever the tap contract; the hit area is.

## 3. Gesture separation (the pan-vs-drag contract)

- **Camera pan**: drag starting on empty world or any unselected target. **Pinch**: zoom (button alternative).
- **Object drag**: only from a *selected* ghost/object's body or its move handle — selection first, drag second; there is no drag-from-cold.
- **Threshold rule (movement AND time — D-048):** a touch becomes a drag after ~24 dp of travel; a still touch held ≥ ~350 ms becomes tap-and-hold (inspect); under both thresholds it resolves as a tap on release. A drag that begins as pan never converts to placement, and vice versa. Tap-and-hold is a **bonus affordance** (09 A.6 amended): everything it does is also reachable by tap → card → inspect.
- **Placement is tap-first with drag assist** (10 §16): BUILD → **object/family picker** (a short list card — the picker is a counted step) → auto-proposed ghost → tap affordances shift/flip → confirm. Rotation: a dedicated rotate button on the ghost (90° steps) — never a gesture. **Tap budgets restated honestly (D-048):** a small install is ≤ 3 taps *from the open BUILD context* (picker → place → confirm) and ≤ 5 from overview including lens entry and workflow; the full room blueprint stays ≤ 6 including lens entry and Start.
- **Undo**: one-step undo of the latest *planning* action (ghost move, rotation, blueprint save) lives on the context panel; committed work is never gesture-undone (it cancels through the ledger rules, 23 §3).
- Accidental-placement guards: no commit without the explicit confirm tap; the monkey test cannot issue a construction order from normal mode (07 §17); destructive actions (deconstruct, repurpose) always confirm with their cost quoted.

## 4. Selection and readability

Enlarged invisible hit areas (object hit box ≥ 48 dp regardless of sprite size); **selection cycling**: a second tap on an overlapping stack cycles candidates; when ≥ 3 targets overlap, a small **target chooser** (chips: room / object / resident) appears instead of guessing. Priority order: active-incident target > current mode's type (build lens: bays/rooms; normal: residents/rooms) > nearest interaction point > smallest target. Tap-and-hold = inspect-without-selecting (the 25%-slowdown inspection tier, 11 §3). Selected entities get outline + card; a center-camera chip sits on the card. Layer filtering: the overlay selector doubles as a tap-priority filter in dense areas. No pixel-perfect taps anywhere (07 §17's monkey + audit gates).

## 5. Invalid placement (specific reasons, always)

A rejected ghost states its reason in words, in 1:1 correspondence with the validator's error classes (D-048 — this list is the complete current placement-rejection set, kept in sync with `spatial_model.py`; internal IDs and raw coordinates never render): "outside a buildable zone" · "those cells are occupied" · "overlaps fixed architecture (column)" · "would block a stair/lift/portal cell" · "no clear working side" · "its working side would be unreachable" · "does not belong in this room" · "no socket of that kind / storage sockets full" · "sticks out of its room" · "needs power — the trunk is dark (CONNECT first)" · "below the family's minimum size" · "module must touch its parent / not another module" · placement-anchor restrictions in their own words ("must sit beside the tank", "interior only", "portal or partition gap") · **"refused: would cut off [facility] — open another route first"** · **"refused: would strand [object] — its every working cell goes dark."** The last two are the severe class, and the slice policy is uniform (D-048): **both are refused outright with the recovery named** (CONNECT/ADAPT); a full-game severe-confirm override is a later-stage decision. Reasons render as text + icon (color-free channel); offending cells mark shape-coded (a static hatch under reduced motion — no flashing).

## 6. Utility preview and overlays

The Power/Air/Water/Structure overlays and their selector follow 18 §7 (worst-warning default, badges persist, build-lens cross-family capacity summary). The BUILD ghost's utility preview answers, before confirm: can it connect · expected demand · remaining headroom · which branch serves it · what sheds first (**comfort lighting, by name — the teaching moment**) · whether backup exists · what expansion is required. No wires, ever.

## 7. Interruption and resume

The build lens obeys the global interruption contract (12 §3): backgrounding mid-placement saves the ghost as a suspended plan; reopening restores it exactly; auto-pause-tier events pause the sim under the lens and present on exit (11 §3.2). A mid-drag interruption resolves as no-op (the ghost returns to its last confirmed cell). Nothing in build mode ever commits without the confirm tap having been the last input.

## 8. Accessibility

All invalid reasons in text (§5); placement states (valid/invalid/suspended) differ by shape + pattern, not color alone; reduced-motion disables ghost pulsing, camera glides, and invalid-cell flashing (static hatch instead); selection cycling replaces precision; no timed placement exists anywhere; every drag has a tap alternative (09 A.6). **Build-feel reserve (D-048):** three feedback moments are reserved line items inside the existing ~20-SFX budget — the ghost-confirm chalk strike, the stage-completion tick, and the portal-opening rumble — placement must feel like *doing*, not admin. The build lens inherits the 130%/200% scaling gates and the muted-play requirement (07 §19).
