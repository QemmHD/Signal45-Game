# Signal 45 — Utility Networks and Forecasts

> Prompt 3 contract. The slice implements exactly four section-level utility families: Power, Air, Water, and Structure. It does not simulate individual wires, pipes, air particles, or engineering physics.

## Shared network rules

Utilities are described by capacity, demand/load, condition, connection, priority, isolation, backup, failure stage, and recovery. They are not collectible currencies. The player may activate one utility overlay at a time; the current urgent issue can temporarily highlight the next affected utility without turning every overlay on.

Simulation state is independent of Overview, zoom, and Room Focus. Camera transitions consume observation time only.

## Power

Power is live operating capacity. A section or device must be connected to a healthy source branch before it can receive Power or Charge backup.

### Priority order

| Tier | Slice consumers |
|---|---|
| Critical | Air protection in an occupied section, essential medical stabilization, emergency controls |
| Essential | Water pumping/treatment, committed Relay operation, core service controls |
| Normal | Workshop and routine equipment |
| Optional | Platform Work Lamp (`platform_lighting`) |

When margin becomes negative, optional lighting sheds before normal or essential systems. The forecast shows current capacity, demand, margin, first shed load, and next endangered load. A faulted or disconnected branch is not repaired by spending Charge.

The model uses a 12-unit source at 90% condition for 10.8 live capacity. These are provisional feasibility values, not diegetic electrical units.

## Charge

Charge is a five-stock reserve, not Power capacity. It has:

- current amount and storage capacity;
- a named connected consumer;
- maximum delivery per stage;
- conversion loss;
- duration under the declared deficit;
- atomic discharge and idempotency ID.

A three-unit stage delivery ceiling and 10% loss prevent the reserve from disguising every Power problem. The card says, for example, “Battery reserve can cover Air for two storm stages,” rather than converting Charge into an unexplained universal fix.

## Relay Load Test

The controlled Day 4 calibration occurs after onboarding and before the Day 5 storm. It reuses the Relay/Forecast Board context and adds zero project WU.

Temporary demand is 11.5 against 10.8 live Power, creating a visible 0.7 deficit. The player chooses:

| Response | Immediate result | Cost and later effect |
|---|---|---|
| Discharge Charge | connected deficit is covered | draws 1.111 Charge after conversion loss; less storm reserve |
| Shed Platform Work Lamp | the same Day 1 lamp visibly dims; calibration continues | no Charge; temporary light loss; lamp restores when margin returns |
| Delay calibration | no stock spent | one stage less warning lead/forecast confidence |

All three remain feasible. The game autosaves before confirmation and after the committed response. No injury or campaign-ending consequence exists. The event teaches one distinction: **Power is live capacity; Charge is finite stored backup.**

## Air

Air is section-level and uses these stages:

1. Stable
2. Loaded
3. Degraded
4. Exposure
5. Evacuate

Inputs are filter condition, fan/movement capacity, resident demand, process demand, cinder load, connection, seals, and protection. Pressure normally advances one visible stage at a time. The alert shows current stage, next stage, residents at risk, and work/stages before escalation.

Responses are service/replace filter media, reduce process load, restore Power, isolate the section, evacuate, use protection, move treatment, or discharge Charge to a connected critical Air load. Preparation can stop the storm after Air. No instant unexplained exposure is permitted.

Teo’s respiratory sensitivity moves his personal warning and treatment threshold earlier; it does not reduce section Air capacity or make him an automatic failure.

## Water utility

Water preserves five diagnostic links:

1. **Source** — available raw supply.
2. **Pumping** — moves source water.
3. **Treatment** — makes it clean.
4. **Delivery** — reaches storage/rooms.
5. **Clean storage** — holds usable stock safely.

The overlay always names the first failing link. It displays throughput, demand, headroom, storage condition, and the expected Clean Water transfer.

Readable states are Clean, Tight, Suspect, Contaminated, and Isolated. A contaminated store is isolated before issue. Responses include restriction, declared reserve, pump repair, treatment improvement, Charge on a connected pump, manual operation, trader supply, nonessential cleaning deferral, and temporary bypass.

