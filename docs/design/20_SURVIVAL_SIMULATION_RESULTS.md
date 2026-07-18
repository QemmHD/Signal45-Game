# 20 — SURVIVAL SIMULATION RESULTS

**Stage:** Prompt 3 (regenerated after the D-045 red-team pass). **Status:** COMPLETE — reports actual output of `tools/survival_model.py` (seed 45) layered over the unchanged labor model; regenerated whenever configs change (by hand — there is no CI; the two suites are run before every commit). **Every value is PROVISIONAL** design-model evidence, not balance and not playtest (D-043). Tests: `tools/test_survival_model.py` (38) + `tools/test_simulate_vertical_slice.py` (12) — **50/50 passing**.

---

## 1. Assumptions and declared simplifications

The survival layer consumes the labor model's per-day output (pools, completions, runs — one shared truth, asserted identical in tests; run names and the materials constant are pinned by tests so the coupling cannot silently break). Deterministic seeded LCG for the single stochastic element (HIGHBALL breakdown; the LCG's low-bit weakness is noted in code — replace before per-phase use).

**Declared simplifications (D-045 — claims this model does NOT evidence):**
- Needs step daily, not per-phase; meal windows and rest are day-granular.
- The needs→work ladder is **same-day survival-side accounting**: strained/critical hunger or fatigue derates the day's effective labor (reported as `needs_derate_wu` and an adjusted margin, floor ×0.7 asserted) — the precomputed labor plan is not re-planned. Full feedback is first-playable work.
- The human ledger beyond HIGHBALL's tracked rest debt is note-level: shared hardships stress all residents uniformly; memories, promises, refusals, grudges, and Marks are 19 §6 canon, not model state. Phrases like "Ash's line crossed" in §2 are design framing, not assertions.
- Materials arithmetic (reservation, cancel refunds, deconstruct recovery) is the labor model's and the reservation system's domain — **rule-level here, not simulated** (see §3B).
- Food spoilage is architecture-only (`spoilage.slice_active: false`); HIGHBALL's +50% labor benefit is unmodeled (the modeled benefit is the cascade bridge — §3B); aptitude-blind labor and unmodeled crafting are inherited D-042 limitations.
- Health never approaches death in any scenario (floor across the matrix: 78). The no-death and critical-warned assertions are **structural guards**, exercised in the healthy regime only; the sub-critical warning ladder (decline warning at health < 55, critical at < 40) fires in no current scenario.
- The exhaustion condition (fatigue 100) is unreachable in the matrix — the anti-spam refusal ladder blocks the consecutive pushes that would reach it (a design result, verified in §2, not an accident).
- The `meds_low` free-doses warning threshold fires in no current scenario (medicine floor is 5).

## 2. Scenario results (23 scenarios, all passing; seed 45)

