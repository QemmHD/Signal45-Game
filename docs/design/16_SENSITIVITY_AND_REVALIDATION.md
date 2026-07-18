# Signal 45 — Sensitivity and Revalidation

## Reading this report

All balance values are provisional. The baseline comparison is East S01 at 20.4% usable project-capacity buffer and West S02 at 15.8%. Paired cases were run on both routes where route effects matter. “Session effect” is a modeled interaction budget, not measured player time.

## Sensitivity matrix

| Parameter | Baseline → tested range | East effect | West effect | Session effect | Safety / feasibility effect | Optional becomes required? | Prototype measurement |
|---|---|---|---|---|---|---|---|
| Work capacity | 100% → 90%, 80% | 90% fails at 7.2%; 80% fails at 5.6% | 90% fails at 6.7%; 80% fails at 4.7% | nominal UI time unchanged; more carryover decisions likely | **Both routes infeasible at −10%** | no; hope beat remains incomplete rather than Highball becoming required | observed useful WU/day by condition and interruption |
| Travel overhead | East 8%, West 10% → ×1.5 | viable but buffer falls to 9.7% | infeasible at 7.0% | walk animation may lengthen unless compressed | **West route crosses feasibility** | no; spatial layout would need correction | path length, lift/stair time, congestion, carry trips |
| Construction work | canonical project WU → +15% | infeasible at 7.6% | infeasible at 7.2% | longer work observation; likely extra segment | **Both routes infeasible** | Highball must not be reclassified as required | instrumented task durations and interruption cost |
| Food use | 1.0/person/day → +20% | fails at 5.4, below reserve 6 | fails at 5.4 | no direct change | **Both routes infeasible** | a Food gain would become mandatory; reject without retune | ration comprehension, expedition packing, newcomer issue |
| Water use | 1.5/person/day → +20% | fails at 6.6, below reserve 8 | viable at 12.6 | no direct change | East crosses; West identity is confirmed | East reserve/trade would become mandatory if consumption rises | actual issue cadence and treatment/emergency demand |
| Charge capacity | 30, start 24 → 15 cap/start | prepared East ends 15 and passes | prepared West ends 15 and passes | no direct change | no route crosses under prepared storm | no | discharge visibility, deficit duration, load-shed behavior |
| Power demand | canonical loads → +15% | passes; margin/display pressure rises | passes | forecast reading may add seconds | no route crosses in prepared case | no | simultaneous runtime loads and mobile forecast clarity |
| Filter condition | 72% → ×0.85 | partial storm passes at 20.1% | partial storm passes at 16.0% | storm stage budget remains under eight minutes | no route crosses; Medicine/Charge pressure rises | filter service remains a choice among responses | degradation rate, section isolation, exposure comprehension |
| Storm lead time | 2 stages (+ signal) → −1 stage and +3 response WU | viable at 18.3% | viable at 16.1% | Day 5 rises to about 7.95 min | narrower work margin, no route cross | no | whether one stage gives understandable response time |
| Storm intensity | 100% → 120% | prepared case viable at 20.0% | prepared case viable at 15.4% | Day 5 about 7.84 min | prepared state absorbs it; unprepared combination not accepted as a release assumption | no | actual incident interaction time and animation readability |
| Medicine use | 100% → 150% with visible minor injury | East viable, ends 6 | West viable, ends 7 | treatment interaction unchanged in budget | reserve tightens without route cross | trader remains helpful, not required | treatment frequency and UI explanation |
| Juna recovery | normal → +1 Water, +1 Medicine, zero Day 7 work | prepared East viable, ends Food 10/Water 15/Medicine 7 | prepared West with a real berth plan viable at 12.0% | Day 6 remains 8.1 min | admission remains viable but costly | a berth plan is required only for “prepared,” not for delay/refusal | newcomer treatment time, berth occupancy, Air load |
| Expedition reward | required route component present → missing | East fails: quiet berths blocked by relay chain | West fails: Water treatment blocked by pump seal | unresolved project adds review, not a longer mission | **Both routes infeasible by design** | the required objective is mandatory; optional loot is not | node comprehension, retreat rule, serialization |
| Highball benefit | 25%, 35%, 50% | all one-use cases viable; WU saved 5.2–8.67 | all paired cases viable | no final multiplier selected; faster animation may reduce observation | zero-use baseline passes; one use creates margin | never | perceived speed, consent, cost salience, camera readability |
| Highball repayment | kept 6 WU; breach 11 WU; two uses 18 WU | breach viable at 18.5%; two-use net WU −6.27 | breach viable at 16.1% | repayment may add one explanation/assignment choice | escalation defeats indefinite spam without auto-failing the week | no | whether promises are remembered and costs feel attributable |

