# 01 — DESIGN PILLARS AND ANTI-PILLARS

**Status:** LOCKED. Every feature proposal in later prompts must pass the tests in this document.

---

## Part A — The five design pillars

### Pillar 1 — One station, every system connected

- **Meaning:** Kestrel Cross is a single legible machine. Power, water, air, heat, and seals are not parallel meters; they are a network in which each subsystem loads the others, and the player can *see the connections* in the cutaway view.
- **Player-facing behavior:** The player learns to read the station like an engineer reads a panel: a browning lamp string means the flywheel is sagging; a sagging flywheel means the cistern pump slows; a slow pump during swelter means rationing tomorrow. Players predict failures before failing, and describe the station causally ("we lost water *because* the scrubbers ate the charge margin").
- **Supporting mechanics:** A single power budget (charge) drawn on by scrubbers, pumps, lights, and tools; heat load that rises during swelter and degrades machines and people; utility states with three readable stages (failing → jury-rigged → restored); failure cascades that always pass through a visible intermediate warning state; repair as targeted work orders, not tap-to-fix.
- **Supporting presentation:** Side-cutaway camera with the whole slice station on one screen at overview zoom; animated "vitals" per room (lamp warmth, pipe drip, fan spin) that *are* the telemetry; cable and pipe runs drawn in the architecture so dependency is literally visible; alarm audio that identifies the subsystem by timbre before the player looks.
- **Concrete example:** During the Day-4 cinderfall storm, intake filters clog. Scrubber draw rises; the flywheel dips below pump threshold; the cistern gauge stops rising. The player chooses: cut the canteen's hotplate (human ledger cost: cold meals, Strain up), throttle scrubbers (Condition risk), or send a fitter into the hot intake shaft mid-storm (injury risk). Any choice works; each posts differently to the two ledgers.
- **Rejection test:** *If a proposed system's state cannot be read from the station picture itself — or if its failure arrives without passing through a visible intermediate state — redesign it or reject it.* (Kills: hidden global modifiers, off-screen resource sinks, instant unheralded breakdowns.)

### Pillar 2 — People are machinery that breaks differently

- **Meaning:** The survivors are the second network. They have needs (Hunger, Fatigue, Condition, Strain), aptitudes (Fitter, Medic, Runner, Steward), values, bonds, grudges, and Marks (durable memories of what happened to them and what you decided). They matter *mechanically*, not decoratively — and unlike machines, they remember.
- **Player-facing behavior:** Players make assignments as personnel decisions, not slot-filling ("Teo's fast but he's carrying that clinic decision; send Imka, she won't flinch"). Players can narrate each survivor's week afterward. Refusals, requests, and reconciliations feel earned, because their causes are visible in the record.
- **Supporting mechanics:** Aptitude fit changes work speed, quality, and accident odds; Strain modifies everything and vents through visible behavior (snapping, withdrawal, refusal) before breakdown; values act as hard lines — ordering a survivor across one costs Accord and creates a grudge; bonds/grudges alter pair efficiency and event branches; Marks permanently annotate a survivor's sheet and gate specific dialogue and endings.
- **Supporting presentation:** Survivors visibly perform their assigned work in the cutaway; posture and idle animation encode need states before any icon appears; a per-survivor "ledger page" UI showing needs, Marks, bonds, and outstanding promises; barks that reference actual recent events, not generic mood lines.
- **Concrete example (slice):** Teo petitions for radio time to search for his brother on the missing-persons band. Granting it costs a forecast slot before a storm cycle; refusing it marks Teo ("The Signal Refused"), raising his Strain and lowering his nightrun reliability until addressed — a delayed, legible, human-ledger consequence.
- **Rejection test:** *If a feature treats survivors as interchangeable units — if swapping two characters changes nothing mechanical or narrative — it violates this pillar. Any population increase that forces anonymity is rejected.* (Kills: dweller-breeding economies, faceless worker pools, stat-stick hiring.)

### Pillar 3 — Information is survival

- **Meaning:** The Listening Post makes *what you choose to know* a rationed resource with opportunity cost. Rumor and fact are different materials; converting one to the other costs capacity that could have gone elsewhere.
- **Player-facing behavior:** The nightly radio schedule is a deliberate, discussed decision ("forecast twice this week — storm season — so Signal 45 waits"). Players hold beliefs of varying confidence and *feel* the difference between choosing blind and choosing informed, especially at Relay Night and the campaign's ending gates.
- **Supporting mechanics:** Channel-hour slots per night (2–3 in the slice), constrained by antenna Condition and charge; signal categories (weather, Signal 45, traders, distress, faction chatter, personal) with distinct payoff types; intel with expiry (a cache broadcast decays; a storm forecast is worthless after the storm); verification as a progressive track per claim, not a binary reveal; unheard signals resolve off-screen and can return as events at the gate.
- **Supporting presentation:** The Listening Post as a warm, personal room — chalkboard of frequencies, punch-card schedule rack; audio design where tuning is tactile and each signal type has a sonic identity; the "day report" explicitly lists *what you did not listen to* as static-marked gaps.
- **Concrete example (slice):** Night 3 offers four signals and two slots: storm band (a front is forming), Linewalker Sable's trade beacon, a distress call on the Foundry Line, and Signal 45's carrier check. The player takes storm + trade. Day 5's storm arrives forewarned (seals pre-staged), Sable arrives with a known manifest — and on Day 6, two exhausted strangers reach the gate: the distress call, resolved without you, now standing in your doorway with one fewer member than it had.
- **Rejection test:** *If information arrives free, total, or without displacing other information — or if a "choice" signal has no consequence when ignored — the feature violates this pillar.* (Kills: omniscient map reveals, free quest markers, consequence-less flavor radio.)