| Scenario | End stocks (food/water/meds/charge) | Verdict & meaning |
|---|---|---|
| East competent | 4 / 16 / 7 / 24 | PASS, 8 warnings — fed, watered, banked charge; food deliberately thin; the Day-3 lantern pinch dims the comfort lighting for one evening (the board's first lesson, D-047) and it auto-restores next day |
| West competent | 2 / 21 / 7 / 10 | PASS — water-rich; **comfort lighting dims first on every deficit day (the Optional tier, D-047), then the hotplate (cold meals Days 2–5)**; repeats present as resident memories, not repeated banners (asserted); extended platform darkness posts its modest stress note; west's priced discomfort is comfort, not blackout |
| East resource mistake (overtraded 10 meals) | 0 / 16 / 7 / 24 | PASS with costs: food rationed Days 6–7 (stress, remembered), 2 meals short Day 7 — warned from Day 3 |
| Shortage unrationed (mistake + every lever refused) | 0 / 16 / 7 / 24 | PASS with costs: 3 short days, hunger climbs, **crew slows ×0.900 (−1.0 WU, adjusted margin +17.6%)** — reduced never zero; short-but-alive; the anti-death-spiral case |
| West resource mistake (valve left open, late rationing) | 2 / 10.5 / 7 / 10 | PASS with costs: −12 water Day 3, forecast fires, **rationing fires Day 4** (stress, remembered) — mistake → forecast → response → recovery |
| Injury absence (labor absence run) | 3 / 16 / 7 / 24 | PASS at +11.6% labor margin |
| Water contamination (Day 5, boil order) | 4 / 15 / 7 / 24 | PASS — STORAGE-link-named warning (asserted), boil order at its config price, flush Day 6 |
| Contamination ignored | 4 / 15 / **5** / 24 | PASS-with-cost: illness-risk forecast Day 5 → **waterborne illness (Maren) Day 6** → 2-dose course Day 7; her health ends 78 — the dismissed warning's price, warned first |
| Power→air cascade (battery response) | 4 / 16 / 7 / 24 | PASS — battery bridge **costs**: −5 cell-hours + Normal tier dark while bridging (cold meal, stress echo); cascade stops at step 2 |
| Cascade ignored | reaches step 3, stops | PASS-with-cost: respiratory exposure, bounded at the 3-system max |
| Storm prepped | 4 / 16 / 7 / 24 | PASS — pre-staged covers, cleanup only (flag-distinguished from the bare competent run) |
| Storm unprepped (east) | 4 / 16 / **6** / 24 | PASS — recoverable: injury (health hit, treated, **never healing past start health**) + dose + damage; margin +14.1%. The Day-3 free telegraph precedes it (asserted) |
| Storm unprepped (west) | 2 / 21 / 6 / 10 | PASS — same recoverability on the west route, +15.5% margin |
| HIGHBALL appropriate (cascade rescue) | cascade stopped step 1 | PASS — one use, promise-of-rest debt logged; trades off against the battery path (debt vs. cold meal — asserted distinct) |
| HIGHBALL overused (attempted 4-day spam) | 4 / 16 / 7 / 24 | PASS-with-cost: **3 executed, 1 refused** ("pushed yesterday — will not go again", stress), 3 rest debts, doubled breakdown risk from use 3; no stock ends better than baseline (asserted) |
| Juna admitted (west) | 2 / 21 / 7 / 10 | PASS — demand rises Day 6+ (the west competent week read through the admission lens — same run by design, scenarios.json note) |
| Juna no-berth (absence week) | 4 / 20 / 7 / 12 | PASS — witnessed turn-away: stress cost, no mechanical collapse |
| Cancel after reserve | — | **Rule-level, labeled as such**: refund ≤ reserve is a design rule (resources.json), not simulated arithmetic — see §3B |
| Production room offline (Pump Room) | water 9 (vs 21) | PASS — visible cause, water margin halves |
| Essentials neglected | +17.4% < +18.4% | PASS — consequence chain outprices the saved labor (inherited) |
| Reduced efficiency (0.80) | +6.9% margin | PASS — hard milestones hold (inherited floor) |
| Storage cap reached (deliberate hoard) | water 26, **11 person-days overflowed** (charge 10) | PASS — overflow is real: "surplus runs to the drain" warning fires Days 4–5, loss visible, never silent (asserted) |
| Save/reload mid-incident (Day 3) | resumed twin identical | PASS — full state serialized through JSON, loaded into a fresh instance, **resumed Days 4–7, Day-7 states compared equal** (asserted; a divergence fails the run) |

**Route balance audit (count-based; magnitudes are playtest questions):** east wins 3 categories (food, charge, stress), west wins 2 (water, margin); fatigue ties at the recovered floor. **Charge is an east win by design** (24 vs 10 — west sheds comfort loads instead of draining the rack, and the platform lamps pay part of the price). No route wins everything (asserted); west's water prize is a buffer whose value the modeled week never stresses on east, so the slice week is expected to *feel* harder on west — the ≤70% route-convergence playtest gate (07 §21) and the §5 cold-meal probe are the checks on that prediction.

## 3. Exploit and contract tests

**A. Closed by simulation (asserted against real state):** negative stocks (all scenarios) · storage hoarding (overflow loss + forecast fire in the hoard run) · HIGHBALL same-day spam (one/day), consecutive-day push (refusal + stress), hazard-bar push (unit-tested refusal at critical fatigue), spam profit (no stock beats baseline) · essentials suspension (net-negative, inherited) · shortage-without-forecast (warning ledger checked at every shortage stage, storm included) · efficiency-ladder floor (×0.7, never zero) · injury-heals-past-start (recovery clamps to start health) · save-scumming a mid-incident state (resume-compare) · route sweep (no category sweep by either route).

**B. Closed by design rule, NOT simulated (the reservation system's first-playable work):** build/cancel refund ≤ unconsumed reserve · deconstruct 50%-once recovery · spoilage forecast-conversion. These are stated in `resources.json`, labeled rule-level in the model's own output, and listed in 07's acceptance gates — claiming them as simulation results was a D-045-corrected error.

## 4. Load audits (D-043/D-045; beat sheet annotated)

**Day 5** — **primary:** the route room (Canteen E / Pump Room+bunks W). **Essential:** storm repair (due Day 5). **Short installs (no slots):** berth, splice. **Deferrable:** lift (west already Day 6; east may slip without milestone loss). The concurrency cap (3 projects + shorts) bounds simultaneity; the report's "tomorrow's headline" names the primary goal so Day 5 reads as *one goal, one obligation, two quick wins*.

**Day 4 (new, D-045)** — the storm day stacks up to three first-time surfaces: the live cascade display, the HIGHBALL card (introduced diegetically here), and — on east — the load board operated in anger. Mitigations now canon: the **east Day-3 charge pinch** (14, Day 3) gives east its first load-board lesson *before* the storm, matching 13 §2's teaching moment; the cascade display carries its interruption points on-card; HIGHBALL is optional and the scheduler caps (1 modal · ≤3 banners) bound simultaneous demands. The audit's verdict is *load acceptable with the pinch in place*; the 07 §4b comprehension probe is the check.

## 5. Remaining uncertainty and first-playable revalidation gates

D-041/D-042's triggers stand, plus (with the D-041-style bound: **first-playable measurements diverging >20% from a config value force re-derivation of that value's block**):

- Real meal/rest pacing vs. daily steps; per-phase needs granularity; the full needs→labor feedback loop (replacing this model's same-day accounting).
- Contamination discovery timing (meal-window vs. instant) — a named first-playable A/B decision.
- **HIGHBALL profitability**: the +50% labor benefit exists only at first playable — re-audit spam vs. benefit there; felt weight, audiovisual identity, and **card comprehension** (07 §4b probe: after first use, ≥4 of 5 testers can state what it cost the named resident and that rest is owed).
- West's cold-meal week (priced strategy vs. annoyance — 07 §20 descriptor-card probe, west cohort) and food thinness (tension vs. starvation anxiety — 07 §20 probe, all testers).
- The unexercised guards (§1): death ladder, exhaustion, meds_low — first playable must construct the states this matrix cannot reach and verify the warnings fire.

**None of this document's numbers are balance claims; they are consistency evidence.**
