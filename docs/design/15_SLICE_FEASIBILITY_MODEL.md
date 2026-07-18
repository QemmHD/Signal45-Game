# 15 — SLICE FEASIBILITY MODEL

**Stage:** Prompt 2 (revised after red-team pass 3, D-042). **Status:** COMPLETE — this document reports the executable model's actual output and is regenerated whenever the model changes. It is the **Slice Feasibility Sketch** promised by D-039/10 §15; 07 §21's exclusive-choice criterion cites it.
**Artifacts:** `tools/simulate_vertical_slice.py` (deterministic, engine-independent, no dependencies) · `tools/test_simulate_vertical_slice.py` (12 automated checks). Run: `python3 tools/simulate_vertical_slice.py --all` · `python3 tools/test_simulate_vertical_slice.py`.
**Prompt-3 note (D-043):** the model now also exposes its per-day ledger (pools, spends, completions, run nights) as data; the survival model (`tools/survival_model.py`, 20) **consumes that output as its labor truth** — one shared arithmetic, asserted identical in `tools/test_survival_model.py`. The labor results below are unchanged; the 12-test suite still passes byte-identically.

---

## 1. Assumptions (the honest inputs)

- **Work unit:** 1 WU ≈ 45 simulated minutes of one resident's focused work. *WU is design/model vocabulary only — it never appears on screen (D-042; the player sees "about half a shift's work").*
- **Capacity:** 4 residents × 7.5 WU/day gross × **0.85 global inefficiency**. 7.5 is the **matched-aptitude baseline**; aptitude modifiers (matched 1.0× / secondary ~0.8× / off-aptitude ~0.6–0.7×, per D-031) are a systems-stage layer this model does not yet carry — a **declared limitation** with its own revisit trigger (below), partially covered by the efficiency sweep.
- **Fiction constraints the model obeys (new in D-042):** Day 1 permits only the guided session's orderable work (gate repair, purifier, surveys, Flywheel stabilization) — **the route breakthrough cannot begin before Day 2's community scene**; storm response work unlocks Day 4; discretionary builds (Cold Store, late second wing) unlock Day 5; nightrun rewards require an able runner that night (an absent runner shifts the run a night later).
- **Human-ledger pricing (new in D-042):** west's rough sleeping costs −1.0 WU/day until the bunks exist and bench triage costs +1 WU when event-19 triage lands without an Aid Car; east's Sleeper Car pays +0.75 WU/day from Day 4; west receives its canonical +3 WU storm-recovery refund on Day 5. The routes' margins now converge *on paper*, not just in prose.
- **Essential daily workload:** cooking 2 + cleaning/checks 2 + water duty (3 tank / 1 cistern) = 6–7 WU/day; Day-3 triage 2 (+1 bench penalty); storm day +4 prepped / +8 **and −2 salvage damage** unprepped (prep is genuinely positive-EV).
- **Materials:** one Salvage pool; start 12; yields: clear +10, drain +8, Depot 9 +7, Arcade +5; reserved at confirmation, refunded on cancel. Crafting beyond the splice/purifier is **not modeled** (listed limitation; 07 §9's joint-account criteria remain a systems-stage test).
- **Task classes:** short installs (≤3 WU) don't consume one of 3 project slots; the class boundary is **authored per order type, never derived at runtime** (anti-decomposition rule, 11 §5); per-project daily cap 12 WU.
- **Milestone classes:** *hard* milestones = the slice fails without them; *soft* milestones (storm prep, Juna's berth-by-D6) have authored miss-branches (unprepped storm; the witnessed turn-away). Dramaturgy targets (trunk mid-storm, first room D3) are tracked as **beat drift** — reported, non-fatal, and required clean in competent runs only.
- **Explicitly NOT assumed:** perfect assignment (0.85 factor + the efficiency sweep), exact foreknowledge (the `prep_last` misordering scenario), zero injuries (event 19 is in every run), any mandatory survivor (absence sweep), optional resources, max speed, cancellation exploits, hidden bonuses.

## 2. The project bill (from the model, not by hand)

**East: 93.0 WU mandatory** (guided Day-1 work 14, clear 12, seal 4, prep 3, sleeper 7, reinforce 3, trunk 6, storm repair 6, canteen 6, aid car 6, lift 5, fitters 4, splice 3, LP upgrade 4, berth 3, module 4, staging 3, + surveys) · **West: 91.0 WU** (drain 12, cistern 6, pump 6, bunks 5, otherwise parallel). **Supply: 110.2 (east) / 109.2 (west)** total project-pool WU across the week — west's water-duty drop after the cistern comes online offsets its rough-sleeping malus.

## 3. Results — required suite, stress, and sweeps (actual output)

| # | Scenario | Hard milestones | Margin | Week time |
|---|---|---|---|---|
| 1 | EAST, competent | **ALL MET**, no beat drift | **+18.4%** | 80.2 min (delegated) |
| 2 | WEST, competent | **ALL MET**, no beat drift | **+19.9%** | 80.2 min |
| 3 | EAST, one significant mistake¹ | ALL MET (drift: trunk d5, sleeper d4) | +9.0% | 80.2 min |
| 4 | WEST, one significant mistake² | ALL MET (drift: trunk d5, pump d6) | +10.1% | 80.2 min |
| 5 | EAST, survivor unavailable (required run) | ALL MET | +11.6% | 80.2 min |
| 6 | EAST, construction interrupted | ALL MET (drift: sleeper d4) | +14.4% | 80.2 min |
| 7 | WEST, delegated nights | ALL MET | +19.9% | 80.2 min |
| 8 | WEST, active nights (same world outcomes) | ALL MET | +19.9% | 90.1 min |
| S | Both wings pre-storm (exclusivity stress) | **Second wing never starts** — the allocator cannot open it pre-storm | +12.4%³ | — |

¹ Early Cold Store + re-sited beds, +8 WU. ² Seal on the wrong bulkhead, +7 WU storm damage. ³ The stress run's margin is computed against completed work only; its meaning is the exclusivity proof, not a viability claim.

**Sweeps (all-cells evidence, not best-case):**
- **Absence sweep (every resident × Days 2–6 × both routes, 40 cells):** worst cell = Imka absent Day 2, west — **all hard milestones still met**, margin +10.7%. The berth (soft) survives every cell in the current tuning.
- **Efficiency sensitivity:** hard milestones hold on both routes down to **0.80** (margins +6.9% E / +6.8% W); first failure at 0.775 (west misses the splice-by-D6). The 15% competent-margin gate itself holds at 0.85 and degrades gracefully below.
- **Essentials-neglect (cheese check):** suspending cleaning saves 2 WU/day but its consequence chain costs 3 WU/day from Day 3 — net margin **+17.4% < +18.4% competent**: the exploit is net-negative (D-042's answer to suspended-tier cheese).
- **Plan misordering (`prep_last`):** storm prep deferred behind the trunk → the soft prep milestone slips (authored unprepped-storm branch: +4 WU and −2 salvage), all hard milestones still met, +14.1%.
- **Late second wing:** startable Day 5 at +25% cost as discretionary work; the competent week absorbs it without losing any milestone — "reachable late-week at documented higher cost" is now modeled, not asserted.

**Automated test suite: 12/12 passing** — hard milestones across the required suite; ≥15% competent margins with clean beats; exclusivity via the second-breakthrough check; disruption + misordering survival; the absence-sweep worst cell; the efficiency floor at 0.80; the neglect-cheese check; determinism; delegated/active world-outcome identity; session budgets (including active ≤ the 100-minute gate and active share ≤ 1/3); runs firing only on scheduled nights; the CLI gate.

## 4. Timing (consistency check under stated constants — not independent proof)

The session-time submodel prices decisions (0.35 min each; a sensitivity note: at 0.5 min/decision a delegated day reaches ~13 min — the systems stage must measure real decision time), phase framing, night mode **on run nights only** (quiet nights 0.25 min), and Day 7's relay scene (+3 min).

| Gate | Target | Model |
|---|---|---|
| Delegated full day | ~8–12 min | 10.6–11.6 (Day 1: 11.1; storm day: 11.0) |
| Active-run day | ~11–16 min | 14.9 (run nights only) |
| Day 7 (relay finale) | — | 13.0 |
| Seven-day totals | 60–100 min | **80.2 delegated · 90.1 all-active** |
| Active share of playtime | ≤ ~1/3 | **15.0%** (13.5 of 90.1 min, 3 runs) |

## 5. What the margins mean

Competent play holds the mandated 15–20% margin on both routes — **and the routes now converge (+18.4 vs +19.9, gap 1.5pp)** because the human ledger is priced into the labor model (D-042): east pays for its comfort in tank-water drudgery, west pays for its water security in rough sleep and bench triage, and each route's compensations are arithmetic, not adjectives. Disruption scenarios stay positive but thin (+9.0% worst): the slice survives one meaningful mistake **or** one absence anywhere in Days 2–6 (proven by sweep, not by a single cell), not both stacked. For the stacked case the documented labor levers are: drop discretionary work (Cold Store, late second wing), draw **Juna's +4 WU uncounted Day-7 buffer** (if her berth landed), and shift Aid/Canteen furnishing to Day 7; the R-11 valve covers **material** deficits only (06 R-11, as re-scoped).

## 6. Schedule findings (competent shape, both routes)

Day 1 is fully guided and fully productive (gate repair, purifier, all three surveys, Flywheel stabilization — 14 WU of real work, no route labor). Day 2 opens the chosen wing (breakthrough completes at the 12-WU cap). Day 3 lands the first wing room (Sleeper Car / Cistern Works) plus seal and prep. Day 4 — sealed storm — lands reinforcement and **the trunk, mid-storm** (the lights-through-the-dust beat), on both routes. Day 5 is the big wave (pools 19.2 E / 20.5 W with the west refund): storm repair, lift, berth, splice, plus Canteen (E) or Pump Room + bunks (W). Day 6 crosses the 8-area threshold (LP wired, Aid Car / staging, Fitters' Shop). Day 7 carries real, visible finale work — **module expansion + Cold Store (+ staging on east)**, ~9.0–9.6 WU spent against ~19–20 available, with the remaining surplus honestly labeled the week's buffer and Juna's uncounted +4 WU on top.

## 7. Model-driven design corrections (D-041 + D-042 — cumulative)

1. Short-install class formalized; **boundary authored per order type, never runtime-derived** (anti-decomposition).
2. Salvage economy retuned (start 12; clear +10 / drain +8 / Depot 9 +7 / Arcade +5; Day-1 repair and purifier now charge their 3 salvage).
3. **Day-1 guided-session constraint encoded** — the model can no longer spend route labor before the route choice exists; Flywheel stabilization added as priced, route-neutral Day-1 work (it also carries the "upgrade" fiction on Day 1).
4. **Human-ledger route pricing** (rough sleep, bench triage, rest bonus, storm refund) — route margins converge on paper.
5. **Nightruns require an able runner**; rewards can no longer materialize without one.
6. Storm prep made positive-EV (unprepped = +4 WU *and* −2 salvage); prep slips are flagged as soft-milestone misses, never silent.
7. Milestone classes (hard / soft / beat-drift) — disruption runs are judged on survival requirements, competent runs on the full dramaturgy.
8. Cold Store added as the priced discretionary build (Day 5+); the late second wing added as priced optional work — Day 7 now has sanctioned, visible finale construction.
9. Berth cost labor-only; lift survey due Day 4; west builds Pump Room in the Day-5 wave.
10. **No mandatory beat was cut, no day lengthened, no invisible resources added, and the building core is untouched.**

## 8. Final feasibility verdict

**FEASIBLE — on both routes, under fiction-faithful constraints, with converged margins and swept (not cherry-picked) disruption evidence.** Remaining declared limitations for the systems stage: aptitude-differentiated labor, crafting's full material draw, real decision-time measurement, and watch-time in the session model. The model is deterministic evidence, not proof of fun; 07's playtest gates remain the experience check. If the model changes, regenerate this document and 14 after running both test suites — there is no CI; the suites run before every commit (06's drift row owns the discipline).
