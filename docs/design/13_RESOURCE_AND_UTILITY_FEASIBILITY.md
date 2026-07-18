# Signal 45 — Resource and Utility Feasibility

## Model boundary

Prompt 2 models the five HUD stocks, five representative component blockers, and four utilities needed to falsify **The First Count**. It is deterministic, intentionally coarse, and sourced from `tools/feasibility/data/model.json`. It is not the final economy or engineering simulation.

## Five primary stocks

| Stock | Start / capacity | Minimum / comfortable | Warning | Main inflow | Main outflow |
|---|---:|---:|---:|---|---|
| Food | 40 / 60 | 6 / 12 | below 10 | trader or later production | daily ration issue |
| Clean Water | 60 / 80 | 8 / 16 | below 14 | trader; West treatment output | daily issue, treatment, storm loss |
| Medicine | 8 / 12 | 2 / 4 | below 3 | trader | examination, injury, exposure, Juna stabilization |
| Materials | 70 / 100 | 5 / 20 | below 10 | reclamation and annex salvage | reservations, trade, Highball wear |
| Charge | 24 / 30 | 3 / 10 | below 6 | no routine slice production | Power deficit and Highball |

### Forecast formula

For each stock, the UI reports current amount, committed reservations, expected issue/production, and projected amount at the next safe ledger. Status is:

- **Critical:** projected amount below minimum viable reserve.
- **Warning:** below the warning threshold.
- **Tight:** below comfortable reserve.
- **Comfortable:** at or above comfortable reserve.

Forecasts evaluate committed state, not animation position. A blocked project names its missing component rather than showing only “insufficient Materials.” End-of-day reporting includes start, end, minimum-to-date, projected status, and exact shortfall reason.

## Resident consumption

Food and Water are issued at visible daily ledger moments, not drained per second.

| State | Food per resident/day | Water per resident/day | Consequence model |
|---|---:|---:|---|
| Normal ration | 1.00 | 1.50 | no capacity penalty |
| Restricted | 0.75 | 1.10 | light Hunger/condition pressure |
| Missed meal | 0 | unchanged unless Water also restricted | one miss cannot create immediate critical harm |
| Treatment | — | +1 baseline | tied to a named treatment transaction |
| Emergency Water | — | +2 event allowance | forecast before commitment |

A resident absent on a nightrun still consumes a packed share; it is moved from shelter inventory at commitment instead of becoming free supply. Juna adds one Food and 1.5 Water per full day after admission, plus 2 Water and 1 Medicine to stabilize. The model applies her Day 6/7 costs honestly and does not credit Day 6 labor.

The baseline end state is Food 11 on both routes; a 20% Food increase ends at 5.4 and fails both. East ends with Water 15 and fails a 20% Water increase at 6.6. West ends with Water 25 and remains viable at 12.6 under the same increase. This is a deliberate route distinction and a fragile Food assumption.

## Representative component blockers

The slice tracks only:

- filter material for storm filtration;
- structural brace for reclamation;
- electrical relay for East utility extension;
- pump seal for West Water treatment;
- radio component for the optional relay ending direction.

The relay or pump seal is obtained from the shared Harbor Line Maintenance Annex objective. If the required component is missing, the route-specific room cannot complete and the scenario fails even when Materials remain abundant. This proves that Materials cannot falsely substitute for every part without creating a large crafting inventory.

## Power versus Charge

**Power** is connected operating capacity and priority. **Charge** is a finite stored reserve.

The damaged source supplies 12 nominal Power at 90% condition, or 10.8 usable capacity before repair. Representative loads are:

| Load | Power |
|---|---:|
| Service Alcove | 1.50 |
| Air filtration | 2.50 |
| Water pumping | 1.50 |
| Relay Kiosk | 1.00 |
| Medical equipment | 0.75 |
| Workshop | 1.50 |
| Task lighting | 0.75 |
| Optional comfort lighting | 1.00 |

Priority protects Air, Water, Medical, Relay, and the Service Alcove before task lighting, Workshop, and comfort. A forecast displays current capacity, demand, margin, the first shed load, Charge duration under deficit, and the next endangered branch. Charge discharges by stage and is capped at 3 units per affected storm stage. It cannot repair a disconnected branch or sustain all loads indefinitely.

