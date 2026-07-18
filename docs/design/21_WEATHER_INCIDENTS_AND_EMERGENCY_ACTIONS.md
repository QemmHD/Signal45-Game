# Signal 45 — Weather, Incidents, Emergency Actions, and Highball

> Prompt 3 contract. The framework creates bounded, forecast pressure and recoverable aftermath. It is not a full conflict, engineering, or weather simulation.

## Weather set for The First Count

| State | Forecast | Shelter/utility pressure | Preparation | Response | Recovery presentation |
|---|---|---|---|---|---|
| Swelter Heat | thermometers and civic bulletins; high confidence | closes daytime surface access; may raise Water estimate | pack water; wait for night | retreat underground | white-orange entrance glare, metal expansion, heat icon |
| Cinder Front | Listening Post burst plus filter readings; medium-high confidence and two-stage lead | Air → Power → Water only | filter service, load plan, Water isolation | service/isolate/evacuate, shed, Charge | cinder ingress, dimming, filter residue, fan strain |
| Ash-wash aftermath | runoff and inspection; measured, one-stage lead | one Water/storage warning after peak; not a second major crisis | isolate drain, cover storage | cleanup or bypass | gray water marks, bagged filter media, pump cycling |

The cinder storm is the one Day 5 major crisis. Ash-wash is queued recovery pressure rather than another simultaneous crisis.

## Reusable incident record

Every incident instance contains:

- `incident_id`, family, source, trigger, section, affected room/object;
- initial warning, confidence, severity, current stage, and escalation allowance;
- affected stocks, utilities, residents, and access;
- propagation rule and maximum depth;
- auto-pause tier and immediate responses;
- generated work orders, Materials/components, and equipment;
- evacuation and isolation rules;
- recovery work, physical aftermath, human-consequence placeholder, and delayed consequence;
- completion/failure conditions, transaction IDs, status, and save state.

Representative families are Power instability, Air contamination, Water contamination, Structural instability, Equipment breakdown, and Medical emergency. Intrusion, theft, sabotage, and internal violence remain architecture-only placeholders; Prompt 3 does not design conflict resolution.

## Incident stages

1. **Warning** — cause and horizon appear.
2. **Active** — the first effect is present; responses remain open.
3. **Severe** — auto-pause when Health, structure, trapping, or essential utility is endangered.
4. **Recovery** — propagation has stopped; repair/treatment remains.
5. **Resolved** — functional recovery transaction commits once; aftermath may remain visible.

No incident may skip directly from hidden state to serious harm. Interrupting an incident records the response, isolation/evacuation state, stopped propagation, and recovery work.

## Scheduler and alert budget

The slice permits at most one live major crisis and two queued minor warnings. A new major incident queues while a major is unresolved. Irreversible choices queue safely; relationship scenes wait for a safe window.

| Day | Major allowance | Minor allowance | Medical | Human scene | Hope/recovery | Intent |
|---:|---:|---:|---:|---:|---:|---|
| 1 | 0 | 1 | 1 | 0 | 0 | Teo examination only; no overload |
| 2 | 0 | 1 | 1 | 0 | 0 | preventable risk/medical follow-up |
| 3 | 0 | 1 | 0 | 0 | 0 | expedition focus |
| 4 | 0 | 1 | 0 | 1 | 0 | Relay Load Test and forecast |
| 5 | 1 | 2 | 1 | 0 | 0 | Cinder Front only major crisis |
| 6 | 0 | 1 | 1 | 1 | 0 | Juna/admission and recovery |
| 7 | 0 | 1 | 1 | 1 | 1 | resolution and earned hope |

Allowances are ceilings, not content quotas. Routine wear should not constantly interrupt.

## Day 5 bounded cascade

```text
Cinder Front
  -> Air filter/load pressure
  -> Power margin shortfall
  -> Water pumping/treatment impairment
```

At each active stage the card reports current cause/effect, likely next effect, stages or WU before escalation, affected residents, interruption, known cost, and uncertainty.

- Fully prepared play stops after Air.
- Partial preparation may reach Power.
- Unprepared but responsive play may reach Water.
- Extended neglect reaches all three and can produce Shelter Failure.

The maximum affected-system count is three. The cascade cannot add Structure, start a second major crisis, skip warning, or cause unseen death. Prepared and responsive paths retain recovery; neglect remains a real failing case.

## Auto-pause

Auto-pause occurs when:

- Health may enter serious deterioration;
- Structure becomes Critical/Closed;
- a utility cascade reaches a severe stage;
- a resident may be trapped or must evacuate;
- admission, promise, or irreversible action requires confirmation;
- an expedition reaches a consequential committed node.

