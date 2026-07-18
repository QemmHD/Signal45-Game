# 20 — SURVIVAL SIMULATION RESULTS

**Stage:** Prompt 3. **Status:** COMPLETE — reports actual output of `tools/survival_model.py` (seed 45) layered over the unchanged labor model; regenerated whenever configs change. **Every value is PROVISIONAL** design-model evidence, not balance and not playtest (D-043). Tests: `tools/test_survival_model.py` (25) + `tools/test_simulate_vertical_slice.py` (12) — **37/37 passing**.

---

## 1. Assumptions

The survival layer consumes the labor model's per-day output (pools, completions, runs — one shared truth, asserted identical in tests) and adds stocks/needs/utilities/incidents from `tools/data/*.json`. Deterministic seeded LCG for the single stochastic element (HIGHBALL breakdown). Known simplifications, declared: needs step daily (not per-phase); Materials mirrors the labor ledger; crafting beyond splice/purifier unmodeled (inherited limitation); aptitude-blind labor (inherited, D-042's declared limitation).

## 2. Scenario results (20 scenarios, all passing)

| Scenario | End stocks (food/water/meds/charge) | Verdict & meaning |
|---|---|---|
| East competent | 4 / 16 / 7 / 24 | PASS, 1 warning — fed, watered, banked charge; food deliberately thin (scarcity is real) |
| West competent | 2 / 21 / 7 / 2 | PASS — water-rich, **charge-poor and cold-meal days 2–4** (pump rig sheds the hotplate: west's priced discomfort, visible as banners) |
| East resource mistake (overtraded 10 meals) | 0 / 16 / 7 / 24 | PASS with costs: short meals late-week, hunger+stress, 6 warnings — serious, recoverable, warned |
| West resource mistake (late rationing) | 2 / 21 / 7 / 2 | PASS with rationing stress costs |
| Injury absence (labor absence run) | 4 / 16 / 7 / 24 | PASS at +11.6% labor margin |
| Water contamination (Day 5) | 4 / 15 / 7 / 24 | PASS — link-named warning, boil order (+2 charge/day), flush by Day 6, 1 person-day lost |
| Power→air cascade (Day 3) | interrupted step 2 | PASS — battery bridge + shedding; warning ledger clean |
| Cascade ignored | reaches step 3, stops | PASS-with-cost: respiratory exposure, bounded at hard max 3 |
| Storm prepped | 4 / 16 / 7 / 24 | PASS — cleanup only |
| Storm unprepped (prep_last labor) | 4 / 16 / **6** / 24 | PASS — **recoverable**: +4 WU emergency, −2 materials, injury + dose; labor margin still +14.1% |
| HIGHBALL appropriate (cascade rescue) | cascade stopped step 1 | PASS — one use, promise-of-rest debt logged |
| HIGHBALL overused (3 uses) | — | PASS-with-cost: 3 rest debts, consecutive-day strain protests, doubled breakdown risk (anti-spam verified) |
| Juna admitted (west) | 2 / 21 / 7 / 2 | PASS — demand rises Day 6+, labor buffer noted |
| Juna no-berth (absence week) | 4 / 20 / 7 / 0 | PASS — witnessed turn-away: stress cost, Ash's line crossed, **no mechanical collapse** |
| Cancel after reserve | — | PASS — refund ≤ reserve, sunk labor lost: net loss, no exploit |
| Production room offline (Pump Room) | water 9 (vs 21) | PASS — visible cause, water margin halves: optional rooms matter, shutdown isn't free |
| Essentials neglected | labor margin +17.4% < +18.4% | PASS — consequence chain outprices the saved labor (cheese dead, inherited) |
| Reduced efficiency (0.80) | +6.9% margin | PASS — hard milestones hold (inherited floor) |
| Storage cap reached (water hoard) | clamped at cap | PASS — overflow forecast ("surplus runs to the drain"), never silent |
| Save/reload mid-incident (Day 3) | identical restore | PASS — no divergence, no duplication |

**Route balance audit:** east wins 2 categories (stress, food), west wins 2 (water, margin), charge splits by design — **no dominant route** (asserted in tests). East = comfort/charge/calm; west = water/margin/cold-meals-and-crowding until the bunks land.

## 3. Exploit tests (all closed)

Negative stocks (asserted everywhere) · infinite materials via build/cancel (refund ≤ unconsumed reserve; sunk labor lost) · deconstruct-rebuild (50% recovery, once per component) · HIGHBALL spam (one/day; debts; doubled risk; consecutive-day refusal) · emergency-action spam (rationing costs stress+memory; shedding costs meals) · utility-priority cheese (optional-room shutdown visibly halves water margin) · essentials suspension (net-negative, inherited) · storage hoarding (cap + forecast overflow) · death-without-warning (structurally impossible: unwarned critical = assertion failure) · uninterruptible cascades (interruption asserted) · hidden mandatory HIGHBALL (competent runs assert zero uses).

## 4. Day-5 audit result (D-043; beat sheet updated)

Day 5 classified — **primary:** the route room (Canteen E / Pump Room+bunks W). **Essential:** storm repair (due Day 5). **Short installs (no slots):** berth, splice. **Deferrable:** lift (west already Day 6; east may slip without milestone loss). **Route-alternative:** everything else. The concurrency cap (3 projects + shorts) already bounds simultaneity; the report's "tomorrow's headline" names the primary goal so Day 5 reads as *one goal, one obligation, two quick wins* — not six competing mandates. No day lengthened; character scenes cost only event-friction WU already priced.

## 5. Remaining uncertainty and first-playable revalidation gates

All of D-041/D-042's triggers stand, plus: real meal/rest pacing vs. daily steps; per-phase needs granularity; contamination discovery timing (meal-window vs. instant); HIGHBALL's felt weight (20-second usability, audiovisual identity); west's cold-meal week (is priced discomfort *felt* as strategy or annoyance — playtest question); food thinness (end-of-week 2–4 meals is intended tension — verify it reads as tension, not starvation anxiety). **None of this document's numbers are balance claims; they are consistency evidence.**
