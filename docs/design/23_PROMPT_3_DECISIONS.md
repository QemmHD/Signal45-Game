# Signal 45 — Prompt 3 Decisions

> Decision record for survival systems. Earlier reasoning remains authoritative except where an explicit amendment below replaces it. All balance values remain provisional.

## Prompt 2 corrections

### P3-D01 — Replace binary outcome interpretation with five explicit classes

- **Previous behavior:** the practical `viable` flag conflated fictional survival, release-slice proof, and some ending requirements.
- **Evidence:** a missing hope setup or route proof could be reported with the same failure language as an unrecoverable shelter.
- **Decision:** Full Proof, Recover First, Proof Incomplete, Shelter Failure, and Invariant Error are canonical. Convenience flags derive from class.
- **Consequence:** failure to stage a celebration is not shelter death; missing a required release proof still fails QA.
- **Revisit:** only if later campaign endings require an additional class; do not weaken these distinctions.

### P3-D02 — Make the full hope setup an ambition with an earned fallback

- **Previous behavior:** the five-WU authored hope setup was effectively mandatory.
- **Evidence:** schedule sensitivity could turn a positive recovery beat into a late construction tax.
- **Decision:** the full setup remains the richer Full Proof beat; an existing relit sign, safe tap, completed repair, or quiet sleep may support a zero-to-two-WU minimal beat.
- **Consequence:** fallback creates no stock and supports Recover First without erasing consequences.
- **Revisit:** playable narrative test of whether the fallback feels earned rather than cheap.

### P3-D03 — Critical incapacity means zero productive WU

- **Previous behavior:** the per-resident emergency minimum could give critically impaired residents project capacity.
- **Evidence:** this contradicted the “people are not batteries” pillar and hid medical consequences.
- **Decision:** Critical Health, Collapse risk, medically incapacitated, untreated critical injury, unconscious, and severe respiratory restrictions block productive work. Self-preservation is separate.
- **Consequence:** the two-WU safeguard belongs to the available shelter pool; all unavailable becomes a named fallback/failure, not forced labor.
- **Revisit:** Prompt 4 evacuation path and Prompt 5 refusal behavior.

### P3-D04 — Split the old ten-WU daily overhead into operation and incident reserve

- **Previous behavior:** ten WU were labeled broadly as daily essential work while incident response could also be charged separately.
- **Evidence:** aggregate buffer hid what capacity was actually available for interruption.
- **Decision:** eight WU are baseline essential operation and two WU are explicit incident reserve. Total baseline burden remains ten; base resident capacity remains 12.
- **Consequence:** no labor was added. Incident work consumes reserve first and reports overflow.
- **Revisit:** after animated task and Prompt 4 travel measurement.

### P3-D05 — Report resilience as a metric set, not one percentage

- **Decision:** report aggregate unused WU, daily uncommitted WU, phase slack, hard-deadline slack, incident reserve, carryover, optional capacity, and emergency recovery.
- **Evidence:** baseline aggregate totals looked healthy while Day 5 had zero uncommitted WU.
- **Consequence:** Days 2, 3, and 6 show two WU; Day 5 is explicitly fragile.
- **Revisit trigger:** any new mandatory Day 5 work or geometry overhead.

### P3-D06 — Pair every adverse stock test with a deliberate response

- **Decision:** add ration/trade, Water restriction/reserve+deferral, Medicine priority, Materials deferral, and Charge load shedding.
- **Consequence:** ignored cases still fail; responses restore Full Proof or Recover First at an explicit human/resource/opportunity cost.
- **Rejected:** unexplained stock injection or global leniency.

### P3-D07 — Teach Power versus Charge through the Day 4 Relay Load Test

- **Decision:** a 0.7 temporary deficit offers Charge, task-light shedding, or delay. It adds no project WU and occurs after onboarding.
- **Consequence:** all choices remain viable; dimming/restore is a future visual requirement.
- **Revisit:** comprehension test on phone.

## Survival semantic decisions

### P3-D08 — Use discrete issue and condition boundaries

Food/Water issue, work blocks, incidents, treatment, rest, and ledgers drive changes. Per-second hidden drain is rejected. One missed meal never causes immediate critical Health loss.

### P3-D09 — Use dominant impairment plus capped secondary penalties

The largest condition penalty applies fully; secondary penalties apply at half weight; total arithmetic penalty caps at 75%, followed by explicit zero-work restrictions. This replaces opaque multiplication without removing compounding.

### P3-D10 — Keep Medicine transaction-bound

Medicine reserves once at named treatment start, persists through interruption, and completes once. Passive expiration is deferred. Room/staff blockers spend nothing.

### P3-D11 — Apply Charge conversion loss in executable behavior

Prompt 2 described reserve loss but did not apply it consistently to every discharge. Prompt 3 applies a 10% loss and stage limit through one helper. A disconnected branch rejects discharge.

### P3-D12 — Make utility diagnosis section-level and link-specific

Power uses priority/branch facts; Air uses visible stages; Water names one of five links; Structure is local with one adjacent warning. Individual wires, pipes, particles, and engineering physics remain deferred.

### P3-D13 — Use one reusable incident schema and scheduler

Six slice families share warning, escalation, interruption, recovery, aftermath, and save fields. One major crisis and two minor warnings are hard ceilings. Conflict families remain placeholders only.

### P3-D14 — Make incident recovery idempotent

- **Finding:** red-team repetition of `recover_incident` appended another completion transaction.
- **Correction:** resolved recovery returns unchanged; one reward claim ID persists.
- **Evidence:** a dedicated failing-capable test now calls recovery twice.

### P3-D15 — Treat Highball as time transfer with deterministic strain