Prepared play remains viable with Charge capacity halved to 15 on both routes, but this does not validate the final discharge rate. The relevant prototype must make Power margin and Charge duration visibly different concepts.

## Air

Air uses capacity, resident/process demand, filter condition, cinder load, and section state:

`effective Air capacity = 12 × filter condition`

The temporary filter starts at 72% condition. The preparation project restores 18 percentage points. Demand is one unit per resident plus two room-process units, with storm cinder load added by profile. The plain stages are Stable, Loaded, Degraded, Exposure, and Evacuate. A negative margin names **filter condition** as the failing link.

Exposure has two modeled response stages before lasting harm: service/replace, isolate, or evacuate. Zoom and Room Focus do not change demand or the exposure clock.

## Water

Water reports each link separately:

`delivered Clean Water = source × pump availability × treatment efficiency × delivery efficiency`

East uses an 8-unit source and stored reserve preparation. West can restore a 10-unit source and then produces 1.5 stock units per day. Pump availability starts at 100%, treatment at 90%, and delivery at 95%. Storm impairment reduces pump and treatment separately and marks storage as suspect; the warning states whether source, pump, treatment, delivery, storage, or contamination is responsible.

The Water states are Clean, Suspect, Contaminated, and Isolated. Prompt 2 does not simulate pipes or fluid particles.

## Structure

Structure is local to a section or project: Safe, Strained, Unstable, Critical, or Closed. Unstable is the visible warning stage. Critical requires immediate stabilization; Closed removes access. Reclamation plus reinforcement improves a local section in discrete steps. A forced closure test confirms that residents cannot access the section.

No unseen structural roll injures a resident. A construction injury requires at least two visible accepted hazards: accepting the risk, inadequate protection, ignoring a warning, or delaying stabilization. Good preparation yields no new injury.

## Deterministic Day 5 storm

The Listening Post weather burst, corroborated by local filter readings, forecasts a cinder front with 80% baseline confidence and two response stages of lead time. Drainage commitment adds a stage. Vulnerabilities and preparation projects are visible before commitment.

The only permitted cascade is:

```text
Cinder front → Air → Power → Water
```

It has one initial environmental pressure, at most three affected systems, one major crisis, and an interruption after every active stage. A minor consequence may queue; a second major crisis may not.

| Profile | Response WU | Systems | Charge | Water loss | Medicine | Next-day capacity loss | Outcome |
|---|---:|---:|---:|---:|---:|---:|---|
| Prepared | 4 | 1 | 1 | 0 | 0 | 0 | manageable |
| Partial | 9 | 2 | 4 | 2 | 1 | 3 | serious but recoverable |
| Unprepared | 15 | 3 | 7 | 5 | 2 | 6 | serious; Day 7 recovery shift |
| Extended neglect | 24 | 3 | 10 | 10 | 3 | 12 | failed/heavily damaged slice state |

Strategy modifies the profile rather than rolling an outcome:

- **Service filter:** +2 WU, stops one system earlier, saves 1 Charge.
- **Load shed:** +1 WU, saves 2 Charge.
- **Isolate Water:** +1 WU, saves 3 Water.

Route preparation then applies. East's stored Water reduces Water loss by 3; West isolation reduces it by 4. East's better Rest/Medical layout helps response capacity; West's Water system helps the aftermath. Neither route is a hidden answer.

At every active stage the UI must show current cause, current effect, likely next effect, stages or WU before escalation, available interruption, known cost, and labeled uncertainty. Prepared, partial, unprepared, neglect, route, signal, strategy, and Highball variants are in the machine-readable scenario report.

## Recovery and feasibility verdict

Prepared East and West remain viable. Unprepared East and West also remain viable but spend more Charge, Water, Medicine, response labor, and next-day capacity; Day 7 explicitly shifts 4 WU from noncritical routine work into recovery. Extended neglect fails with a named unrecoverable storm state. No profile can propagate past Water, and no profile kills a resident through an unseen roll.

The model validates arithmetic and bounded causality. Prompt 3 must refine forecast presentation, restriction consequences, Power/Charge behavior, filter degradation, and the incident state machine without adding hidden resources or unbounded cascades.
