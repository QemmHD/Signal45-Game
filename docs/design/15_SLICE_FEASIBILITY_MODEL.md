# 15 — SLICE FEASIBILITY MODEL

**Stage:** Prompt 2. **Status:** COMPLETE — this document reports the executable model's results and is regenerated whenever the model changes. The model is the **Slice Feasibility Sketch** promised as a blocking deliverable by D-039/10 §15; 07 §21's "labor/material math verified" refers to this artifact.
**Artifacts:** `tools/simulate_vertical_slice.py` (deterministic, engine-independent, no dependencies) · `tools/test_simulate_vertical_slice.py` (8 automated checks). Run: `python3 tools/simulate_vertical_slice.py --all` · `python3 -m unittest discover tools -v`.

---

## 1. Assumptions (the honest inputs)

- **Work unit:** 1 WU ≈ 45 simulated minutes of one resident's focused work.
- **Capacity:** 4 residents × 7.5 WU/day gross, × **0.85 global inefficiency** (travel, task switching, imperfect assignment — the mandated competence margin, not perfect play).
- **Essential survival workload, daily:** cooking 2 + cleaning/checks 2 + water duty (**3** from the emergency tank / **1** once Cistern Works + Pump Room are online) = 6–7 WU/day off the top.
- **Frictions modeled:** Day-1 onboarding loss (−5); runner's morning-after (−3 per run); event-19 minor injury (Teo −2 on Day 3 + 2 WU triage); storm-day emergency load (−4 prepped / −8 unprepped); scene/arbitration friction (−2 on Days 2 and 6).
- **Materials:** one Salvage pool (construction and crafting draw jointly, per the 07 §9 joint account); start 12; yields from clearing (+8 E), draining (+6 W), Depot 9 (+7), Arcade (+5). Reserved at project confirmation; refunded on cancel.
- **Task classes:** short installs (≤3 WU) don't consume one of the 3 concurrent-project slots; the daily per-project cap is 12 WU (~2 workers' useful limit).
- **Explicitly NOT assumed:** perfect assignment, exact foreknowledge, zero injuries, any single mandatory survivor beyond canon roles, optional resources, max simulation speed, cancellation exploits, hidden bonuses.

## 2. The project bill (route totals)