Routine completions, minor wear, and informational forecasts do not repeatedly stop the game. Every decision can be manually paused and accessibility settings may extend decision time without changing simulation results.

## Emergency actions

| Action | Immediate benefit | Immediate/delayed cost | Reversible | Abuse prevention |
|---|---|---|---|---|
| Ration Food | lower next issue | visible smaller meal; Hunger and escalating Stress | next meal | consecutive-day escalation; no free stock |
| Restrict Water | lower demand | treatment/cleaning constraints; Stress/dehydration context if repeated | next issue | two-day safe limit before stronger consequence |
| Shed Load | immediate Power relief | named room/light off; work or comfort loss | when margin returns | shed function supplies no benefit |
| Discharge Charge | preserves one connected load | finite reserve and conversion loss | no | connection and per-stage limit |
| Isolate Section | stops configured propagation | room/tasks/branch suspended; later inspection | after clearance | isolated function remains unavailable |
| Evacuate | removes residents from exposure | crowding, Fatigue/Stress, lost work | after clearance | evacuees cannot work in closed section |
| Temporary Filter/Bypass | reduces one stage | Materials/component plus later permanent repair | no | deterministic repair obligation |
| Defer Project | releases future labor pressure | proof/ambition delay; reservation rules persist | before hard deadline | delivered value is not refunded |
| Temporary Room Conversion | creates care/rest/storage capacity | displaces existing room function; restoration | yes, with work | no simultaneous original benefit |
| Highball Order | pulls work before a deadline | Fatigue, Charge, wear, Stress, strain, rest promise | no | eligibility, strain, escalating repayment |

All actions save before commitment and after logical state mutation. Animation is presentation only.

## Recovery as gameplay

Stopping danger does not erase it. Recovery can include filter cleanup, branch inspection, tank isolation/flush, braces, treatment observation, restoration of a converted room, lost work, depleted reserve, and a delayed human response. Repaired rooms and residents using the repair can supply an earned hope beat without generating resources.

## Highball purpose

Highball is a deadline-shifting tool. Its useful cases are completing storm preparation before the front or restoring a system before the next incident stage. It is not a permanent production buff or required optimal loop.

The model continues to test **25%, 35%, and 50%** timing candidates. No production multiplier is selected.

### Guaranteed cost architecture

The first use consumes named Charge/Materials, creates Fatigue and Stress placeholders, adds one strain, and creates a rest promise. Consecutive use costs more, adds two additional strain, and requires more repayment. Exact canonical values live only in `model.json`.

| Strain tier | Effect |
|---|---|
| Low | visible wear; no automatic breakdown |
| Elevated | deterministic inspection/repair work |
| Critical | blocks another normal Highball; an explicit emergency override guarantees impairment/repair rather than rolling secretly |

Low-condition equipment adds known strain. Critical Health, untreated critical injury, collapse, unconsciousness, and severe respiratory restriction make the named resident ineligible. A broken rest promise causes later capacity loss, Stress placeholder, and refusal of the next order.

Every guaranteed cost applies regardless of any uncertainty. There is no hidden roulette and no unseen lethal Highball outcome.

### Timing findings

- Baseline East and West need zero Highball uses.
- One pre-deadline use creates useful timing margin but spends reserve and future work.
- Noncritical use pays the same costs for little or no meaningful deadline value.
- Consecutive use produces Recover First in the tested case because inspection/rest pushes the authored hope setup past its hard boundary.
- Low-condition equipment also produces Recover First through declared strain.
- Repeat commitment cannot duplicate acceleration or costs after save/reload.

## Physical and human aftermath requirements

Future runtime states must show dimmed/restored lighting, isolated doors, cinder residue, dirty filter media, marked Water storage, braces/closure tape, open machine panels, occupied treatment space, crowding after evacuation, and residents returning to repaired rooms. Human consequences remain specific placeholders for Prompt 5; no global morality meter is introduced.

## Save and idempotency

Each warning, escalation, interruption, isolation, evacuation, recovery, Highball commitment, strain change, promise, and completion has a stable transaction ID. Recovering an already resolved incident is a no-op. Reloading at every tested incident stage preserves the stage and cannot duplicate a reward. No incident advances while closed.

## Prototype gates

- Measure alert density and whether one-major/two-minor limits feel quiet enough on phone.
- Validate stage readability and response timing in an interactive storm.
- Test visual/auditory distinction between warning, active, recovery, and resolved states.
- Measure Highball’s felt urgency at all three candidate timings before selecting one.
- Revalidate evacuation/access timing with Prompt 4 coordinates.
