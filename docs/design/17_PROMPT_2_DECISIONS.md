# Signal 45 — Prompt 2 Decisions

## Stage outcome

Prompt 2 locks a deterministic feasibility baseline for **The First Count**. It adds no full game implementation, final art, final resident AI, or Prompt 3 system expansion. Canonical machine data is `tools/feasibility/data/model.json`; scenario inputs are `tools/feasibility/data/scenarios.json`.

## Corrections to Prompt 1

### P2-D01 — Day 2 injury is conditional and preventable

- **Contradiction:** Prompt 1 guaranteed a minor construction injury to teach Medical, conflicting with warning and agency requirements.
- **Evidence:** deterministic risk scenarios produce no injury at hazard score 0 and a minor injury only after two visible hazards are accepted.
- **Smallest correction:** Teo's existing respiratory exposure guarantees examination/treatment teaching. A new injury occurs only through a forecast risk path.
- **Consequence:** good preparation can prevent all new Day 2 injuries; Medical remains taught.
- **Revisit:** playable warning comprehension test.

### P2-D02 — Day 1 receives a strict teaching budget

- **Contradiction:** Prompt 1 presented Overview, Focus, selection, assignment, five stocks, four utilities, actions, offline rules, signals, and improvement with similar weight.
- **Evidence:** the first-session budget fits required milestones only when six actions are practiced, four facts demonstrated, five systems teased, and advanced systems withheld.
- **Smallest correction:** explain only one Food forecast and one Power warning. Do not teach Medicine, Materials, Charge, Air, Water, or Structure mastery.
- **Consequence:** first choice at 0.8 minutes, improvement at 4.1, safe stop at 6.1.
- **Revisit:** instrumented onboarding build.

### P2-D03 — Storm cascade is explicitly bounded

- **Contradiction:** Prompt 1's “power, air, water, and structural pressure” could read as simultaneous or unlimited propagation.
- **Evidence:** Air → Power → Water is sufficient to create prepared, partial, unprepared, and failed states.
- **Smallest correction:** one cinder pressure, at most three systems, one major crisis, stage interruption, minor queue.
- **Consequence:** Structure can remain a preparation/reclamation concern without becoming a fourth live storm link.
- **Revisit:** incident comprehension prototype.

### P2-D04 — Highball stays provisional and optional

- **Contradiction:** an exact-feeling speed result could be mistaken for validated balance.
- **Evidence:** zero-use East/West pass; 25%, 35%, and 50% candidates all pass with different work margin. Promise breach and consecutive use impose later loss.
- **Smallest correction:** keep 35% only as a model baseline, label all candidates provisional, and select none for production.
- **Consequence:** competent play requires zero uses; two consecutive 35% uses have negative net WU before other costs.
- **Revisit:** playable perception and promise-attribution test.

### P2-D05 — Juna is neither moral score nor route key

- **Contradiction:** newcomer labor or Water aptitude could secretly make admission the correct choice.
- **Evidence:** eight admission/delay/refusal cases pass; zero-work-through-Day-7 passes; no-admission baselines pass both routes.
- **Smallest correction:** charge stabilization, consumption, rest, Air, and aid immediately; credit at most limited later work.
- **Consequence:** preparedness changes cost, not moral rank. Delay/refusal includes concrete aid and outside-contact consequences.
- **Revisit:** Prompt 5 human consequence model.

### P2-D06 — Camera remains presentation-only for simulation

- **Contradiction:** none in foundation, but timing work could have implied a new focus simulation.
- **Evidence:** every result is invariant to zoom and Room Focus.
- **Smallest correction:** budget selection/observation time only.
- **Consequence:** Overview and Room Focus observe one live state; no redesign.
- **Revisit:** camera comfort prototype, not balance code.

## Model-driven decisions

### P2-D07 — Use target dates plus hard carryover dates

The first model treated Day 4 and Day 6 targets as immediate failure cliffs. Common mistakes and temporary absences then failed even with sufficient weekly capacity. Projects now have a visible target and a hard completion checkpoint one phase/day later where appropriate. A target miss queues pressure; a hard miss gives the exact failure. This is recovery, not hidden leniency.

### P2-D08 — Move route-Highball promise repayment to Day 5

Repaying promised rest before the accelerated route task's own hard boundary erased the order's immediate purpose. Repayment now occurs after the route window, while still reducing weekly availability and competing with storm work.

### P2-D09 — Shift four Day 7 WU into recovery after an unprepared storm

Unprepared West initially failed despite the intended “serious but normally recoverable” rule. The smallest correction explicitly defers four WU of noncritical routine operation to visible recovery. The player sees the shift; no labor is created. Extended neglect still fails.

### P2-D10 — Increase post-storm proof workload rather than pad timers

An early baseline had excessive unused labor. Workshop, Storage, Triage, Forecast Board, recovery, and hope work were raised within their class ranges. Baselines now land at 20.4% East and 15.8% West while still proving one mistake recovery.

### P2-D11 — Keep seven families while ending at ten areas

Ten areas are achieved through reclamation, an upgrade, repurposing, and repeated family instances. The model does not create ten independent room systems.

### P2-D12 — Required expedition value is route-specific but mode-neutral

