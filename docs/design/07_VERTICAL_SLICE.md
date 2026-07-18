# Signal 45 — Vertical Slice: The First Count

## Slice purpose

**The First Count** is a complete seven-day mini-campaign that proves the risky core of Signal 45: a visible shelter grows through understandable work; systems can fail and recover; named people respond to how they are treated; uncertain signals change practical decisions; and one compact nightrun serves the base.

It does not prove a complete 45-day content pipeline, late population scale, final art, complete resident AI, full crafting balance, or production readiness.

## Starting station

### Functional areas (approximately four)

1. **Platform Camp (Rest):** four bedrolls, poor privacy, high noise, no fifth berth.
2. **Relay Kiosk (Operations):** improvised receiver, one listening commitment at a time, intermittent antenna path.
3. **Service Alcove (Utility):** weak power connection, small Charge reserve, damaged air filtration, unreliable water pump access.
4. **Concession Cage (temporary Storage/Food use):** secured small inventory and cold ration preparation using one crowded space.

### Visible station state

- central platform and main gate;
- blocked East route through a staff corridor;
- blocked West route toward a flooded pump/track service area;
- jammed vertical stair/lift route, visible but not slice-expandable;
- damaged utility trunks, rubble, flooding, cinder ingress, structural cracks, broken lights;
- several visibly unusable bays that can become part of the ending station;
- limited Food, Clean Water, Medicine, Materials, and Charge;
- limited Power, limited Clean Water delivery, damaged Air, and local Structure risk.

Prompt 2 now defines the provisional starting quantities and deterministic feasibility in `tools/feasibility/data/model.json`. They remain model inputs rather than final balance.

## Canonical slice residents

No prior repository canon existed beyond the title, so Prompt 1 locks these provisional names as slice canon. Details are intentionally bounded; Prompt 2 may quantify effects but should not expand into full resident AI.

| Resident | Useful skills | Weakness / condition | Values and preferences | Fear / boundaries | Key relationship and recovery behavior |
|---|---|---|---|---|---|
| **Ash** | Structural survey, clearing, bracing, salvage judgment | Pushes through Fatigue and underreports pain | Practical proof, visible progress, early starts, well-organized tools | Hard boundary: ordered entry into an unshored red zone. Soft boundary: wasteful rework. | Trusts Imka’s judgment but clashes with Maren over accepting delay. Recovers by doing low-risk tool maintenance near others. |
| **Imka** | Triage, illness recognition, treatment, calm negotiation | Slower heavy work; Stress rises when care space is unsafe | Clean work surfaces, consent, protected recovery time | Hard boundary: denying emergency stabilization to leverage compliance. Soft boundary: using dirty water for care. | Protective of Teo’s respiratory risk; respects Maren’s logistical honesty. Recovers through quiet inventory and one-on-one check-ins. |
| **Teo** | Electrical repair, radio tuning, utility monitoring | Respiratory sensitivity; generator/fan noise disrupts sleep | Redundancy, accurate forecasts, repairing old systems | Hard boundary: cinder work without effective protection. Soft boundary: overtime after a broken rest promise. | Looks to Ash for technical confidence but resents being volunteered. Recovers in a quiet berth away from the Service Alcove. |
| **Maren** | Logistics, ration planning, carrying, food handling, visitor screening | Limited technical repair; becomes rigid under high Stress | Fair counts, prepared capacity, shared meals, explicit agreements | Hard boundary: surrendering named residents’ medicine without consent. Soft boundary: admitting people with no declared sleeping/air plan. | Challenges Ash’s risk tolerance; builds trust by keeping distribution promises. Recovers by organizing a communal meal. |
| **Juna Malek** | Water treatment, pump operation, patient instruction | Arrives dehydrated and exhausted; cannot immediately carry full workload | Mutual aid, keeping companions informed, useful work without coercion | Hard boundary: separation by deception from her outside group. Soft boundary: being treated as admission payment. | Has an obligation to the outside group at the gate. Recovers with clean water, uninterrupted sleep, and honest contact. |

Every character also has authored personal preferences, memories, work preferences, and promise hooks in the slice data. There are no rarity tiers or overall levels.

