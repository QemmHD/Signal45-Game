# 23 — CONSTRUCTION AND RECLAMATION

**Stage:** Prompt 4. **Status:** LOCKED at structural level; costs PROVISIONAL (D-046). The reservation arithmetic is **executable**: `tools/spatial_model.py → MaterialsLedger`, asserted in `test_spatial_model.py` — the rules Prompt 3 could only state (20 §3B) now run as code at placement scale. The survival week still does not simulate cancels; first playable joins the two.

---

## 1. The RECLAIM workflow (per section, subset-based)

A section's reclamation uses the subset its data declares (never all steps): survey · debris clearing · drainage · contamination control · reinforcement · access restoration · hazard removal · utility isolation · occupant negotiation (full game) · salvage removal · story investigation. Every reclaimable section presents, from its survey report onward: the visible obstacle, known information, **unknown information (labeled unknown — 18 §8)**, forecast labor, required equipment/skill, materials, risks, potential capacity, utility access, possible salvage, possible human consequence, its story reveal, and at least one decision where the content supplies one (the east/west choice, the seal placement, drain-vs-plank).

**Project classes:** *minor clearance* (Scrubber Gate repair — one order) · *standard reclamation* (lift restoration — survey + connect, tools-gated, intel-discounted) · *major reclamation* (east breakthrough, west drainage — survey + clear/drain + reinforce + connect-utility, 12+ WU class) · *story-critical reclamation* (full game: the Annex — sealed from the inside). Slice set: **Scrubber Gate repair · east breakthrough · west drainage · lift restoration · the optional late Cold Store clearance** — exactly the recommended bound. Both routes run the same system foundations (same section schema, same works orders, same validator); only presentation and consequences differ (D-039's route-completeness canon).

Reclamation reveals **opportunity and history together**: each slice section's reveal (kiosk inventory, silt line, shift log) surfaces through the survey report and the clear/drain staging as an authored story-object anchor (22 §4).

## 2. Room creation (the 14-step flow, honestly divided)

Steps 1–7 (select area → choose family → preview footprint → preview access/utilities → preview sockets → review costs → confirm blueprint) are **immediate planning** — free, reversible, no reservation. Step 8 (reserve) is **automatic at activation**. Steps 9–12 (deliver → stages appear → equipment installs) are **resident-performed work** through the existing works-order system (11 §5's schema unchanged). Step 13 (operational) is automatic; step 14 (modules/upgrades/decoration) is optional later ADAPT work. **Small installations skip the ceremony** (D-040's task classes are binding): a bed, lamp, cabinet, or partition is a *placement* or *short install* — tap, ghost, confirm, a brief carry-and-install task; only projects and major reclamations use the full staged flow.

## 3. Blueprint mode and the reservation lifecycle (executable)

**Preview: no reservation. Saved inactive blueprint: no reservation. Activation: reservation. Delivered stage: reserved → consumed.** Cancel refunds the unconsumed reserve only (sunk stages and labor lost); deconstruct recovers 50% of consumed materials **once per component** and stores major equipment intact; duplicate activation is refused; stock can never go negative; the build→complete→deconstruct→rebuild loop strictly loses materials — all eight properties are asserted tests, not prose. Blueprints render ghost-styled (dashed, chalk-marked — 09's build lens grammar) and are visually distinct from active construction (crew + materials on site) and from completed rooms. Blueprint count is bounded per section (performance guard; UI shows the queue).

## 4. Construction stages (visible, staged, interruptible)

Full projects: blueprint markings → material delivery → structural framing → utility preparation → equipment installation → finishing → activation. Short installs: delivery → installation → activation. Furniture: placement + a brief resident move task. Major reclamations: several separate works orders (survey/clear/reinforce/connect — §1). The site always shows: assigned residents, delivered materials, remaining work in plain effort language (never WU — D-042), the current blocker (named — the anti-lie rule), priority, an estimate *without false precision* ("about a day", forecast-class projection), HIGHBALL availability, and unsafe-condition flags.

## 5. HIGHBALL in construction (presentation lock, D-047)

Available only on suitable *active* orders and utilities; the card names the resident/team, quotes benefit and overtime + promise-of-rest cost as facts and breakdown risk as a labeled uncertain %; the railway-signal audiovisual identity (green-lantern sweep, the Flywheel's rising note) makes it unmistakably different from a priority change; it cannot fire from a stray tap (distinct control + confirm); one per day enforced. **The exact timing multiplier stays provisional until first playable** — this stage locks presentation and constraints only (19 §5's verification boundary unchanged).

## 6. Repair, repurposing, and recovery from poor layout

Repair is one verb through the same works system (the Scrubber Gate storm order is the slice's proof). Repurpose keeps the shell, swaps incompatible equipment to storage (executable: `repurpose_room` displaces-and-stores, never destroys), and posts its two-sided price (person-phases + a visible human echo — 10 §9). The recovery guarantee stands and is now structurally tested: a bad placement is refused *before* it strands equipment or severs the shelter (the no-strand and no-sever guards); a bad *layout* is repairable through ADAPT (move/store/repurpose/deconstruct) at real, non-ruinous cost. One poor choice is never terminal; free thrash is priced.
