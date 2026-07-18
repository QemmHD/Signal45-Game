# Signal 45 — Prompt 2 Requirements

## Purpose

Prompt 2 must convert **The First Count** from a coherent design into a deterministic seven-day feasibility model. It must answer whether the intended work, consumption, construction, utilities, recovery, route differences, first-session teaching, and safe stopping points can fit the mobile-session target.

Prompt 2 must not begin full implementation or expand the game into later-stage systems.

## Inputs that are locked

- Four starting residents: Ash, Imka, Teo, Maren; Juna Malek is the admission candidate.
- Four approximate starting functional areas and eight to ten ending functional areas.
- Seven slice room families.
- Five stocks, four utilities, four resident conditions.
- Reclaim, Connect, Build, Operate, Adapt workflows.
- East comfort/treatment identity and West water/storm/salvage identity; both viable.
- Swelter, Slack, Nightrun, Graymorn phases with plain-language labels.
- One optional Highball opportunity with displayed cost.
- One shared active/delegated nightrun graph.
- Day 5 storm cascade, Day 6 Juna decision, Day 7 recovery/ending direction.
- Offline pause and safe serialization requirements.

Prompt 2 may adjust provisional quantities and distribute beats, but it must log any requested change to these locks rather than silently overriding them.

## What Prompt 2 must solve

1. **Exact session pacing:** target decision count, observation time, animation time, planning time, and safe stop cadence for 5–12 minute normal shelter sessions.
2. **Day-phase timing:** exact or bounded duration/work windows for Swelter, Slack, Nightrun, and Graymorn; how pause and speed affect them.
3. **Work capacity:** resident work availability by condition, travel, skill, rest, treatment, staffing, and interruption.
4. **Construction workload:** work units, resident requirements, utility/resource/component costs, partial progress, interruptions, upgrade, repurpose, and deconstruction rules.
5. **Resource model:** deterministic starting stock, production, consumption, reserve, loss, trade, expedition gain, and forecast calculations.
6. **Utility model:** capacity/demand, topology simplification, priority, condition, backup, failure thresholds, cascade transitions, repair, and recovery.
7. **East/West feasibility:** both routes through Day 7 under competent normal play, imperfect play, Highball/no-Highball, Juna decisions, and representative signal choices.
8. **First-session timing:** tutorial sequence and time-to-first meaningful assignment, visible improvement, forecast, and safe stop.
9. **Safe stopping points:** exact transaction boundaries for construction, incidents, signals, visitors, promises, and expedition nodes.
10. **Deterministic seven-day proof:** a reproducible model showing required, optional, and buffer capacity each day.
11. **Failure and recovery margins:** how much response time and reserve a competent player receives, plus causal recap inputs.
12. **Forecast presentation:** which numbers/ranges are exposed and how uncertainty is represented without deception.

## Unresolved calculations

Prompt 2 must define or bound:

- real seconds per in-game work interval and expected session duration per day;
- phase lengths and whether they are time-driven, work-capacity-driven, or hybrid;
- number of concurrent assignments and interruption behavior;
- base work units per resident and skill/condition modifiers;
- travel-time contribution from layout and how it is summarized;
- Fatigue accumulation/recovery, Stress pressure/recovery, Hunger cadence, and Health limitations;
- consumption per resident/day for Food and Clean Water;
- Medicine use for injury, respiratory exposure, and waterborne illness;
- Materials summary conversion and detailed component blockers;
- Charge capacity, Power shortfall coverage, discharge limits, and losses;
- Power/Air/Water capacity and demand per representative room/equipment state;
- Structure zone thresholds, reinforcement effect, storm load, and closure rules;
- reclaim/connect/build/upgrade/repurpose work and cost for both routes;
- component rewards and opportunity cost from the nightrun/trader;
- Highball work benefit, known costs, conditional risk, cooldown/eligibility, and promised-rest repayment;
- storm timing, warning lead, cascade thresholds, response work, and recovery cost;
- Juna’s Day 6 consumption/capacity/treatment impact and alternatives;
- minimum viable and comfortable buffers at each day ledger;
- conditions for Prepare Platform, Root Settlement, Strengthen Relay, and Recover First slice endings.

All numbers must be marked **provisional** until a playable build validates them.

## Required simulations

At minimum, construct a deterministic spreadsheet, script, table model, or equivalent reproducible artifact for:

1. **East / standard plan / no Highball.**
2. **East / selected Highball / promise kept.**
3. **West / standard plan / no Highball.**
4. **West / selected Highball / promise kept.**
5. **Each route with one common imperfect decision** and a viable recovery path.
6. **Each route with the opposite signal commitment** affecting trader/drainage/expedition information.
7. **Juna admitted versus not immediately admitted**, showing capacity and human consequences without declaring morality.
8. **Active versus delegated nightrun** using identical graph inputs and no mandatory mode-exclusive reward.
9. **Day 5 cascade with each main intervention path** and one extended-neglect path.
10. **Save/reload state snapshots** at every phase boundary and risky transaction.