## Slice room families

The slice uses exactly seven true families: **Rest, Medical, Food, Storage, Utility, Workshop, and Operations/Radio**. Temporary combined areas are allowed; the ending shelter contains approximately eight to ten functional areas, not eight to ten distinct system families.

## East versus West

Both routes are viable. The route choice changes the easiest recovery tools and layout, not whether the player is allowed to succeed.

| Dimension | East — Staff & First-Aid Wing | West — Pump & Service Gallery |
|---|---|---|
| Shell | Drier staff rooms, old first-aid bay, damaged but shorter internal corridor | Flooded track service area, pump gallery, salvage cage, rough exposed surfaces |
| Early strength | Rest capacity, treatment comfort, lower Fatigue/Stress, earlier fifth berth | Water security, drainage control, storm recovery, more salvage/components |
| Early weakness | Weaker water/drainage security and fewer early components | Rough sleeping, cold meals, more noise/damp, higher Stress |
| Layout consequence | Clinic/berths are farther from the main gate; visitor or expedition treatment has longer response travel | Utility/Stores are near gate/service access, but comfortable recovery remains on the central platform |
| Storm tool | Better treatment and rested responders; must improvise water isolation/reserve | Better drain/pump isolation and repair stock; must manage fatigue, stress, and respiratory comfort |
| Likely upgrade | Platform Camp → East Bunkroom/Quiet Berths or Triage → Clinic | Service Alcove/Pump equipment → treated-water capability or West Stores → Workshop |
| Likely repurpose | Concession Cage can become dedicated Food once East storage/lockers are fitted | Concession Cage can become better Rest/Food use once West Stores take inventory |
| Juna pressure | A berth exists more easily, but water forecast may not support a fifth person without restrictions | Water supports admission more easily, but adequate rest/privacy must be improvised |

No route receives strictly better stocks, resident outcomes, and incident answers. Prompt 3 tests both deterministically, including imperfect but competent play: East and West reach ten functioning areas and Full Proof without Highball. Weekly unused WU is no longer presented as the whole safety margin; Day 5 consumes all uncommitted response slack.

## Seven-day beat sheet

### Day 1 — The Count

**Purpose:** Practice one complete shelter action while demonstrating only the minimum stock, utility, condition, and pause context needed to understand it.

- Graymorn opens on the four residents counting supplies and confirming that the station clock paused while the game was closed.
- The player practices selecting the damaged platform lamp, entering Room Focus, assigning one resident, confirming the repair, returning to Overview, and accepting a safe save.
- Only one Food forecast, one Power connection warning, Teo's contextual Health exposure, and Pause are demonstrated. The player is not asked to master all five stocks or four utilities.
- Imka identifies Teo’s early cinder exposure as treatable if dusty tasks are limited and protection is prepared. It is a warning, not random damage.
- The Relay Kiosk catches two incomplete bursts: a municipal drainage code and a medical trader call. Neither can be fully followed yet.
- The repaired platform lamp supplies the first visible improvement at the modeled 4.1-minute mark. The safe ledger is budgeted at 6.1 minutes.
- **Safe stops:** after each tutorial action, after assignments, and at the Day 1 ledger.

**Proof:** 32-second baseline interaction, resident assignment, Room Focus, one stock forecast, one utility warning, visible activity, and save/reload tutorial. Listening Post, routes, other utilities, Highball, and Nightrun are teased; advanced systems are withheld.

### Day 2 — Choose a Wing

**Purpose:** Teach Survey/Reclaim/Connect and commit East or West without implying a correct answer.

- The player surveys both blockages. Forecast cards state route strengths, hazards, work/component needs, and uncertainty.
- Choose the first route; the unchosen route remains visible and available later in the campaign, not permanently erased.
- During controlled clearing, Ash's work exposes unstable debris. The player can reinforce first, change worker/protection, or accept a labeled injury risk to finish sooner.
- **Good preparation prevents a new injury.** A deterministic authored injury occurs only after at least two visible accepted hazards, such as accepting the risk without protection, ignoring a warning, or delaying stabilization. It never exists merely to force the tutorial.
- The guaranteed Medical path is Teo's existing respiratory exposure and examination. If the player accepts the construction risk, Imka additionally stabilizes that injury at the triage cot; Medicine, Clean Water, travel, and room condition determine its recovery forecast.
- A new signal choice appears: commit Relay attention to the drainage code or the trader call. It expires on Day 3/4 and visibly changes forecasted opportunities.
- **Safe stops:** after survey, before route commitment, after hazard stabilization, and at the ledger.

