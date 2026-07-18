# 24 — MOBILE BUILD INTERFACE

**Stage:** Prompt 4. **Status:** LOCKED at interaction-grammar level; pixel values are design targets for the UI stage (D-046). Extends 09 A.6/A.9 and 10 §16 — those rules stand; this document completes them.

---

## 1. The five workflows (the only top level, verbatim contents)

**RECLAIM** — survey · clear · drain · reinforce · remove hazard · salvage. **CONNECT** — open passage · restore door · restore stairs/ladder · restore lift · extend section access · connect utility node · isolate branch. **BUILD** — room blueprint · equipment · furniture · partition · door (where valid) · utility module · decoration. **OPERATE** — staff · priority · supply · repair · maintenance · utility priority · room policy. **ADAPT** — upgrade · add module · specialize · move equipment · repurpose · store · deconstruct. Only contextually legal commands appear (a blocked section shows RECLAIM; a functional room shows OPERATE/ADAPT); the sixteen internal verbs are never a flat vocabulary (07 §17 audits). Verb cards stay two-tier: 2–4 ranked actions + the "all works…" expander; Repurpose/Deconstruct ≤ 2 taps from any built room's card.

## 2. Screen regions (landscape, both thumb zones)

Top edge: resource HUD + clock (suppressed in full-screen allocation views). Left thumb corner: crew strip. Right thumb corner cluster: build-lens toggle · engineer's-overlay toggle · zoom button. Bottom center-right: the **workflow bar** (build lens only — five buttons, the lens's mode frame anchors it). Context panel: slides from the right on selection (never covers the selected object); confirm/cancel pinned to its bottom corners, ≥ 48 dp, cancel always left of confirm. Simulation controls (pause/speed) top-right under the clock. All interactive chrome inside platform safe areas; the lens's fixed exit affordance in the named right corner (10 §16).

**Design-target viewports:** 844×390 and 932×430 (primary), tablet landscape (relaxed), with 390×844 / 430×932 portrait showing the friendly rotate-device card (portrait remains cut — 03). Minimum targets: **48 dp primary / 28 dp secondary, ≥ 8 dp spacing** (09 A.6's platform-neutral spec, unchanged); every build-lens target ≥ 48 dp at every zoom where it is live (overview = section-granularity only).

## 3. Gesture separation (the pan-vs-drag contract)

- **Camera pan**: drag starting on empty world or any unselected target. **Pinch**: zoom (button alternative).
- **Object drag**: only from a *selected* ghost/object's body or its move handle — selection first, drag second; there is no drag-from-cold.
- **Threshold rule:** a touch becomes a drag only after ~24 dp of travel; under that it resolves as a tap on release. A drag that begins as pan never converts to placement, and vice versa.
- **Placement is tap-first with drag assist** (10 §16): footprint chips → auto-proposed ghost → tap affordances shift/flip → confirm. Rotation: a dedicated rotate button on the ghost (90° steps) — never a gesture.
- **Undo**: one-step undo of the latest *planning* action (ghost move, rotation, blueprint save) lives on the context panel; committed work is never gesture-undone (it cancels through the ledger rules, 23 §3).
- Accidental-placement guards: no commit without the explicit confirm tap; the monkey test cannot issue a construction order from normal mode (07 §17); destructive actions (deconstruct, repurpose) always confirm with their cost quoted.

## 4. Selection and readability

Enlarged invisible hit areas (object hit box ≥ 48 dp regardless of sprite size); **selection cycling**: a second tap on an overlapping stack cycles candidates; when ≥ 3 targets overlap, a small **target chooser** (chips: room / object / resident) appears instead of guessing. Priority order: active-incident target > current mode's type (build lens: bays/rooms; normal: residents/rooms) > nearest interaction point > smallest target. Tap-and-hold = inspect-without-selecting (the 25%-slowdown inspection tier, 11 §3). Selected entities get outline + card; a center-camera chip sits on the card. Layer filtering: the overlay selector doubles as a tap-priority filter in dense areas. No pixel-perfect taps anywhere (07 §17's monkey + audit gates).

## 5. Invalid placement (specific reasons, always)

A rejected ghost states its reason in words, from the validator's own vocabulary: "outside a buildable zone" · "overlaps fixed architecture (column)" · "would block a stair/lift/portal cell" · "no clear working side" · "sticks out of its room" · "needs power — trunk east is dark (CONNECT first)" · "below the family's minimum size" · "module must touch its parent" · "would cut off [facility] — severe confirmation required" · "would strand [object] — its every working cell goes dark." The last two are the *warned-severe* class: the first is refused outright in the slice; the strand warning demands explicit confirmation with the recovery verb named. Reasons render as text + icon (color-free channel), and the offending cells flash shape-coded.

## 6. Utility preview and overlays

The Power/Air/Water/Structure overlays and their selector follow 18 §7 (worst-warning default, badges persist, build-lens cross-family capacity summary). The BUILD ghost's utility preview answers, before confirm: can it connect · expected demand · remaining headroom · which branch serves it · what sheds first (**comfort lighting, by name — the teaching moment**) · whether backup exists · what expansion is required. No wires, ever.

## 7. Interruption and resume

The build lens obeys the global interruption contract (12 §3): backgrounding mid-placement saves the ghost as a suspended plan; reopening restores it exactly; auto-pause-tier events pause the sim under the lens and present on exit (11 §3.2). A mid-drag interruption resolves as no-op (the ghost returns to its last confirmed cell). Nothing in build mode ever commits without the confirm tap having been the last input.

## 8. Accessibility

All invalid reasons in text (§5); placement states (valid/invalid/suspended) differ by shape + pattern, not color alone; reduced-motion disables ghost pulsing and camera glides; selection cycling replaces precision; no timed placement exists anywhere; every drag has a tap alternative (09 A.6). The build lens inherits the 130%/200% scaling gates and the muted-play requirement (07 §19).
