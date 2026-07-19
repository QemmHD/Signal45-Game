# Signal 45 — Prompt 3 Survival Simulation Results

> Deterministic feasibility evidence, not a balance or fun claim. Canonical inputs are `model.json` and `scenarios.json`; the complete generated matrix is in `tools/feasibility/reports/`.

## Verification snapshot

- Canonical scenarios: **176**
- Expectations matched: **176**
- Full Proof: **139**
- Recover First: **21**
- Proof Incomplete: **3**
- Shelter Failure: **12**
- Intentionally detected Invariant Error: **1**
- Unexpected quality errors: **0**
- Unit/integration tests: **144 passed locally**
- Deterministic repeat: equal

The expected invariant scenario deliberately injects an impossible state to prove detection. It is not an accepted runtime invariant error.

## Outcome taxonomy

| Class | Survival viable | Slice proof complete | Meaning |
|---|---:|---:|---|
| FULL_PROOF | yes | yes | survival, all mandatory proof, and at least one supported ambitious direction |
| RECOVER_FIRST | yes | no | survival remains viable, but repair/treatment/shortage makes recovery the honest Day 7 direction |
| PROOF_INCOMPLETE | potentially | no | the shelter may live, but a required release-slice mechanic or acceptance proof was not demonstrated |
| SHELTER_FAILURE | no | no | no recoverable Day 7 survival direction remains |
| INVARIANT_ERROR | invalid | invalid | negative/duplicate/malformed/save-divergent or otherwise impossible state |

The convenience `viable` flag is derived: true only for Full Proof and Recover First. A missing celebration no longer masquerades as shelter death.

## Baseline East and West

| Metric | East S01 | West S02 |
|---|---:|---:|
| Outcome | Full Proof | Full Proof |
| Highball uses | 0 | 0 |
| Functional areas | 10 | 10 |
| Food at Day 7 | 11 | 11 |
| Clean Water at Day 7 | 15 | 25 |
| Medicine at Day 7 | 8 | 9 |
| Materials at Day 7 | 34 | 37 |
| Charge at Day 7 | 24 | 24 |
| Aggregate unused project WU | 36.788 | 27.108 |
| Incident reserve, total / unused | 14 / 12 | 14 / 12 |
| Minimum critical-path slack | 0 days | 0 days |

Both routes retain their identity. West has the stronger Water/salvage finish; East retains treatment/rest advantages in its workload and presentation. Neither route needs Highball or Juna labor.

## Schedule resilience

Aggregate unused WU is not treated as the safety margin. Baseline critical-day data is:

| Day | East daily uncommitted | West daily uncommitted | Unused incident reserve | Interpretation |
|---:|---:|---:|---:|---|
| 1 | 15.656 | 14.732 | 2 | onboarding work leaves a large stop/recovery window |
| 2 | 2.000 | 2.000 | 2 | small visible contingency; route critical path is active |
| 3 | 2.000 | 2.000 | 2 | small contingency around expedition work |
| 4 | 4.143 | 2.014 | 2 | Relay/forecast preparation remains feasible |
| 5 | 0.000 | 0.000 | 0 | prepared storm consumes the full configured response reserve and project slack |
| 6 | 2.000 | 2.000 | 2 | Juna/recovery day retains minimal contingency |
| 7 | 22.989 | 16.362 | 2 | ending and recovery carryover window |

Day 5 is the fragile point. It is an intended major-crisis day, not evidence of a normal-day buffer. The prepared profile costs six incident WU: two come from reserved incident capacity and four from explicit response/project capacity. The model must be revalidated if Prompt 4 travel or Prompt 5 human scenes add Day 5 labor.

Reported metrics now include aggregate unused WU, minimum daily uncommitted WU, minimum phase slack, per-project hard-deadline slack, incident reserve, carryover, optional-work capacity, and emergency recovery capacity.

## Food response cases