**Proof:** reclamation, East/West choice, injury prevention or causal injury, warning/response, treatment through at least one forecast path, and signal commitment.

### Day 3 — On the Wire

**Purpose:** Connect the Listening Post to one shared active/delegated expedition graph.

- Reclamation opens a partial bay and exposes a project blocked by a detailed component family—filter media, pump seal, or electrical relay—not merely “Materials.”
- Signal follow-up or direct station need identifies the **Harbor Line Maintenance Annex**, a compact side-cutaway nightrun location.
- The player sets a shelter objective: obtain the missing component, verify drainage information, or meet the trader’s relay contact.
- Slack shows route, age/confidence of information, time, noise, visibility, air-protection requirement, carry limit, tools, injury factors, and retreat point.
- Choose **Delegate** or **On the Wire**. Both use the same nodes and rules. Active play selects routes/actions at visible nodes; it has no joystick and no routine combat.
- The location persists: a forced locker stays open, a bypassed hazard remains, taken components are gone, and a discovered route annotation is retained.
- Graymorn resolves return, inventory, exposure, relationship reactions, and any promise. Retreat is a valid outcome with partial knowledge.
- **Safe stops:** before run commitment, at each secured node, after each irreversible encounter transaction, and after debrief.

**Proof:** active/delegated nightrun, signal-to-expedition causality, spatial presentation, persistent location, save serialization.

### Day 4 — Make It Ours

**Purpose:** Complete the first wing, demonstrate construction choice, an upgrade, adaptation/repurpose, and human conflict.

- The selected wing is made safe and connected to one utility branch.
- Build one permanent or improved function in a compatible bay and install a major equipment/module.
- Complete **one room upgrade** and **one adaptation/repurpose**. The recommended demonstration depends on route but the player chooses among valid compatible plans.
- Travel and utility previews reveal the route’s meaningful layout consequence (East treatment distance from gate or West recovery/noise distance).
- Ash wants construction finished before the forecast storm; Maren argues for reserve and living capacity. The disagreement uses real project/stock/condition facts.
- A **Highball Order** becomes optional: finish reinforcement/filter/pump work before the storm for one of three provisional displayed timing candidates. Known costs include named-resident Fatigue/Stress, Charge, material wear, deterministic strain, inspection, and a promise of rest. There is no hidden breakdown roulette.
- Competent normal play can prepare without Highball by narrowing the plan. Highball creates margin, not a paywall or mandatory answer.
- If used, the player records a specific rest promise. If refused or negotiated, the reason is shown.
- **Safe stops:** before placement confirmation, after undo window, before Highball, after promise, and at the ledger.

**Proof:** Build/Operate/Adapt, upgrade, repurpose, equipment placement, layout consequence, relationship conflict, Highball.

### Day 5 — Cinder Front

**Purpose:** Test forecasting, one storm, a legible failure cascade, intervention, and recovery.

- The storm forecast states arrival, confidence, expected cinder load, vulnerable Air branch, Power/Charge headroom, Structure concern, and response options.
- The storm applies one environmental pressure and a maximum three-system cascade: **cinder front → Air → Power → Water**. Preparation may stop it after Air or Power; not every link fires in every run.
- East and West meet different weak links. East leans on rested responders/clinic while improvising drainage or water reserve. West isolates/pumps more effectively but manages tired, stressed residents and rough recovery space.
- Interventions include stopping Workshop or another load, discharging Charge, isolating a branch, replacing/repairing filter equipment, protecting/evacuating a zone, repairing a pump, using clean reserve, or accepting a forecast consequence.
- Only one major crisis may be live; minor consequences queue. Every active stage shows cause, effect, likely next effect, escalation allowance, intervention, known cost, and uncertainty. Structure warnings can close, but not randomly destroy, one project area. A responder can be injured only after a visible risk decision or extended missed response.
- The game pauses for serious decisions and presents plain-language reasons. No death is used as the main challenge.
- After the peak, lights and machinery visibly show what held, failed, and was repaired.
- **Safe stops:** immediately on background, before each incident commitment, after each stabilized cascade stage, and at Graymorn recap.