### Pillar 4 — Night is a door, not a level

- **Meaning:** Nightruns are short, purposeful sorties that exist to feed the station — matter (salvage, meds, food), people (contacts, arrivals), and knowledge (confirmed intel). They are never a second, separate action game.
- **Player-facing behavior:** Players plan runs in the Slack phase like a checklist ritual — who, where, carrying what, back by when — and feel the station *behind* them during the run. A player who never wants to actively steer a run can delegate every one and still play the whole game well.
- **Supporting mechanics:** 3–6 minute active runs: touch-driven movement through a side-view location, risk-priced interactions (pry, wade, climb, approach a stranger), a hard air/heat clock, and a carry-weight commitment decision at the exit; full **delegate option** resolving any run from preparation quality, runner aptitude, intel level, and stated priorities; consequences flow *homeward* — injuries triage at the Aid Car, encounters knock at the gate later, and every location connects to the tunnel map, not an abstract mission list.
- **Supporting presentation:** Runs rendered in the same cutaway language as the station (a ruined mirror of home); the runner's lantern and mask filter as the visual clock; no HUD combat elements — threats are staged as environment and standoff, not target reticles; return-and-triage as a staged scene at the Scrubber Gate, not a loot popup.
- **Concrete example (slice):** The Marrow Street Clinic run: the med stock is real, but so are the squatters living on it. The active player choices are approach, barter, take-and-go, or leave; there is no "clear the room" option. Taking the insulin cold-stock is the slice's flagged delayed consequence — the squatters are Tidemill kin, and Day 6 brings that bill to the gate.
- **Rejection test:** *If an expedition feature would still make sense with the station deleted from the game, it is too big — reject or shrink it. If it requires reflex skill to avoid unfair loss (no delegate path, no telegraph), reject it.* (Kills: combat depth trees, boss encounters, expedition-only progression currencies.)

### Pillar 5 — Hope has a schedule

- **Meaning:** The emotional arc is authored rhythm, not ambient misery. Pressure, activity, consequence, recovery, and hope alternate at every timescale — phase, day, storm cycle, act — and hope beats are engineered as deliberately as crises.
- **Player-facing behavior:** Players end most sessions at a stable exhale (day report, safe stop), not mid-panic. They can feel the campaign's shape: storm seasons crescendo, Relay Nights punctuate, quiet days genuinely restore. They describe the game as tense and warm, not punishing.
- **Supporting mechanics:** The four-phase day (Swelter → Slack → Nightrun → Graymorn) with recovery mechanically located in Slack and Graymorn; storm cycles telegraphed days ahead (with forecast investment); scheduled hope beats — Relay Nights, trader arrivals, restorations (first hot water, lights on Level 3) — that carry mechanical bonuses (Strain relief, Accord gain), not just text; a cap on simultaneous active crises (max 2 in the slice) enforced by the event scheduler.
- **Supporting presentation:** Lighting warms as the station heals — restoration is *visible* room by room; music holds a quiet ambient floor, spending intensity only on storms and returns; the day report is framed as the stationmaster's log, ending on the state of people, not stockpiles.
- **Concrete example (slice):** Day 5, storm's end: the seals held. Graymorn's report notes the repaired scrubber, then — because Accord is above threshold — a small scripted scene: Maren reopens the canteen shutter and the survivors eat together under the newly-fixed platform lamps. +Strain recovery, +Accord. The scene exists *because* the player got them there; it is withheld in the fractured state.
- **Rejection test:** *If a feature adds pressure without a paired recovery or telegraph — or if it could make the third consecutive simultaneous crisis — it violates this pillar. Any "hope" content with no mechanical weight is decoration, not a hope beat; rework it.* (Kills: random no-warning disasters, doom-stacking event rolls, purely cosmetic morale.)

---

## Part B — The five anti-pillars

What Cinderline refuses to become. Each names the feature type it forbids.

### Anti-pillar 1 — Not an idle tap-collector

Cinderline never generates value from the player's absence and never asks for a visit to *harvest* rather than *decide*. **Forbidden feature types:** offline resource accrual; tap-to-collect production bubbles; login streaks and daily gift calendars; timers whose only interaction is waiting or paying; notification hooks engineered to reopen the app ("your water is ready!"). Production runs only while the player plays; sessions exist to make decisions, not collect yield.