Each run must report by phase/day:

- resident assignment and usable work capacity;
- travel, treatment, rest, and promise obligations;
- stock start, changes, end, minimum reserve, and forecast;
- utility capacity, demand, condition, connection, priority, backup, and failure state;
- construction/reclamation progress and dependencies;
- signal commitment/expiry and knowledge changes;
- incident stage and response window;
- ending functional areas and acceptance conditions;
- buffer or deficit and why.

## Required prototype questions

Prompt 2 should specify tests and expected evidence for these questions; implementation can follow in the appropriate later stage.

1. Can a new player reach a meaningful station change in the first 2–3 minutes?
2. How many meaningful decisions fit a normal session before fatigue or UI overload?
3. Can players distinguish stocks from utilities, especially Charge from Power?
4. Can players diagnose the Day 5 cascade using one overlay at a time?
5. Does Room Focus accelerate selection without making overview state easy to miss?
6. Does travel/layout matter enough to notice but not enough to create tedious waiting?
7. Does East feel safer socially/medically without being universally stronger?
8. Does West feel resilient and resourceful without making comfort irrelevant?
9. Is Highball tempting but optional, and are its costs remembered?
10. Can one nightrun graph feel spatial in both active and delegated modes?
11. Are signal confidence, commitment, expiry, and opportunity cost understood?
12. Does the Juna decision feel grounded in capacity and relationships rather than authored moral scoring?
13. Can an interrupted app resume every risky state without hidden advancement or outcome change?
14. Does Day 7 visibly and emotionally contrast with Day 1?

## First-session output required

Prompt 2 must provide a minute-by-minute or bounded first-session sequence including:

- resume/offline-pause statement;
- first overview scan;
- first Room Focus;
- first resident assignment;
- first visible task response;
- first stock/utility distinction;
- first forecast;
- first small shelter improvement;
- first signal teaser;
- first safe stop and reload opportunity.

It must state what is skippable, what pauses the simulation, and how reduced motion/large text affect timing.

## Deterministic model acceptance gates

Prompt 2 is complete only if:

- [ ] Required quantities and formulas are explicit, internally consistent, and labeled provisional.
- [ ] Both East and West can complete all mandatory slice proofs without mandatory Highball.
- [ ] Highball creates a useful alternative and real repayment, not an optimal spam action.
- [ ] At least one imperfect-play state per route can recover through understandable action.
- [ ] Day 5 failure is possible through deliberate risk/extended neglect but not an unseen roll.
- [ ] Required work fits resident capacity with a visible buffer; optional work is clearly separated.
- [ ] Food, water, medicine, materials/components, and Charge remain viable through Day 7 in representative plans.
- [ ] Utility overlays can derive plain-language cause/forecast from the model.
- [ ] Juna paths account for capacity and treatment honestly.
- [ ] Active/delegated expedition results derive from the same graph state.
- [ ] Normal day/session targets and longer optional nightrun sessions are reconciled.
- [ ] Safe stopping points cover every dangerous or irreversible transaction.
- [ ] No closed-app simulation advancement is introduced.
- [ ] Sensitivity analysis identifies which provisional numbers are fragile.
- [ ] Discovered contradictions are proposed as logged concept changes, not hidden tuning.

## What must not be expanded yet

Do not use Prompt 2 to design or produce:

- detailed full resident AI, broad cast arcs, or runtime-generated dialogue;
- full combat, security, faction, trader, or visitor systems;
- multiple expedition maps or direct joystick controls;
- complete crafting/item balance or large recipe catalogs;
- Act II/III event catalogs, final Signal 45 truth variants, or complete endings;
- final graphics, production character/room assets, rigs, cinematics, or marketing images;
- store packaging, final entitlement UX, pricing, achievements, or platform submissions;
- multiplayer, PvP, online raids, procedural stations, vehicles, children, pregnancy, generations, pets, hundreds of residents, realistic fluids, particle air, freehand walls, full voice acting, extra maps, or endless mode.

## Prompt 2 deliverables

Recommended artifacts for the next stage:

1. pacing and phase specification;
2. work-capacity model;
3. stock/utility formula sheet;
4. construction cost/work table;
5. deterministic seven-day route matrix;
6. failure/recovery state-transition table;
7. Highball calculation and promise repayment model;
8. nightrun shared-graph resolution table;
9. first-session timeline;
10. safe-save transaction matrix;
11. sensitivity analysis and revised risk/decision entries.

Do not begin Prompt 2 until explicitly requested.