**Proof:** storm, failure cascade, utility priority/backup, warning, intervention, injury/treatment if applicable, causal recap, route viability.

### Day 6 — Room at the Gate

**Purpose:** Test visitor/trader/outside-group systems, admission under real constraints, and delayed human consequence.

- The medical trader arrives early, late, or via a less favorable arrangement depending on the Day 1–2 signal commitment. Inventory and knowledge differ; the trader is not a generic shop timer.
- An outside group reaches the main gate with **Juna Malek**, exhausted and able to help with water systems after recovery. Her companions cannot all be housed safely inside under the current slice capacity.
- The decision panel shows berth count, Air/Water/Food forecasts, treatment queue, gate security, Juna’s condition/obligation, and resident concerns.
- Viable approaches include:
  - admit Juna with her informed consent and a contact/support agreement for companions;
  - create temporary internal/external holding by sacrificing another project or reserve;
  - negotiate supplies, water expertise, and a later admission review without immediate residence;
  - refuse entry while offering only what the station can safely spare;
  - a better prepared shelter may admit more than one person, but the slice need not support the entire group permanently.
- Juna is never a reward for choosing the “good” button and never becomes immediate labor payment. She needs water, treatment/rest, honest communication, and a place.
- Maren objects if no berth/air plan exists; Imka objects to coercive stabilization terms; Ash may support admission if the station work can make it safe. Teo’s response reflects whether protection/rest promises were kept.
- **Delayed consequence from Day 4:** keeping the Highball rest promise yields voluntary help or calm cooperation now; breaking it produces reluctance/refusal and relationship strain. If Highball was not used, an earlier signal, treatment, or expedition promise provides the delayed check.
- **Safe stops:** before trade confirmation, before admission commitment, after agreement serialization, and after the relationship scene.

**Proof:** trader, outside group, Juna decision, capacity/forecast integration, relationship conflict, promises, delayed consequence.

### Day 7 — The First Count

**Purpose:** Demonstrate recovery, visible transformation, evidence, and an earned ending direction.

- The community repairs storm damage, completes treatment, and counts the station’s new capacity. A recovering resident returns to a preferred low-risk activity.
- A **hope beat** uses what was built: a warm communal meal, the first quiet uninterrupted sleep, clean water at a marked tap, or residents relighting a restored platform sign.
- The Listening Post resolves the followed signal and exposes one credible but incomplete Signal 45 evidence fragment. It also records what expired and the practical opportunity cost without shaming the player.
- The ending station contains approximately eight to ten functional areas across seven families, including visible improvements, one reclaimed wing, extended utilities, personal traces, and storm repairs.
- The final commitment is a physical near-term priority for the next act, supported by existing state:
  - **Prepare the Platform:** preserve access and verify evacuation logistics;
  - **Root the Settlement:** invest in water, food, berths, and permanent community capacity;
  - **Strengthen the Relay:** expand listening/rebroadcast capability and outside-network ties;
  - a damaged shelter may instead choose **Recover First**, an honest costly-survival result that protects life but delays larger ambition.
- This is not the Day 45 ending and not a detached morality choice. Available confidence, project cost, resident willingness, and closing montage derive from route, construction, evidence, admission, promises, and recovery.
- The final ledger shows concrete consequences and explicitly states which questions belong to the full campaign.

**Proof:** Day 7 resolution, recovery path, hope, signal evidence, ending decision, accumulated-state evaluation, visibly expanded home.

## Storm and failure-cascade contract

The cascade must be deterministic enough to explain, with authored variability used only within displayed conditions. At each stage the player receives:

- current cause and next likely consequence;
- time/work window before escalation;
- affected rooms/residents/networks;
- at least one available intervention in a competently prepared route;
- cost and known side effects;
- labeled uncertainty where applicable;
- post-event causal recap.

