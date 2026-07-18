# Signal 45 — Resident Conditions and Medical Rules

> Prompt 3 contract. This is a bounded feasibility model, not full resident AI or a medical realism claim.

## Primary condition ceiling

Residents have exactly four permanent primary condition meters: **Health, Hunger, Fatigue, and Stress**. Injury, respiratory exposure, exhaustion, and waterborne illness are contextual conditions that explain meter changes; they are not extra permanent bars.

## Four primary conditions

| Condition | Player bands | Updates at | Productive-work effect | Recovery | UI and save state |
|---|---|---|---|---|---|
| Health | Stable, Strained, Impaired, Critical | incident/treatment stage, rest completion, ledger | 15% at Strained, 35% at Impaired; Critical is an explicit zero-work restriction | named treatment, observation, rest | one meter plus named cause; band and contextual causes serialize |
| Hunger | Fed, Hungry, Restricted, Prolonged shortage | meal issue and ledger | bounded reduction; never zero by itself | later normal issues | meal consequence and next issue forecast serialize |
| Fatigue | Rested, Tired, Exhausted, Collapse risk | work block, Highball, rest, ledger | 15% Tired, 40% Exhausted; Collapse risk blocks assignment | protected rest and promise repayment | next-rest forecast and active promise serialize |
| Stress | Steady, Elevated, High, Acute | incident, ration, promise, recovery scene | bounded reduction; Acute alone is not medical incapacity | safety, rest, kept promises, preferred behavior | sources are named; band and points serialize |

All percentages are provisional canonical inputs. They are not player-facing arithmetic.

## Legible condition combination

The old unrestricted multiplicative approach is rejected. Productive capacity uses:

1. the largest current condition penalty in full;
2. half of each secondary penalty;
3. a total cap of 75%;
4. explicit zero-work restriction states after that arithmetic.

This preserves compounding without hiding a near-zero product of four multipliers. A resident can see “Impaired Health is the dominant restriction; Hunger and Stress reduce the remaining shift.” Critical Health, Collapse risk, or a non-working medical restriction overrides the formula and gives zero productive WU.

## Productive work versus self-preservation

Every resident work profile reports separately:

- `productive_capacity`;
- `current_work_restriction`;
- `emergency_self_action_available`;
- `assignment_eligible`;
- `treatment_required`;
- `evacuation_required`;
- `requires_assistance`.

A medically incapacitated resident may call for help, accept treatment, warn someone, or move toward evacuation if conscious. None of that counts as construction, repair, production, hauling, or treatment labor.

The anti-death-spiral safeguard applies to the **available shelter labor pool**. It asks whether at least one eligible resident can supply the two-WU emergency survival minimum. It never assigns minimum WU to every impaired person. If all residents are medically unavailable, the model reports a named outside/manual fallback requirement and Shelter Failure when none exists; it does not invent forced labor.

## Assignment examples

| State | Productive work | Self-action | Assignment | Assistance |
|---|---:|---:|---:|---:|
| Hungry only | reduced, above zero | yes | eligible | no |
| Exhausted | substantially reduced | yes | eligible/light duty until Collapse risk | context-dependent |
| Critical Health | zero | usually yes | ineligible | yes |
| Severe respiratory restriction | zero | yes if conscious | ineligible | yes; evacuate |
| Collapse | zero | yes if conscious | ineligible | yes |
| Unconscious | zero | no | ineligible | yes; evacuate |

## Contextual conditions in The First Count

| Condition | Visible cause and warning | Severity path | Work/movement restriction | Named care | Recovery |
|---|---|---|---|---|---|
| Respiratory exposure | degraded Air, cinder load, cough/exposure icon | warning → limited → severe → evacuate | limited avoids dusty work; severe blocks work and evacuates | 1–2 Medicine, 1–2 Water, triage/stable treatment, capable staff | one to two days |
| Minor injury | accepted forecast construction risk | warning → minor → impaired | light duty | 1 Medicine, 1 Water, four medical WU | one day |
| Serious injury | multiple visible risks or severe warned incident | warning → serious → critical → stabilized | zero work; assisted movement | 2 Medicine, 2 Water, six to eight medical WU | two to three days |
| Exhaustion | Highball, broken rest, sustained work at Collapse risk | tired → exhausted → collapse risk → resting | zero at Collapse risk; self-evacuate to rest | Water and protected rest; Medicine not automatic | one day baseline |
| Waterborne illness | known suspect/contaminated Water used after warning | exposed → symptomatic → impaired → stabilized | light duty or zero at serious | 1–2 Medicine, 2 Water, triage/stable treatment | one to two days |