### Anti-pillar 2 — Not a city, not a crowd

Cinderline never zooms out past names and faces. **Forbidden feature types:** population growth beyond the named-cast ceiling (~12 full game); anonymous migrant/worker pools; district- or zone-level abstractions; statistical "population happiness" replacing individual Accord contributions; any system whose UI would need a spreadsheet of people. If a feature needs more people than the player can know by name and history, it is out of scope by identity, not by budget.

### Anti-pillar 3 — Not a combat power fantasy

Violence in Cinderline is rare, costly, avoidable, and never the reward loop. **Forbidden feature types:** weapon tiers and damage progression; kill-counting or combat XP; encounters that must be won by force; enemy factions that exist to be cleared; loot pinatas guarded by fights. The nightrun verb set is *reach, take, talk, avoid, flee* — a standoff is a dialogue with body language, and hurting someone is a Mark on the survivor who did it, every time.

### Anti-pillar 4 — Not a micromanagement treadmill

The player commands at the level of intent — shifts, priorities, work orders — never at the level of bladders and footsteps. **Forbidden feature types:** per-survivor need-servicing orders (eat now, sleep now); conveyor/logistics routing puzzles; per-item inventory shuffling between containers; any recurring decision that is identical every day (auto-standing orders must exist for anything done three times); more than ~4 pending decisions queued at once. If optimal play would look like janitorial tapping, the system is misdesigned.

### Anti-pillar 5 — Not a misery slot machine, and never paid relief

Suffering in Cinderline is always causal, telegraphed, and answerable — and never for sale. **Forbidden feature types:** unheralded random deaths or irreversible losses without a prior visible warning state; difficulty via dice rather than via dilemmas; and categorically — per the monetization restrictions — loot boxes, paid resources/medicine/food, energy gates, compulsory ads, paid revivals, or any purchasable relief from designed pressure. The business model is a free first chapter and one permanent unlock; monetization may never touch the simulation. (This anti-pillar also forbids *designing* pressure whose obvious relief valve would be a purchase, even before any store exists.)

---

## Part C — Feature-decision tests (apply to every future proposal)

A proposed feature must pass **all five gates**:

| # | Gate | Question | Instant-fail examples |
|---|------|----------|----------------------|
| T1 | Readability | Can its state be read from the station picture or a single ledger page, and does failure telegraph through a visible intermediate state? | Hidden modifiers; surprise catastrophic rolls |
| T2 | Personhood | Does it treat survivors as specific people (names, memory, refusal), and survive the "swap two survivors — does anything change?" check? | Faceless labor pools; breeding economies |
| T3 | Cost of knowing | If it delivers information, does that information displace other information or cost something real? | Free map reveals; omniscient alerts |
| T4 | Station gravity | Does it feed or draw on the station? Would it still make sense if the station were deleted? (If yes → reject.) | Expedition-only progression; minigames |
| T5 | Rhythm | Does it respect the pressure/recovery alternation and the two-crisis cap, and is any new pressure paired with telegraph + recovery? | Doom-stacking; no-warning disasters |

Plus the standing constraints: no monetization contact with simulation (Anti-pillar 5), landscape one-screen readability, and a safe stop within 12 minutes of any point.

## Part D — Worked examples

**Accepted features (pass all gates):**

1. **Antenna repair raises Listening Post capacity** — readable (antenna is a visible rooftop structure with damage states), station-gravity (built by fitters from salvage), cost-of-knowing (capacity remains scarce, just less scarce), rhythm (a restoration hope beat). *Accepted for full game; slice has fixed capacity.*
2. **Pair assignments with bond/grudge modifiers** — personhood (specific pairs matter), readability (bond lines on ledger pages), rhythm (reconciliation arcs are recovery content). *Accepted; slice ships one scripted conflict pair.*
3. **Delegated nightrun resolution** — station-gravity (outcome derives from preparation the base produced), personhood (runner's aptitudes/Marks drive the roll and the report), readability (the return report explains outcomes causally). *Accepted; slice requires it (accessibility baseline).*

**Rejected features (with the gate that killed them):**

1. **Radio minigame: signal-tuning dexterity puzzle each night** — fails T5 and mobile constraint (adds reflex friction to a decision ritual) and T4 (a game apart from the station). The schedule *choice* is the game; tuning is presentation.
2. **Raider defense wave mode** — fails Anti-pillar 3 and T5 (combat as recurring pressure loop); external threat instead arrives as standoffs, arrivals, and faction pressure at the gate.
3. **Breeding/recruit-stream population growth** — fails T2/Anti-pillar 2 outright. New people arrive rarely, as authored arrivals with histories.
4. **Offline generation ("the station keeps working while you're away")** — fails Anti-pillar 1 and the offline-safety quality gate (absence must be consequence-free in both directions).
5. **Fog-of-war overworld map with scouting units** — fails T3 as designed (unit-scouting bypasses the Listening Post's zero-sum knowledge economy) and Anti-pillar 2 (map-scale play). The tunnel diagram + radio intel *is* the map.