| Case | Outcome | Day 7 Food | Cost |
|---|---|---:|---|
| +20% use ignored, S104 | Shelter Failure | 5.4 | below 6-unit minimum reserve |
| +20% plus ration response, S105 | Full Proof | 7.8 | restricted issues, Stress/Hunger, one WU response effect |
| +20% plus trade/expedition response, S106 | Full Proof | 9.4 | Materials or carry opportunity cost |
| repeated rationing, S111 | Recover First | viable stock | Prolonged Hunger and escalating Stress require recovery |

No response creates Food. One missed meal does not cause immediate critical Health loss.

## Water response cases

| Case | Outcome | Day 7 Clean Water | Meaning |
|---|---|---:|---|
| East +20% ignored, S107 | Shelter Failure | 6.6 | below 8-unit minimum |
| East +20% restriction, S108 | Full Proof | 12.52 | resident/treatment cost; one response WU |
| East reserve plus deferral, S109 | Recover First | 10.44 | survival retained; richer ambition deferred |
| West comparative pressure, S110 | Full Proof | 12.6 | retains a slight Water advantage under the same pressure |

East response does not become better than West Water security.

## Medicine, Materials, and Charge responses

- Medicine priority S171 protects stabilization, defers one nonurgent use, adds Stress and one recovery day, and yields Recover First at 5 Medicine. Ignored pressure S174 ends at 1 and fails.
- Materials deferral S172 preserves 20 Materials, uses an earned minimal hope beat, and yields Recover First. Ignored shortage S175 ends at 3 and fails.
- Charge load shedding S173 retains Full Proof at 10.5 Charge. Ignored severe Charge shortage plus storm neglect S176 reaches Shelter Failure.

## Relay Load Test

All three Day 4 choices pass:

- Charge S112 covers the 0.7 live deficit and draws 1.111 reserve after loss; final Charge is 22.889.
- Shed S113 visibly dims the canonical Platform Work Lamp, spends no Charge, and restores that same consumer automatically.
- Delay S114 spends no stock but reduces warning lead by one stage.

Save/reload preserves the Power/Charge distinction and cannot repeat the debit.

## Medical cases

The suite executes Teo examination, early and delayed respiratory exposure, minor and serious injury, critical work restriction, waterborne illness, Medicine reservation, interruption, resume, completion, save/reload, and over-heal prevention.

Results establish:

- critical or explicitly incapacitated residents produce zero project WU;
- self-evacuation remains possible where conscious and never counts as project work;
- severe respiratory and serious injury treatments block productive work;
- interrupted treatment retains its Medicine/Water reservation;
- completion is idempotent and Health is capped at the pre-condition maximum;
- no single missed slice warning causes death.

The all-medically-unavailable case names the missing shelter fallback and fails; it does not force residents to work.

## Incident cases

All six representative families execute through the shared schema. Tests verify warning, stage progression, interruption, isolation, evacuation, recovery, stage save/reload, and a single recovery claim. A second major incident queues. A minor warning may queue. The configured cascade rejects a fourth affected system.

A red-team test found repeat incident recovery could append another completion transaction. Recovery is now explicitly idempotent; the same resolved incident is returned unchanged.

## Storm results

| Profile | Outcome | Cascade | Response WU | Charge draw | Water loss | Medicine | Recoverable |
|---|---|---|---:|---:|---:|---:|---:|
| Prepared S142 | Full Proof | Air | 6 | 0 | 0 | 0 | yes |
| Partial S143 | Full Proof | Air → Power | 10 | 2.222 | 2 | 1 | yes |
| Unprepared responsive S144 | Full Proof | Air → Power → Water | 16 | 7.778 | 2 | 2 | yes |
| Extended neglect S145 | Shelter Failure | Air → Power → Water | 24 | 10 | 9 | 3 | no |

The prepared case materially reduces harm. The responsive unprepared case is costly but recoverable. Extended neglect remains a real failure. Every profile has warning and interruption; the cascade never exceeds three systems or one major crisis.