Shared mandatory work ≈ 43 WU (surveys, seal, storm prep + repair, LP upgrade, splice, lift, Fitters' Shop, staging, berth, module). East wing ≈ 46 WU (clear 14, reinforce 4, trunk 6, Sleeper 8, Canteen 7, Aid Car 7). West wing ≈ 44 WU (drain 14, reinforce 4, trunk 6, Cistern 8, Pump Room 6, bunks 6). **Route totals: East ≈ 89 WU · West ≈ 87 WU** against ~105–107 WU of available project labor across the week.

## 3. Results — the eight required scenarios (+1 stress)

| # | Scenario | Milestones | Margin | Week session time |
|---|---|---|---|---|
| 1 | EAST, competent | **ALL MET** | **+15.5%** | 80.1 min (delegated) |
| 2 | WEST, competent | **ALL MET** | **+22.6%** | 80.1 min |
| 3 | EAST, one significant mistake¹ | **ALL MET** | +2.4% | 80.1 min |
| 4 | WEST, one significant mistake² | **ALL MET** | +14.8% | 80.1 min |
| 5 | EAST, survivor unavailable³ | **ALL MET** | +8.5% | 80.1 min |
| 6 | EAST, construction interrupted⁴ | **ALL MET** | +12.3% | 80.1 min |
| 7 | WEST, delegated nightruns | **ALL MET** | +22.6% | 80.1 min |
| 8 | WEST, active nightruns (same world outcomes) | **ALL MET** | +22.6% | 99.9 min |
| S | Both wings pre-storm (exclusivity stress) | **FAILS** (7 milestones missed) | — | — |

¹ early Cold Store + re-sited beds: +8 WU wasted. ² seal on the wrong bulkhead: +7 WU storm damage. ³ Imka absent all of Day 5 (overwork collapse). ⁴ one project loses 3 WU of staged progress. The stress row is *supposed* to fail: it proves the east/west choice is genuinely exclusive before the storm (a both-wings attempt misses the storm repair, room count, upgrade, module, berth, and splice).

**Automated test suite: 8/8 passing** — milestones in all required runs; ≥15% competent margins; exclusivity; disruption survival; determinism (identical reports on repeat runs); delegated/active world-outcome identity (same completion days, different session minutes); session-time budgets.

## 4. Timing validation (quality-gate evidence)

| Gate | Target | Model |
|---|---|---|
| Delegated full day | ~8–12 min | 10.4–11.6 (avg 11.4) |
| Active-run day | ~11–16 min | 14.9 |
| Day 1 guided | ≤15 min | 12.0 |
| Seven-day total | 60–100 min (07 §14) | 80.1 delegated · 99.9 all-active |
| Active share of playtime | ≤ ~1/3 | 19.8 min of 99.9 = 20% |
| Safe stops | every 2–5 min | structural (per decision/stage; 12 §3) |

## 5. Capacity margins and what they mean

Competent play holds the mandated **15–20%+ margin** on both routes (E +15.5, W +22.6). Disruption scenarios stay positive but thin (+2.4% worst): the slice **survives one meaningful mistake or one absence, not both stacked** — which is the intended difficulty posture for a first chapter (the R-11 valve exists for the stacked case, once, never erasing a deficit). East's tighter margin is the price of its three-room comfort suite; west's looser margin is taxed instead in Strain and triage penalties that the labor model does not price — the human ledger keeps the routes honest where the arithmetic can't.

## 6. Schedule findings (the model's day-by-day shape)

- Both breakthroughs complete **Day 2**, first wing room **Day 3**, trunk **Day 4 (mid-storm — the lights-through-the-dust beat)**, the big build wave **Day 5** (18.5 WU pool), the 8-area threshold **Day 6**, and Day 7 runs deliberately light (~6–12 WU planned against 18.5 available) so the finale breathes.
- The exclusivity window is real: pre-storm capacity ≈ 42 project-WU vs. ≈ 34 WU for a *second* wing's pre-storm chain — the both-wings stress run confirms wholesale failure, not near-miss.
- Salvage is the binding constraint early (start 12 is fully committed by Day 3); the breakthrough yield and Depot 9's +7 are load-bearing — which is by design (the keystone run matters) and is the documented reason Depot 9 is Night 2 canon.

## 7. Scope revisions produced by the model (D-041)

1. **Short-install class formalized:** tasks ≤3 WU don't occupy a project slot (they starved behind the concurrency cap in early runs). This is now a work-order model rule (11 §5), not just a simulator fix.
2. **Salvage economy retuned:** start 12 (was 10); clear/drain yields raised to +8/+6; Depot 9 +7; Arcade +5. The earlier numbers left the west route materials-starved by Day 6 (lift, Fitters', LP upgrade, and module all blocked).
3. **Plan-order corrections:** lift repair and the LP upgrade scheduled ahead of second-wave rooms; west builds Pump Room before bunks (pump due-date pressure). These are the beat sheet's canonical orderings.
4. **Berth cost reduced to labor-only** (bedding from stores) — materials pressure belongs on rooms, not on Juna's welcome.
5. **Survey-lift due date moved to Day 4** (was Day 3) — mid-week is honest; Day 3 forced a false rush against the injury beat.
6. **No reductions were needed** to the mandatory beat list itself: all 07 §21 beats fit as specified. No day was lengthened, no invisible resources added, no instant completion introduced, and the building core is untouched.

## 8. Final feasibility verdict

**FEASIBLE.** The First Count's mandatory beats fit four residents' honest labor on both routes with the required competent-play margin, survive each single disruption tested, keep the exclusive choice exclusive, land the session-time budgets, and leave Day 7 the breathing room the finale needs. The model is deterministic evidence, not proof of fun — the playtest gates in 07 remain the experience check. Numbers in 14 and 11 are this model's outputs; if the model changes, regenerate both.