East needs an electrical relay; West needs a pump seal. Active and Delegated modes use the same annex graph, can obtain the required route component, and have no exclusive reward. Active buys control and time, not superior loot.

### P2-D13 — Treat work throughput, Food, and West travel as critical gates

Both routes fail a 10% work reduction, a 15% construction increase, and a 20% Food increase. West also fails the tested travel increase; East fails the tested Water increase. These were not tuned away because the model must be able to reject the plan.

### P2-D14 — Consecutive Highball charges every use

The first simulator implementation accelerated repeated uses but charged only first-use cost. Red-team testing found the mismatch. Each use now records its own escalating Charge, wear, Fatigue, Stress, and rest cost; the two-use case has negative net weekly work value.

## Rejected alternatives

- A model that auto-adds resources or WU until every scenario passes.
- A guaranteed injury for tutorial coverage.
- Per-second Food and Water drain.
- Exact footstep/path simulation before station geometry exists.
- A fourth simulation speed.
- Separate reward tables for Active and Delegated expeditions.
- Highball as a mandatory deadline tool or unbounded throughput multiplier.
- Juna as an instant Water specialist or free fifth worker.
- Unlimited storm propagation or simultaneous major crises.
- Treating the optional Platform Lighting Upgrade, Visitor Screen, or Relay Upgrade as hidden mandatory work.
- Eight to ten unique room systems for eight to ten functional areas.

## Red-team findings and resolutions

| Perspective | Finding | Severity | Resolution / evidence |
|---|---|---:|---|
| New player | Day 1 originally taught too much | High | strict practiced/demonstrated/teased/withheld budget; only Food and Power explained |
| Mobile player | Active day reaches twelve decisions | Medium | kept optional and within 12.3-minute long-session budget; requires device test |
| Base builder | Hard target dates made recovery illusory | High | separate target and hard checkpoints; mistake cases now pass |
| Survival player | Guaranteed injury violated preparation | High | deterministic visible hazard score; Teo supplies no-injury tutorial |
| Min-maxer | consecutive Highball cost was not actually applied | High | code fixed; S73 and unit test verify escalating costs and −6.27 net WU |
| Min-maxer | unprepared scenario looked cheap because prep work was omitted | Medium | accepted only as an incident-isolation test; docs compare harm costs, not raw free buffer |
| Production lead | ten areas risked ten systems | High | seven families, repeated forms, upgrades, and repurpose locked |
| Accessibility | large text could threaten safe-stop target | Medium | budget reaches 6.9 minutes; hard revalidation trigger at seven |
| Adversarial tester | test compared East and West expedition components as identical | Medium | refuted assumption; invariant is same graph/mode value within a route, while components intentionally differ by route |
| Adversarial tester | prepared load shedding did not spend Charge | Low | refuted as valid preparation; discharge test moved to unprepared case |
| Adversarial tester | four scenario pairs initially produced identical normalized outputs | Medium | preparation now spends explicit work, Delegated policy is serialized, storm strategies differ, and Medical tutorial path is reported; final audit finds zero output-duplicate groups |
| Save tester | animation could have become authority | High | transaction ledger, stable action IDs, reward claim IDs, and ten save probes |

## Remaining uncertainty

- The WU scale has not been calibrated to animated tasks.
- Travel allowances have no pathfinding evidence.
- Actual touch, reading, camera, and accessible session times are unmeasured.
- Power/Charge and Air/Water link forecasts may still be confusing.
- The storm state machine is bounded but not yet playable.
- Active nightrun spatial interest and Delegated trust are unproven.
- Emotional promise, refusal, Stress, and relationship consequences are placeholders for Prompt 5.
- The 35% Highball baseline is not a final multiplier.
- Narrative volume, art workload, and mobile performance remain Prompt 1 risks, not solved by arithmetic.

## Prompt 3 entry requirements

Prompt 3 may begin only from this canonical baseline and must:

1. Preserve exactly five primary stocks, four utilities, and four primary resident conditions.
2. Preserve preventable injury, bounded cascades, no offline advancement, mode-neutral expedition objectives, and non-mandatory Highball/Juna.
3. Refine survival consumption, medical conditions, utility states, forecasts, incident transitions, emergency actions, and Highball risk without silently changing WU or project costs.
4. Add or amend canonical JSON and paired scenarios for every changed numeric assumption.
5. Re-run validation, unit tests, mandatory scenarios, and save-fault tests.

Prompt 3 must not yet expand full resident AI, final art, campaign content beyond validation needs, multiplayer, full combat, or additional station maps.

## Prompt 3 completion amendment

Prompt 3 has now executed these entry requirements without changing the 12-WU resident base or adding stocks, primary conditions, utilities, room families, maps, combat, or resident AI. It split the existing ten-WU daily allowance into eight essential plus two incident reserve; replaced the per-person emergency floor with a shelter-pool rule; added five outcome classes, an earned hope fallback, explicit resource responses, the Relay Load Test, named treatment, reusable incidents, and deterministic Highball strain.

Current survival evidence remains 176/176 matched scenarios and 144 passing feasibility tests. Prompt 4 adds 111/111 spatial scenarios and 71 spatial tests, unifies the Platform Work Lamp, corrects physical area counting, and supplies coordinate travel without changing the 12-WU base. Documents 24–30 supersede this handoff for geometry; Prompt 5 is the next entry boundary.
