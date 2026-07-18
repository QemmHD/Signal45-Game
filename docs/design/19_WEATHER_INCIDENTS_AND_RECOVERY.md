# 19 — WEATHER, INCIDENTS, AND RECOVERY

**Stage:** Prompt 3. **Status:** LOCKED at structural level; schemas and values PROVISIONAL in `tools/data/incidents.json` (D-043).

---

## 1. Weather families

Full-game palette: swelter heat · cinder storm · still-air pressure · drainage surge · cold front · electrical storm · clear window. **Slice set (three):** swelter heat (the standing daytime condition), the **Day-4 cinder storm**, and its **drainage/ash-wash aftermath** (feeding the water-contamination incident). Each weather type defines warning source, forecast class, lead time, base/utility/resident/construction/expedition effects, preparation and emergency options, recovery work, and its visual/audio/accessibility language (ash light, fan pitch, captioned pressure cues).

## 2. The Day-4 storm (the slice's proving weather)

- **Early signal:** free 1-phase telegraph always (ash ticking, pressure audio); the monitored band gives a 2-day forecast with severity (D-022) — **no hidden-knowledge preparation**: everything prep rewards is visible in the report.
- **Preparation window & two strategies:** (a) *pre-stage* (storm-prep order: covers, intake baffles) and/or (b) *positioning* (seal-bulkhead choice, load-board pre-shedding, run scheduling around the front).
- **Three-plus emergency responses:** cut the hotplate · throttle scrubbers · hot repair · HIGHBALL bridge · abandon the unsealed side behind its bulkhead.
- **East/west asymmetry:** east rides on comfort (its wing holds sleepers — seal placement guards people); west rides on infrastructure (pump chain exposure; its storm-recovery refund is canon) — different effects, both documented in the model.
- **Outcomes:** prepped = manageable expenditure (cleanup, the storm-repair order); unprepped = **serious but recoverable**: +4 WU emergency labor, −2 Materials damage, one injury + a dose (model: `storm_unprepped` passes with visible costs, margin +14.1%).
- **Aftermath:** physical (intake repair, ash wash → contamination risk, salvage from wrack) and human (stress, the unprotected side's memory of the seal choice, confinement scenes).

## 3. Incident architecture and cascade rules

One reusable schema (config: family, cause, trigger, location, warning, severity, propagation, affected rooms/residents, escalation time, pause tier, responses, works generated, materials/equipment, utility/layout/skill interaction, escalation, aftermath ×2, recovery, delayed consequences, completion/failure, save behavior, test scenario). **Slice families (six):** flywheel instability · air-filtration failure · storm infiltration · structural instability · water contamination · health emergency. Full-game families (fire, flooding, spoilage, theft, sabotage, **intrusion**, panic, internal violence) reuse the schema — intrusion is *defined as a family here, resolved in a later stage* (§7).

**Cascade bounds (config-enforced):** normal incident touches 1 system; escalated 2; severe-ignored 3; **hard max 3, ever**. Isolation, backups, doors, layout, and priorities interrupt propagation. Every active cascade shows: current cause → current effect → *possible* next effect → time available → interruption points. Serious risk is never concealed; exact outcomes may stay uncertain (labeled as such).

**Canonical slice cascade** (modeled, both directions): *Flywheel instability → optional loads shed → scrubbers underpowered → east-wing air degrades (3-phase window) → exposure.* Interrupted at step 1 by HIGHBALL/repair, at step 2 by battery + shedding, at any point by evacuation/masks; ignored, it stops at step 3 (respiratory conditions — bounded, costed, recoverable).

**Stacking control (the scheduler caps stand):** one major immediate crisis; ≤2 minor warnings; decisions queue; scenes wait for safe windows; critical deterioration auto-pauses; routine wear never interrupts.

## 4. Recovery and emergency actions

The fifteen-action emergency vocabulary (ration food/water · shut down rooms · reassign all labor · battery · manual pump · temp filter · evacuate · isolate · cancel a run · break equipment for parts · request help · inferior materials · accept crowding · temporary conversion · abandon a section) — each stating **immediate benefit, immediate cost, delayed cost, residents affected, reversibility, promise/debt created, and future-incident effects**. Recovery is gameplay: one poor placement is never terminal (10 §9's two-sided guarantees); repurposing and relocation stay available at meaningful, non-ruinous cost.

## 5. HIGHBALL ORDER (the risk-reward action; "Redline" renamed, D-043)

Railway-native: *highball* — the old all-clear, full-speed signal. **One order per day**: push one works order (+50% progress this phase) or run one utility past rated capacity for one phase. Usable in <20 s: tap the order/load → HIGHBALL → confirm card shows **likely benefit (fact), known costs (fact), and breakdown risk (labeled uncertain, %)**. Costs: a named resident's overtime (fatigue + a **promise-of-rest debt** the game remembers), breakdown risk (worn machinery → repair debt, −Materials), consecutive-day use of the same resident → refusal + stress, 3+ uses/week doubles breakdown risk. **Never mandatory** (competent runs use zero — asserted); **can rescue a crisis** (the cascade scenario, verified); **cannot be spammed profitably** (the spam scenario shows debts + wear, verified). No premium anything; strong audiovisual identity (the green-lantern sweep, the Flywheel's rising note). Introduced diegetically at the storm, not in the first session.

## 6. Human aftermath (the ledger boundary holds)

Every incident and emergency action posts specific, named consequences — *"Teo cannot sleep beside the Flywheel" · "Imka remembers water security was overruled" · "Ash volunteered for overtime and expects the next shift off" · "the eastern sleepers distrust another shutdown"* — via memories, promises, refusals, dialogue, and room use. Internal numbers exist; **no global Humanity/Morality score is ever exposed**, and no mathematically perfect choice is identified (the community summary describes, never grades).

## 7. Conflict-boundary correction (D-044)

The absolute "no combat, permanently" rule (D-006, old Anti-pillar 3 phrasing, cut C5) is **retired** and replaced with **NO COMBAT POWER FANTASY**. Signal 45 may contain physical conflict: intrusion, threats, restraint, defensive preparation, dangerous encounters, last-resort force. Conflict must be dangerous, brief, avoidable where reasonably possible, prepared for through shelter design/information/equipment/negotiation/relationships, and consequential to health, trust, stress, resources, factions, and the station. Signal 45 must never become a shooter, a combat-loot treadmill, a resident power-level contest, a raid game, or a game where violence is routinely optimal. **No combat system is designed now** — but this stage's architecture is deliberately compatible: intrusion is an incident family; injuries route through the medical framework; protective gear is an item family; the Watch Post exists in the room catalog; standoffs remain the encounter grammar. Detailed resolution belongs to a later stage.