West’s treatment project improves supply/throughput and storm recovery. East’s reserve project creates a smaller buffer rather than matching West’s Water security.

## Structure

Structure is local to authored sections:

1. Safe
2. Strained
3. Unstable
4. Critical
5. Closed

Survey confidence is reported separately from condition. Storm/project pressure advances known stages; reinforcement moves the section toward safety. Unstable displays cracks/debris and warning. Critical auto-pauses, restricts access, and requires evacuation. Closed suspends tasks, cancels or pauses paths, updates utility access, and creates recovery work.

Propagation is capped at one adjacent-section warning. No structural roll can secretly injure a resident. Injury is possible only after a visible accepted risk.

## Isolation and backup

Isolation is a real trade:

- it stops the configured propagation path;
- disconnects the selected branch/section;
- suspends its room benefit and local tasks;
- evacuates occupied unsafe sections;
- preserves unaffected sections;
- creates an inspection/reconnection obligation.

Backup applies only to a connected load. A temporary bypass uses named Materials/components, reduces one stage, and creates later permanent repair.

## Shared forecast framework

Every forecast is classified as:

| Class | Meaning | Precision rule |
|---|---|---|
| FACT | measured current state | exact only to useful resolution |
| PROJECTION | committed known behavior | next-ledger arithmetic |
| ESTIMATE | incomplete environmental/behavior assumptions | range or plain horizon |
| SIGNAL INTELLIGENCE | Listening Post source and confidence | source, age, and uncertainty visible |
| UNKNOWN | important missing information is known to be missing | names what must be surveyed/listened to |

A card may contain current state, committed use, expected gain, projected next ledger, approximate operating stages/person-days, confidence, source, drain, failing link, next consequence, and responses. Estimate, intelligence, and Unknown cards explicitly avoid false precision.

Examples of approved language:

- “Water should last through tomorrow evening at current issue.”
- “East reserve becomes unsafe after one additional treatment.”
- “Battery reserve can cover Air for two storm stages.”
- “The filter is likely to enter Exposure during the next cinder peak.”
- “Structure timing is uncertain because the eastern bay is not fully surveyed.”

## Forecast causality

Forecasts update only from committed state:

- a meal policy changes committed Food use;
- treatment start changes Medicine and Water reservations;
- a completed project changes capacity/throughput;
- a Relay response changes Charge or warning lead;
- a signal commitment changes intelligence confidence;
- an incident stage changes likely next consequence;
- an isolation changes connected demand and room availability.

An animation never changes the forecast independently of its committed transaction.

## Landscape-phone diagnosis flow

Major shortage diagnosis must fit within two taps:

1. **Overview alert:** stock/utility symbol, current band, horizon, cause summary, likely next result.
2. **Focused card/overlay:** failing link, affected section/residents, committed drain, responses, cost, and irreversible confirmation.

Only one overlay is active. Symbols accompany color. The player may pause before opening or while reading. Large text scrolls within the panel without hiding the station permanently. Reduced motion centers the selected section without a cinematic move.

## Physical and audio state requirements

Future runtime presentation must distinguish:

- powered, shed, disconnected, and faulted equipment;
- Stable, Loaded, Degraded, Exposure, and evacuated Air sections;
- clean, suspect, contaminated, and isolated Water storage;
- Safe, braced, Critical, and Closed structure;
- active Charge discharge and finite reserve;
- platform lamp dimming/restoration in the Relay Load Test.

These are state requirements, not final assets.

## Save requirements

Power priority, branch connection, isolated state, Charge consumer/draw/loss, Air stage, Water failing link, Structure stage, forecast class/confidence, and Relay choice serialize. Closing mid-dimming or mid-camera move resumes the logical state. No closed-app progression occurs.

## Prototype gates

- Validate Power-versus-Charge comprehension in the Relay Load Test.
- Validate two-tap Water-link diagnosis on a small landscape phone.
- Measure overlay readability with large text and color-vision settings.
- Prompt 4 now validates branch/node placement, service access, isolation, evacuation, and sealed vertical travel. Revalidate logical cost against a mobile 3D graybox before production tuning.
- Test whether Air progression feels fair without becoming a meter wall.
