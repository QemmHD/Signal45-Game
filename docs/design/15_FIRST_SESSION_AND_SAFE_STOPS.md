# Signal 45 — First Session and Safe Stops

## Opening objective

The first session teaches one complete shelter action, not the full game. The player repairs the platform lamp, sees a named resident respond, reads one forecast, and reaches a committed save. Teo's existing respiratory exposure introduces Health and treatment context without forcing a new injury.

Canonical milestone budgets are in `tools/feasibility/data/model.json`; these are design targets pending playable measurement.

## Minute-by-minute opening

| Time | Player experience | Teaching class | Committed result |
|---|---|---|---|
| 0:00–0:30 | Side-cutaway Overview establishes four working/damaged areas, residents, blockages, and darkness | Demonstrated atmosphere; no system lecture | opening state already saved |
| 0:30–0:48 | Lamp warning centers the damaged platform object; player chooses to inspect | Practiced selection; first meaningful choice at 0.8 min | selection only, reversible |
| 0:48–1:12 | Room Focus reveals wiring and an enlarged target; player assigns one resident | Practiced Focus and assignment by 1.2 min | assignment transaction |
| 1:12–1:27 | Resident acknowledges and begins; Pause control is shown | Demonstrated Pause; visible response by 1.45 min | project activation/reservation saved |
| 1:27–3:00 | Short installation proceeds; Teo's exposure icon and triage cot appear contextually | Demonstrated one Health state; Medical path available | partial work commits incrementally |
| 3:00–4:06 | Lamp completes and overview visibly warms | Practiced return to Overview; first improvement at 4.1 min | completion benefit committed before celebration |
| 4:06–5:12 | One Food forecast and one Power connection warning explain “why” and “next” | Demonstrated, not optimized | forecast is read-only; warning state saved |
| 5:12–6:06 | Player accepts the Day 1 ledger; Listening Post and blockages remain visible but inactive | Teased future systems; practiced safe stop | end-of-day ledger committed at 6.1 min |

The player may continue into another safe segment, but the game clearly states that closing now pauses everything.

## Strict teaching budget

### Practiced

The player must perform:

- select a room or damaged object;
- enter Room Focus;
- assign one resident;
- confirm one repair or installation;
- return to Overview;
- reach a safe save.

### Demonstrated

The game shows once with light guidance:

- one Food forecast only;
- one Power connection warning only;
- Teo's contextual Health exposure;
- Pause.

### Teased

Visible but not mastered:

- Listening Post;
- East and West blockages;
- Air, Water, and Structure overlays;
- Highball;
- Nightrun.

### Deliberately withheld

- full signal-board choices;
- admission;
- utility-priority optimization;
- multi-stage cascades;
- detailed expedition equipment;
- full room repurposing;
- relationship management;
- Medicine, Materials, and Charge mastery.

The opening never asks the player to learn all five stocks or all four utilities. Only Food and Power receive explanatory depth.

## Timing variants

| Variant | Safe-stop target | Behavior |
|---|---:|---|
| Normal motion | 6.1 min | short smooth Overview/Room Focus transitions |
| Reduced motion | 5.8 min | quick focus change; no long fly-through |
| Large text | 6.9 min | panels reflow and reading allowance increases; decisions still pause |
| Tutorial skip | 3.4 min | preserves required assignment and completion; removes explanatory holds |

Combined reduced-motion and large-text budgeting keeps an ordinary day around 8.1 minutes, but only device testing can validate real wrapping and reading time.

## Interruption and resume

- Backgrounding first commits the current transaction boundary and pauses the simulation.
- A preview returns as an uncommitted preview.
- Activated work resumes with its stable project ID, reservation, exact remainder, and assigned priority.
- A completion animation may replay, but its benefit cannot fire twice.
- A blocking choice reopens on the same options unless the player had already committed it.
- The return notice says, **“The station was paused. No time passed while you were away.”**
- Food, Water, construction, incidents, resident conditions, and expeditions do not advance while closed.

## Safe transaction contract

The state ledger, never an animation, is authoritative. Every committed action has a stable action ID; every resource or reward grant has a claim ID. The following table covers all slice mutation boundaries.

