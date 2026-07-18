# Signal 45 — Session and Phase Timing

## Status and source of truth

This document records Prompt 2's provisional timing budget for **The First Count**. Canonical numeric inputs live in `tools/feasibility/data/model.json`; the values below are readable extracts, not a second balance source.

The model budgets interaction time. It does not measure a playable build, player comprehension, camera comfort, or enjoyment. Every timing value must be revalidated in an instrumented mobile prototype.

## Timing at four scales

### 20–40-second interaction

The baseline interaction is **32 seconds**:

| Part | Provisional budget |
|---|---:|
| Notice a need or completion | 4 s |
| Select or move camera | 5 s |
| Read cause and forecast | 8 s |
| Choose | 8 s |
| Confirm | 3 s |
| See the first visual response | 4 s |

The interaction is successful when the player can name the cause, commit one choice, and see a resident or shelter response. Repeated routine confirmation should be shorter; a consequential choice may use the full range and pause the simulation.

### 2–5-minute safe segment

A safe segment contains one coherent task: complete a short repair, assign a standard project, commit a signal, stabilize one incident stage, prepare a nightrun, or process its return. A committed transaction or stabilized incident ends each segment. The player never has to remain online to protect the outcome.

### 5–12-minute normal session

A normal shelter session should deliver:

1. One visible shelter improvement.
2. One resource, staffing, or utility decision.
3. One consequence or forecast review.
4. At least one committed safe save.

The model's ordinary no-expedition day is **7.5 minutes**. The visitor/admission day is **8.1 minutes**. The prepared-storm day is **about 7.8 minutes**. These are budget estimates, not measured playtimes.

### Full-day results

| Day type | Baseline | Target range | Maximum useful decisions | Result |
|---|---:|---:|---:|---|
| Ordinary shelter day | 7.5 min | 5–12 min | 6 | Fits target |
| Delegated-nightrun day | 9.1 min | 8–12 min | 8 | Fits target |
| Active-nightrun day | 12.3 min | 11–16 min | 12 | Fits the optional longer-session target |
| Admission day | 8.1 min | 5–12 min | 7 | Fits target |

The active day is deliberately not treated as a normal short session. Its additional decisions are spatial route choices, not more shelter panels.

## Day phases

### Day Shift — Swelter

- **Entry:** Graymorn ledger accepted; day forecast visible.
- **Exit:** work window closed by the player after every severe incident is stable.
- **Player actions:** assign, construct, produce, treat, maintain, and respond.
- **Simulation:** runs at the selected speed except during a blocking choice.
- **Pause:** automatic for serious Health decline, structure closure risk, trapping, or a severe cascade decision.
- **Autosave:** entry, every project transaction, stabilized incident stage, and exit.
- **Expected time:** 4.0–6.5 minutes; 5.2-minute baseline.
- **Decision ceiling:** five meaningful decisions.
- **Safe stops:** completed transaction, treatment start, or stabilized incident stage.

### Evening Window — Slack

- **Entry:** Swelter exit committed.
- **Exit:** signal and expedition/no-expedition plan committed.
- **Player actions:** review forecast, choose a signal commitment, prepare loadout, and set final priorities.
- **Simulation:** routine shelter tasks may finish; commitments pause.
- **Pause:** automatic for signals, promises, loadouts, and irreversible confirmation.
- **Autosave:** signal commitment, loadout commitment, and phase exit.
- **Expected time:** 0.8–1.6 minutes; 1.2-minute baseline.
- **Decision ceiling:** two.
- **Safe stops:** before departure or after committing no run.

### Night Operation — Nightrun

- **Entry:** loadout or stay-home decision committed.
- **Exit:** return, retreat, or no-run state committed.
- **Player actions:** set objective/risk policy; choose nodes in Active mode; retreat or complete.
- **Simulation:** Active and Delegated modes read the same graph state. Shelter simulation does not fork by camera scale.
- **Pause:** automatic before every consequential committed node.
- **Autosave:** before departure, on node entry, after an irreversible action, on retreat, and on return.
- **Delegated time:** 1.2–2.0 minutes; 1.6-minute baseline and two decisions.
- **Active time:** 4.0–6.0 minutes; 4.8-minute baseline and six decisions.
- **Safe stops:** departure gate, each secured node, irreversible action commit, retreat, and return.

### Return and Report — Graymorn

- **Entry:** nightrun or no-run transaction complete.
- **Exit:** inventory, treatment, consequences, and ledger accepted.
- **Player actions:** review inventory, begin treatment, inspect consequences, and set the next priority.
- **Simulation:** paused while the ledger or a blocking treatment choice is open.
- **Autosave:** before ledger, after treatment, and after ledger.
- **Expected time:** 0.8–1.5 minutes; 1.1-minute baseline.
- **Decision ceiling:** two.
- **Safe stops:** treatment commit and accepted ledger.

## Simulation speed

Prompt 2 retains exactly three controls:

| Control | Simulation behavior | Presentation behavior |
|---|---|---|
| Pause | No work, need, utility, incident, or expedition clock advances | Camera and accessible inspection remain available |
| Normal | Canonical work and incident rate | Full readable animation |
| Fast | Compresses routine work, travel allowance, hauling, and noncritical animation together | Cannot skip a committed warning or blocking choice |

A fourth speed is not justified for the slice. It would add UI and tuning cost without solving a demonstrated pacing problem.

Open contextual panels do not pause routine shelter work unless the panel contains a blocking decision. Blueprint preview, forecast inspection, and non-destructive selection may remain live. Admission, promises, signal commitment, irreversible project changes, serious Health intervention, severe incident escalation, and expedition consequence nodes pause automatically.

## Decision budget

- Ordinary day: six meaningful decisions across all phases.
- Delegated expedition day: eight.
- Active expedition day: twelve, including at most six route-node choices.
- Only one major crisis may be live. Minor consequences queue behind it.
- Routine completion toasts do not consume a decision slot and do not stop time.
- A decision is counted only when it changes labor, resources, utility state, route knowledge, a promise, or a consequential human outcome.

## Accessibility timing

Reduced motion shortens modeled camera-transition time rather than slowing simulation. A normal 7.5-minute day budgets **6.9 minutes** with reduced motion. Large text adds reading allowance, producing **8.85 minutes**. The combined budget is **8.1 minutes** because reduced camera time offsets part of the reading increase.

All consequential choices can pause indefinitely. Extended expedition decision time changes no simulation fact. Enhanced forecasting exposes the same canonical forecast earlier and in plain language. Room Focus remains usable without a cinematic move. No challenge requires rapid tapping.

These multipliers are workload budgets only. Device testing must measure text wrapping, touch target reach, screen-reader order, reduced-motion comfort, and whether twelve active-day decisions remain tolerable.

## Timing acceptance and revalidation

Prompt 2 accepts the schedule because modeled normal days fit 5–12 minutes, active days fit 11–16 minutes, and every phase exposes transaction-level safe stops. Prompt 3 must not silently add decisions. A playable prototype must reopen the schedule if median interaction time falls outside 20–40 seconds, the first safe stop exceeds seven minutes, or accessibility raises an ordinary session above twelve minutes.

## Prompt 3 timing amendment

The first-session teaching budget is unchanged. Charge mastery, incident cascades, admission, and Highball remain withheld/teased. The Relay Load Test is introduced on Day 4 as one controlled decision with an autosave before commitment. Major incidents auto-pause; one major/two minor warnings cap alert density. No survival system advances while closed. Phase reports now include conditions, utility summary, forecasts, emergency actions, promises, and critical-path slack, but these fields do not add player decisions by themselves.