Optional burns, panic response, grief impairment, and contamination are not implemented as slice systems. They remain future contextual possibilities only if they reuse this framework.

## Preventable injury contract

No new construction injury is injected for tutorial coverage. An injury requires a visible authored risk supported by one or more of:

- inadequate protection;
- delayed stabilization;
- ignored warning;
- accepted structural risk;
- a declared Highball strain exception.

Good preparation prevents the Day 2 injury. Teo’s existing respiratory exposure provides the guaranteed examination/treatment tutorial when no injury occurs.

## Medical loop

1. **Condition begins:** a named cause creates a contextual record.
2. **Warning:** severity, likely progression, and response window appear.
3. **Examination:** one grouped action establishes the treatment plan.
4. **Stabilization:** Medicine, Clean Water, room, and staff are reserved atomically.
5. **Treatment:** medical work proceeds and can be interrupted at a stable stage.
6. **Observation/rest:** bed/cot remains occupied and the resident remains unavailable as specified.
7. **Recovery:** Health cannot exceed the resident’s pre-condition maximum.
8. **Lasting consequence:** only a declared temporary restriction exists in the slice; full-game consequences require later design.

Minor care does not require a click for every sub-step. Examination, reservation, and treatment can be presented as one contextual flow while remaining separate save-safe transactions.

## Treatment transactions

Starting treatment checks room and capable-staff blockers before spending anything. A valid start reserves Medicine and Clean Water once under a treatment ID. Interruption:

- retains the reservation;
- records its reason and resume stage;
- does not reserve Medicine again;
- leaves the resident’s restriction active.

Completion has a separate idempotency key, closes the treatment only once, and moves the resident into recovery. Saving at planned, active, interrupted, resumed, completed, or recovery state produces the same committed outcome after reload.

## Serious-harm ladder and slice boundary

The sequence is pressure → warning → response window → restriction → stabilization opportunity → recovery cost. One missed meal, one missed warning, or one brief utility interruption cannot cause instant critical harm.

The First Count requires no death. Full-game death may exist later only after a serious known condition, clear warning, meaningful response time, available intervention, and deliberate risk or sustained neglect. No hidden roll may bypass the ladder.

## Room and utility interactions

- A triage cot supports examination and limited care.
- A stable treatment area is required for severe respiratory, serious injury, and serious waterborne care.
- Power is required only for named powered equipment or critical controls, not every bandage.
- Clean Water is a treatment reservation; contaminated Water cannot substitute silently.
- Air Exposure requires evacuation or protection before continuing care in that section.
- Temporary room conversion can provide treatment capacity while suspending the displaced room function.

## Mobile presentation requirements

From the shelter overview, a condition alert shows portrait, primary band, contextual cause, progression horizon, and auto-pause tier. One tap centers the resident/room; the second opens the care card with required stock, staff, room, work, likely deterioration, and alternatives.

Symbols accompany color. Plain-language reasons replace diagnostic jargon. Blocking decisions pause. Reduced motion centers without a long camera move. Large text may expand the card but cannot hide cause, response, or irreversible confirmation.

## What the model proves and does not prove

The tests prove zero productive capacity for explicit restrictions, bounded condition stacking, named reservations, interruption persistence, no over-healing, and no single-warning slice death. They do not prove medical realism, emotional credibility, animation clarity, humane writing, or player comprehension.

## Prototype gates

- Test whether players distinguish Health from the named injury/exposure cause.
- Measure treatment-card comprehension and two-tap diagnosis.
- Validate cot occupancy, staff travel, and evacuation timing in Prompt 4 geometry.
- Review terminology and consequences with medical/accessibility sensitivity readers.
- Revalidate productive restrictions against resident animation and task interruption behavior.