| Boundary | Save before / commit after | Reversible | Resume state | Duplication and mid-animation rule |
|---|---|---:|---|---|
| Blueprint preview | yes / no | yes | return to uncommitted preview | no mutation; discard incomplete preview |
| Project activation | yes / yes | yes until delivery | stable active project ID | repeated activation ID is ignored; committed state wins |
| Material reservation | yes / yes | yes by cancellation rules | reservation remains attached | reservation ID prevents a second debit; ledger outranks carry animation |
| Material delivery | yes / yes | no | delivered stage remains | delivery ID prevents replay; animation never creates inventory state |
| Partial construction | progress checkpoint / yes | no rollback | exact WU remainder | monotonic progress sequence; last committed increment wins |
| Project completion | yes / yes | no | room and benefit persist | completion/reward IDs fire once before celebration |
| Project cancellation | yes / yes | no | canceled state and one refund | refund claim ID prevents duplicate refund |
| Room repurpose | yes / yes | no after confirm | new purpose and displaced tasks persist | repurpose action ID; visual swap follows commit |
| Highball confirmation | yes / yes | no | cost, promise, acceleration, due rest persist | order ID; acceleration animation derives from committed state |
| Promise creation | yes / yes | no | promise and due phase persist | promise ID; dialogue is presentation only |
| Signal commitment | yes / yes | no | selected signal, confidence, and expiry persist | commitment ID; tuning animation follows commit |
| Signal expiry | phase checkpoint / yes | no | expired/processed state persists | expiry ID fires once; clock display is not authority |
| Expedition loadout | yes / yes | yes before departure | exact loadout restored | loadout revision ID; departure is a separate transaction |
| Expedition node entry | yes / yes | no | resident at committed node | node visit sequence ID controls position |
| Expedition irreversible action | yes / yes | no | site mutation and claim persist | site-action and reward IDs prevent duplicate loot |
| Expedition retreat | yes / yes | no | retreat path and partial result persist | retreat ID; return animation cannot resolve twice |
| Trader transaction | yes / yes | no | exact exchange persists | exchange and reward IDs debit/credit once |
| Juna admission decision | yes / yes | no | agreement/refusal, costs, capacity, and aid persist | decision ID; gate animation follows commit |
| Incident escalation | yes / yes | no | exact bounded stage persists | stage sequence ID; effects derive once from stage |
| Treatment start | yes / yes | no | patient, cost, condition, and end rule persist | treatment ID; animation cannot consume again |
| Treatment completion | checkpoint / yes | no | recovered/new condition persists | completion ID; recovered state controls presentation |
| Phase transition | yes / yes | no | exact new phase resumes | phase/day tuple prevents repeat; transition can replay safely |
| End-of-day ledger | yes / yes | no | next day starts from accepted ledger | day-ledger ID prevents double consumption or production |

## Save-probe evidence

Scenarios S45–S54 round-trip partial construction, reservation, storm stage, pre/post Highball, active expedition, irreversible expedition reward, pre/post admission, and treatment. Each verifies byte-equivalent canonical state after JSON serialization, idempotent reward claims, and no offline advancement. Unit tests independently cover phase state, completion/refund IDs, and week-long backgrounding.

An application close after a committed mutation but before its animation restores the committed mutation. A close before commitment restores the prior state or safe preview. No resolution is inferred from how far an animation appeared to play.

## Acceptance and prototype gate

Prompt 2 accepts the first-session plan because the modeled choice, assignment, response, improvement, forecast, and safe stop fall within their requested bounds. A playable mobile build must measure each milestone. If large-text safe stop exceeds seven minutes or skip mode omits the assignment/completion transaction, the opening must be simplified before adding more teaching.

## Prompt 3 transaction amendment

The opening remains unchanged. Later safe boundaries now include Relay choice, Medicine/Water treatment reservation, treatment interruption/completion, incident warning/escalation/interruption/recovery, emergency action, isolation/evacuation, hope fallback, Highball strain, and promise state. Each saves before irreversible confirmation and after logical commitment. Repeating treatment completion, incident recovery, Charge discharge, refund, expedition reward, or Highball commitment cannot duplicate value. Phase/day output records active promises and available emergency actions; no closed-app time advances.