## Fragile assumptions

### High severity

1. **Resident work throughput:** a 10% loss fails both routes. The baseline's apparent 15–20% buffer is not a 15–20% global tuning cushion because work arrives behind dependencies and hard Day 7 proofs.
2. **Construction estimates:** +15% fails both routes. Art/animation cannot quietly expand interaction ceremony or labor stages.
3. **Food baseline:** +20% fails both routes. The slice has little Food resilience and must forecast this clearly.
4. **West travel:** a plausible spatial increase makes West fail while East survives. Exact station geometry is a production and balance gate.
5. **Required annex component:** missing or duplicate resolution directly changes route feasibility. Save idempotency and objective clarity are release-critical.

### Medium severity

- East Water is deliberately tight and sensitive to consumption.
- Prepared storm results tolerate intensity and lead variation, but unprepared combined extremes were not accepted as a balance promise.
- Juna prepared admission needs real rest capacity. Temporary admission is allowed but carries later Stress/relationship work not fully modeled.
- The active-day twelve-decision budget could be tiring even though it fits the numerical time target.
- Highball's 35% candidate has only 0.74 net WU before Charge, Materials, Stress, and player attention; its perceived value may differ sharply from the arithmetic.

## Model-driven retuning triggers

Reopen the canonical JSON rather than patching prose if any prototype finds:

- median resident useful capacity below 12 WU equivalent;
- West travel/hauling above the tested typical allowance;
- a standard room requiring more than 14 WU or a major reclamation more than 32;
- first improvement later than five minutes;
- first safe stop later than seven minutes;
- ordinary accessible session longer than twelve minutes;
- less than two clear storm interruption points in an unprepared run;
- an unavoidable new injury despite correct preparation;
- Active or Delegated mode unable to secure the required component;
- Juna required for route completion or producing more labor than her admission consumes during the slice;
- any save/reload changing a committed outcome or granting a reward twice.

## Required prototype measurements

### Spatial and construction prototype

Measure average and 95th-percentile travel, vertical travel, material trips, congestion, path failures, worker handoff, setup, and interruption. Test East and West in compact, typical, and poor-but-valid layouts.

### Mobile timing prototype

Instrument notice, focus, reading, choice, confirmation, response, session length, decision count, safe-stop interval, reduced-motion transition, large-text wrapping, and tutorial skip. Record pause usage rather than interpreting it as failure.

### Utility incident prototype

Measure whether players can distinguish Power from Charge, identify a failing Air/Water link, predict the next cascade stage, and interrupt it without rapid input. Validate symbols plus color and plain-language forecasts.

### Expedition prototype

Measure route comprehension, node-save confidence, carry choice, wrong-tool alternative, retreat, Active-versus-Delegated control, and whether 4.8 active minutes feels supportive rather than like a second game.

### Save-fault prototype

Force termination before and after every transaction in `15_FIRST_SESSION_AND_SAFE_STOPS.md`. Verify state equality, monotonic progress, one debit, one reward, and zero closed-app advancement.

## What the simulation does not prove

It does not prove enjoyment, balance, comprehension, tactile construction, emotional investment, camera comfort, readable 2.5D staging, animation quality, actual device performance, or final session pacing. It uses a travel allowance instead of pathfinding, four conditions instead of full resident behavior, bounded authored incidents instead of a complete weather architecture, and a graph abstraction instead of final nightrun presentation.

Passing scenarios authorizes a prototype; it does not authorize production-scale content expansion.

## Prompt 3 sensitivity amendment

The original Prompt 2 percentages above remain historical evidence for the construction model. Prompt 3 adds fragility around outcome meaning, condition stacking, Medicine, Materials, Charge conversion, Relay response, incident reserve, and deterministic strain. Current baselines pass Full Proof, but prepared Day 5 leaves zero daily/phase slack and zero minimum hard-deadline days. Any geometry-derived travel increase must rerun all 176 cases.

Additional retuning triggers:

- a stock response creates value rather than trading Hunger, Stress, Materials, time, or opportunity;
- East’s deliberate Water response overtakes West’s Water security;
- a critical resident appears in productive capacity;
- a forecast needs more than two taps to name the failing link;
- two major incidents overlap or a cascade exceeds three systems;
- a Highball candidate becomes mandatory, repeat-profitable, or medically applicable;
- a save/reload changes treatment, incident, strain, promise, or outcome class.

Required Prompt 4 measurements are horizontal/vertical travel, carrying, material trips, congestion, evacuation, isolation reachability, and path failure. Prompt 5 must measure promise/refusal consequences; neither may silently increase the 12-WU resident base.