All uses apply guaranteed Fatigue, Stress placeholder, Charge, wear, rest promise, and strain. Low/elevated/critical tiers add deterministic inspection or block use. Medical restrictions reject the order. There is no hidden lethal roll.

The 25%, 35%, and 50% candidates remain unselected. One well-timed use can pull a deadline forward; repeated/low-equipment use produces Recover First in tested cases. Weekly net value may be negative, which is intentional.

## Values changed

| Area | Prompt 2 baseline | Prompt 3 change | Reason |
|---|---|---|---|
| daily survival overhead | ten broadly essential WU | eight essential + two reserved incident WU | expose interruption reserve without increasing total |
| critical individual capacity | could floor above zero | explicit zero productive work | medical integrity |
| hope setup tier | mandatory in practice | ambition plus earned fallback | avoid mandatory hope tax |
| Charge discharge | loss described inconsistently | one 10%-loss, three-unit/stage helper | causal and save consistency |
| outcomes | boolean-first interpretation | five-class taxonomy | distinguish survival, proof, and defects |

Resident base capacity remains 12 WU. Project WU, starting stocks, seven room families, route components, active/delegated objective parity, Juna’s non-mandatory status, and no-offline-advancement rule remain locked unless explicitly represented in canonical scenarios.

## Rejected alternatives

- Adding Thirst, Infection, Air, Morale, or Trust as permanent meters.
- Increasing every resident above 12 WU to absorb survival detail.
- Per-second Food/Water loss.
- Passive Medicine expiration.
- Materials substituting silently for route components.
- Charge powering disconnected branches.
- A hidden random Highball breakdown or lethal roll.
- More than one simultaneous major crisis.
- Adding full intrusion/combat resolution.
- Making the hope fallback grant supplies or cancel consequences.
- Converting all adverse outcomes to Recover First.
- Selecting 35% because it was the previous baseline candidate.

## Red-team findings

| Perspective | Finding | Severity | Resolution/evidence |
|---|---|---:|---|
| Survivor | critical residents could appear to supply emergency work | high | individual zero; shelter-pool provider list; all-unavailable failure case |
| Base builder | survival detail could add hidden construction load | high | old ten WU split, not increased; S170 reconciles every day |
| Mobile player | condition and incident detail risked alert density | high | four meters, one overlay, one major/two minor ceiling, two-tap cards |
| New player | Charge could arrive too early | medium | Relay test on Day 4, explicitly outside first-session window |
| Min-maxer | rationing could be spammed | high | consecutive Hunger/Stress escalation and Recover First case |
| Min-maxer | Charge/Highball/recovery could duplicate | high | transaction IDs plus direct repeat tests |
| Medical review | serious restrictions needed respectful, comprehensible behavior | high | zero work, named cause, assistance, no comic mental-health mechanics |
| Adversarial tester | proof loss masqueraded as death | high | class separation and direct S95 evidence |
| Adversarial tester | repeat incident completion was not idempotent | high | code fixed and test added |
| Production lead | incident families could become bespoke minigames | high | one data schema; six families; conflict deferred |
| Accessibility | severe response might demand speed | high | auto-pause, extended decision time, symbols+color, plain-language causes |

### Refuted findings

- **“The 35% Highball value is now final.”** Refuted: canonical data explicitly marks multiplier unselected and tests all three candidates.
- **“Prepared storm work is hidden.”** Refuted: daily reports separate incident reserve, used reserve, overflow, project work, and buffer; S170 differences are zero.
- **“Recover First makes adverse scenarios pass automatically.”** Refuted: twelve Shelter Failures, three Proof Incomplete cases, and one invariant detection remain.
- **“Juna supplies the missing labor.”** Refuted: route baselines pass without her work; admitted/unavailable cases remain covered by Prompt 2.

## Remaining fragility

- Day 5 has zero uncommitted WU after the prepared response; new labor cannot be added casually.
- Hard-deadline slack reaches zero for several baseline projects.
- East Water and all-route Food remain sensitive. The responding East case ends at 12.52 Water versus West at 12.60 under comparable pressure; that 0.08 separation preserves the ordering but is too narrow to claim a robust route identity before spatial and usability prototypes.
- West travel remains unmeasured and previously failed the higher-overhead sensitivity.
- Treatment and evacuation travel are allowances, not coordinate-derived.
- Forecast comprehension, alert density, and Relay teaching are unmeasured.
- Highball’s emotional/relationship consequences remain Prompt 5 placeholders.
- Incident presentation and physical aftermath have no runtime evidence.
- Medical terminology requires professional/sensitivity review.

## Prompt 4 entry requirements

Prompt 4 may define station geometry only while preserving:

1. the Prompt 3 canonical stock, condition, utility, incident, and outcome semantics;
2. one live simulation across camera scales;
3. seven room families and four-to-ten-area growth;
4. section-level nodes rather than freehand utility drawing;
5. explicit paths for carrying, treatment, isolation, and evacuation;
6. Day 1, East Day 7, and West Day 7 layouts that reproduce project dependencies;
7. both routes’ non-Highball feasibility and Water distinction;
8. no new Day 5 mandatory work without an offset and scenario evidence;
9. machine-readable coordinates that can remeasure travel, congestion, and access;
10. the existing save boundaries for placement, connection, isolation, closure, and room conversion.

Prompt 4 must not expand survival values, resident AI, full crafting, conflict, expeditions, factions, additional maps, or final assets. Its mandatory output is a spatial revalidation input, not a replacement economy.

## Prompt 4 completion amendment

Prompt 4 preserves the survival ceiling while correcting spatial contradictions: one Platform Work Lamp consumer, physical area counting, and exclusive spatial travel mapping. All 176 mandatory Prompt 2/3 scenarios still match. Documents 24–30 and `tools/spatial/` supersede this entry section for current geometry; Prompt 5 is now the next boundary.
