# 17 — RESIDENT NEEDS AND MEDICAL

**Stage:** Prompt 3. **Status:** LOCKED at structural level; numbers PROVISIONAL in `tools/data/resources.json → needs` and `tools/data/incidents.json → condition_rules` (D-043).

---

## 1. Four primary conditions — and only four

**Health · Hunger · Fatigue · Stress** (0–100; bands: safe / strained / critical from config). *Stress is the Prompt-3 name for the concept-stage "Strain"; one concept, one meter.* **No fifth bar:** thirst, cold, hygiene, morale, fear, infection, and grief are **contextual conditions and presentation states**, not meters — shown through portrait states, room warnings, behavior, dialogue, condition cards, and medical inspection. Dehydration exists only as a contextual condition when water actually runs dry.

### Per-condition definition

| | Changes when | Visible behavior | Work effect | Recovery | Critical risk |
|---|---|---|---|---|---|
| **Hunger** | Meal windows (steps, never per-second); sustained shortage | Slower gait, canteen lingering, barks | Strained −10% efficiency; critical −30% + no overtime | Meals; the Canteen's warm meals recover extra | Never death from one miss; sustained → health erosion *with its own warning* |
| **Fatigue** | Work blocks, travel, nightruns, overtime/HIGHBALL; recovery only in rest | Slumped posture, yawning idle | Same efficiency ladder; **critical bars hazardous work** (accident risk) | Sleep (rough sleep recovers less — west's priced cost); ember tea | Exhaustion condition: must rest next shift, refuses hazards |
| **Stress** | Events, unsafe rooms, conflict, overwork, broken promises, rationing; recovery through good days, scenes, comfort | Snapping barks, withdrawal, pacing | Interruption/refusal likelihood up; conflict events likelier | Warm beats, gathering scenes, kept promises, ember tea | Vents visibly before breakdown (Pillar 2); never a silent detonation |
| **Health** | Injury, illness, exposure, untreated conditions; treatment + rest to recover (recovery never exceeds pre-injury health — an injury is never a net gain, asserted) | Limps, coughs, bed rest; condition card | Restrictions by condition class | Treatment (Medicine committed at start) + treatment days | **Critical health auto-pauses** ("a resident may die" is the *internal tier name* — slice modal copy states the true stakes: lasting harm and forced treatment, never death, per the no-death policy below); full game: death only via serious condition + warning + response window + deliberate risk |

**Timing philosophy (as mandated):** hunger at meal windows; fatigue through work/rest cycles; stress through events and environments; health through discrete causes. **No invisible continuous decay from minor inconvenience** — the model asserts no unwarned critical state ever occurs.

## 2. Needs × work (the anti-death-spiral contract)

Efficiency ladder from config (strained ×0.9, critical ×0.7) — reduced, never zero: **emergency survival work always remains possible**, so low-food → less work → less food converges instead of spiraling. *What the model asserts (D-045):* the unrationed-shortage scenario drives sustained hunger into the strained band, the crew visibly slows (×0.9, never below the ×0.7 floor), and the week still ends short-but-alive (20 §2) — as same-day survival-side accounting; the full per-phase feedback loop is first-playable work. Residents can volunteer for emergency work, refuse unsafe work (legibly — cause named, never a percentage), be reassigned, receive rest priority, use protective gear, work one controlled overtime shift (fatigue + a promise), or be medically restricted. Refusal causes: value lines, Marks, active conditions, genuine danger, exhaustion — the finite authored list (11 §6), each self-explaining with a real player response.

## 3. Medical condition framework (slice set)

Five slice conditions (schema + numbers in `incidents.json`): **minor injury · serious injury · respiratory exposure · exhaustion · waterborne illness.** Burns, panic, grief-impairment, malnutrition, dehydration are architected as the same condition-card structure for the full game — added only when their stage needs them.

Every condition card answers, in plain language: *who needs help · how urgent (safe hours/days shown as a forecast) · what treatment requires (doses, venue, carer) · what delay costs · who can provide care.* Treatment **reserves** the carer, the venue (Aid Car bed or the bench at Ash's penalty), and the doses (committed at start — no double-spend after reload: the mid-incident snapshot is serialized, reloaded into a fresh instance, resumed to Day 7, and compared equal, committed doses included — asserted, D-045). Triage is a decision when demands collide (event 19's two-casualties-one-bed), not minute-to-minute micromanagement.

**Death policy:** the slice proves injury→consequence→recovery, not mortality. Full-game deaths require the four-step ladder above and are never a random roll — a death without a prior serious condition and a declined response window is a design bug by definition.

## 4. UI and accessibility presentation

Needs live on the **crew strip** (portrait glance states: posture/tint per band) and the **ledger page** (four bars + active condition cards + causes in words: "slept rough · storm watch · treated Teo"). No permanent top-bar meter wall — the HUD stays five stocks + clock. Conditions use icon + shape + text (color-safe); all state changes announce via captioned barks/banners; portrait states carry redundant iconography; the critical-health modal is the one hard interrupt (auto-pause tier). Screen-reader labels on bars and cards are the full-game accessibility row already in 03.

## 5. Save representation

Needs are four floats + a condition set per resident inside the single world-state object (R-10); treatment bookings serialize with their committed doses; reloads can neither repeat a dose nor lose a booking (asserted by the reload-and-resume comparison in `test_survival_model.py` — D-045).