The player may finish with damage, illness, lost materials, missed opportunity, or strained relationships. The slice must also allow recovery and cannot require random death.

## Expedition contract

The Harbor Line Maintenance Annex graph contains a small number of visible nodes—entry, service passage, maintenance cage, control booth or drainage junction, and retreat route. Active and delegated modes share:

- node/edge topology and travel time;
- darkness, visibility, and noise state;
- air protection and exposure;
- tool checks and carry capacity;
- injury/encounter risks and warnings;
- stateful objects and taken items;
- retreat and partial-success rules;
- serialized committed outcomes.

Active mode offers informed node choices and observation; delegated mode applies the selected route policy, equipment, retreat threshold, and resident judgment to the same model. Neither mode grants unique mandatory resources solely to force a preferred play style.

## Admission decision contract

- Juna’s identity, condition, consent, obligations, and station impact are explicit.
- “Admit” is not automatically correct; unsafe admission can harm Juna and residents.
- “Refuse” is not automatically evil; honest limits and aid differ from deception, exploitation, or indifference.
- Preparation can create better options.
- Juna is never rare, purchased, instantly recovered, or obligated to work for admission.
- Consequences affect people, supplies, outside relationships, water capability, evidence, and later willingness.

## Safe stopping and reload test points

- after every confirmed construction/assignment transaction;
- before and after route choice, Highball, signal commitment, trade, and admission;
- at every stabilized incident stage;
- at every secured expedition node;
- at every phase boundary and day ledger;
- immediately on app background, with simulation paused.

Reload testing must reproduce construction stage, resident position/task/condition, utility networks/priorities, stock and detailed items, incident stage, forecasts, signal expiry/commitment, expedition node/site state, promises, memories, relationships, visitor state, and deterministic random-stream position.

## Acceptance criteria

The slice passes only when:

- [ ] It completes in seven in-game days through both East and West with no hidden correct route.
- [ ] It starts with about four and ends with about eight to ten functional areas across seven room families.
- [ ] Overview and Room Focus work on target mobile hardware with reduced motion and accessible targeting.
- [ ] Assignment, Reclaim, Connect, Build, Operate, Adapt, one upgrade, and one repurpose are playable and visible.
- [ ] Stock and utility forecasts are understandable; only five stocks occupy the main HUD and one utility overlay is active.
- [ ] Exactly four primary resident condition meters are used.
- [ ] One layout decision changes travel, utilities, safety, capacity, or recovery in a previewable way.
- [ ] The storm cascade has warnings, intervention, consequences, recap, and recovery.
- [ ] Injury, respiratory exposure, waterborne risk, treatment, and recovery are demonstrated without random death as the core challenge.
- [ ] Highball is optional, discloses benefits/costs/uncertainty, and creates a persistent consequence.
- [ ] A signal changes ordinary shelter, trader, storm, expedition, or ending state.
- [ ] One nightrun graph works actively and through delegation from the same state model.
- [ ] A trader and outside group appear, and Juna’s admission is a capacity-and-values decision rather than a morality test.
- [ ] At least one promise or earlier choice produces a delayed human consequence.
- [ ] At least one recovery/hope scene uses the changed station.
- [ ] The ending direction is earned from accumulated state rather than one detached dialogue option.
- [ ] Save/reload and background pause preserve state; nothing dangerous advances while closed.
- [ ] Safe stopping points are available throughout a normal mobile session.
- [ ] No result is described as proven fun, balanced, technically validated, or production-ready until corresponding tests pass.

### Prompt 3 additions to the slice proof

- Day 4 includes the zero-WU Relay Load Test: Charge, task-light shedding, or delay all remain viable.
- Day 5 is one major Cinder Front with Air → Power → Water maximum depth and queued ash-wash aftermath.
- Critical medical incapacity supplies zero productive WU; Teo’s exposure preserves the no-injury tutorial path.
- Day 7 may produce Full Proof, Recover First, Proof Incomplete, or Shelter Failure for distinct causes.
- Missing only the five-WU authored hope setup uses an earned zero-to-two-WU fallback and cannot create stock.