## Highball results

The 25%, 35%, and 50% candidates remain provisional; no production multiplier is selected. Representative 35% cases show:

| Case | Work pulled forward | Repayment/strain result | Outcome |
|---|---:|---|---|
| storm preparation S151 | 2.333 WU | 6 later WU; low strain; net weekly −3.667 | Full Proof through timing |
| noncritical S152 | 0 | 6 later WU; net −6 | Full Proof but clearly wasteful |
| route, promise kept S153 | 6.741 | 6 later WU; low strain | Full Proof |
| route, promise broken S154 | 6.741 | 11 later WU; future refusal | Full Proof with lasting cost |
| consecutive S155 | 11.734 | 21 later WU; elevated strain/inspection; net −9.266 | Recover First |
| medically ineligible S156 | 0 | order rejected; no costs/benefit | Full Proof without Highball |
| low-condition equipment S157 | 11.734 | critical strain, 24 later WU, next use blocked | Recover First |

Highball remains optional, deterministic, save-safe, and nonlethal. Repeating a committed order cannot duplicate work or costs.

## Recover First and hope

Missing only the five-WU authored hope setup uses the already earned relit platform sign at zero additional WU. S93 and S168 produce Recover First, not Shelter Failure. The fallback creates no stock and does not erase outstanding repair/treatment. Full setup S169 remains Full Proof and visibly richer.

## Save and resume

Existing Prompt 2 transaction probes still pass, and Prompt 3 adds treatment interruption/completion, Relay choice, incident recovery, hope fallback, emergency action, strain, and stage snapshots. Tests confirm:

- no duplicate resource, refund, treatment, incident reward, expedition reward, or Highball benefit;
- partial construction and reservation persist;
- Power/Charge, treatment, incident, promise, and strain states round-trip;
- mid-animation closure uses committed state;
- seven closed days advance nothing.

## Expected failures retained

The model still rejects extended storm neglect, ignored Food/Water/Medicine/Materials/Charge pressure, severe work/cost sensitivity cases, route-component proof loss, and the injected invariant. Recover First does not turn all adverse cases into passes; Proof Incomplete remains a QA failure.

## Red-team corrections

| Finding | Severity | Correction |
|---|---:|---|
| one viability boolean confused proof loss with shelter death | high | five-class taxonomy and derived flags |
| five-WU hope setup could turn hope into mandatory burden | high | earned 0–2 WU fallback; full version remains richer |
| individual emergency minimum forced critical residents to work | high | zero productive WU restrictions plus shelter-pool safeguard |
| aggregate weekly buffer hid Day 5 zero slack | high | separate daily, phase, critical-path, reserve, and carryover metrics |
| adverse stock tests had no responding counterparts | high | explicit ration, restriction, priority, deferral, and load-shed cases |
| Charge/Power distinction lacked a controlled teaching moment | medium | Day 4 Relay Load Test with three viable responses |
| incident completion could repeat its transaction | high | resolved recovery is a no-op; idempotency test added |
| richer phase output omitted emergency actions/promises | medium | day and phase snapshots now report both |

Refuted: the 35% candidate is not a selected production value; it remains only one sensitivity point. Refuted: prepared storm using six response WU is not hidden work; all seven days reconcile gross capacity exactly in S170.

## Model limits and mandatory revalidation

This model proves arithmetic consistency, bounded causality, explicit outcome meaning, recovery logic, and serialization. It does not prove comprehension, emotional credibility, tension, tactility, camera readability, or actual pacing.

Prompt 4 revalidated average/essential travel, material and heavy carry, congestion proxy, access, evacuation, and utility-node location. Coordinate factors replace the abstract branch; no extra Day 5 work or resident capacity was added. Actual seconds, animation and congestion still require a graybox, and any measured overrun must improve siting/staging or reduce/split work before changing the 12-WU base.
