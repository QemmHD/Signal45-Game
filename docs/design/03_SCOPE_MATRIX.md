# 03 — SCOPE MATRIX AND VERTICAL-SLICE DEFINITION

**Status:** LOCKED. Slice numbers match the recommended targets; the two documented adjustments are flagged inline (§3, notes A and B).
**Difficulty scale used below (solo dev / small team):** **S** ≈ 1–3 days · **M** ≈ 1–2 weeks · **L** ≈ 3+ weeks. Estimates are planning aids, not commitments.

---

## 1. Four-tier scope overview

| Feature area | Vertical slice | Full base game | Post-launch possibility | Cut or deferred |
|---|---|---|---|---|
| **Station** | One 3-level section of Kestrel Cross; 8 room types restored from pre-existing spaces | Full interchange; ~16 room types; restoration ladder per act | A second station scenario (different interchange, different question) | Free-form excavation/base-layout building (station spaces are authored) |
| **People** | 4 named survivors; needs ×4; aptitudes ×4; 1 scripted conflict pair; Marks | 8–12 named survivors; arrival arcs; full bond/grudge web; personal-signal arcs for all | New survivor arcs; "storyteller" pacing variants | Procedurally generated cast as the core cast; population beyond ~12 (Anti-pillar 2) |
| **Resources & crafting** | 5 primary resources; 12 craftables; single crafting queue | ~30–40 craftables; recipe discovery; workshop upgrades | Recipe variants, scenario-specific chains | Item quality tiers; per-item durability micromanagement |
| **Utilities** | Abstract network: charge, water, air, heat, seals; 3 damage states; 1 cascade crisis | Full network incl. antenna ladder, second cistern, Level-3 grid; storm-season load model | — | Physical routing sim (pipe/wire placement puzzles — see cut C3) |
| **Listening Post** | 2–3 slots/night; 6 signal categories; verification track for Signal 45 (slice-length) | Capacity ladder via antenna restoration; faction chatter; jamming/interference events; full verification arc | Community "frequency archive" (lore collection) | Signal-tuning dexterity minigame (rejected, 01 §D) |
| **Nightruns** | 3 hand-authored locations; active mode + full delegation; 1 scripted scavenging mission | 18–24 locations across 3 tunnel branches; multi-runner teams; location states that evolve with acts | Endless "deep line" survey mode | Procedural location generation (C2); any combat system (C5) |
| **Outside world** | 1 trader (Linewalker Sable); 1 faction (the Tidemill); gate arrivals | 3 factions + independent holdouts; standing agreements; Junction Event | Faction epilogue variations | Overworld map with movable units (rejected, 01 §D) |
| **Events** | 20 authored events incl. ≥5 delayed-consequence chains; max 2 concurrent crises | 120–180 events; act-gated pools; anti-repetition scheduler | Seasonal event packs | Random no-telegraph disasters (Anti-pillar 5) |
| **Campaign** | 7-day mini-campaign "The First Count"; 1 ending (state-reactive epilogue) | 35–50 days; 3 acts; 5 ending frames + 2 failure states; commitment gates | New-game+ modifiers; scenario seeds | Branching mid-campaign map/route choice (one station, one line) |
| **Platform** | iOS/Android landscape; touch controls; save/reload; perf on mid-tier devices | Cloud save; device-tier scaling; notification opt-in (player-scheduled only) | PC/Steam port; controller support; tablet layouts | Portrait mode; always-online anything; real-time offline simulation |
| **A/V** | Blockout-quality modular art, final art direction; basic SFX + 2 music states; captions | Full modular set, character animation library, adaptive score, full VO-free audio identity | Marketing cinematics (Higgsfield pipeline); OST release | Voice acting (text + barks only); photorealism |
| **Accessibility** | Scalable text, color-safe palette + icon shapes, no reflex requirement in base loop, delegation path, captions | + screen-reader labels on ledgers, reduced-motion mode, left/right-hand layouts | + full audio-description pass | — |
| **Business** | No store; slice is chapter-1-shaped by design | Free Chapter One (Days 1–7) + single permanent unlock; no consumables ever | Cosmetic-free by policy; paid *scenario* expansions only | All monetization listed in restrictions (loot boxes, energy, ads, paid relief) — **cut permanently** |

## 2. The five-plus deliberate cuts (appealing but dangerous)

| ID | Cut feature | Why it is appealing | Why it is cut from the slice (and mostly the base game) |
|---|---|---|---|
| C1 | **Multi-faction political web** (3+ factions with reputation interplay) | Depth, replayability, "living world" | Quadratic content cost; dilutes the Tidemill's characterization; slice needs one *deep* outside relationship to prove the pattern. Full game caps at 3 factions. |
| C2 | **Procedural expedition locations** | Infinite content, replay value | Procedural ruins are anonymous ruins — they break Pillar 4's "purposeful sortie" and the intel economy (intel must reference authored truths). Hand-authored locations with state changes instead. |
| C3 | **Physical utility routing** (place pipes/wires, flow sim) | Satisfying systems depth (ONI-style) | A second engineering game; mobile screen budget can't carry routing UI; the *abstract* network already delivers the cascade drama. Permanently out. |
| C4 | **Deep relationship arcs / romance web** | Emotional richness | Content explosion and tone risk; slice proves the machinery with one authored conflict (Teo vs. Imka over radio time). Full game grows bonds/grudges systemically, still no romance system. |
| C5 | **Any combat system** | Market expectation; "night danger needs teeth" | Anti-pillar 3. Danger is environmental + standoff-shaped. Cutting combat is an identity decision, not a budget one. Permanently out. |
| C6 | **Free-form base building** (dig, place, rearrange rooms) | Player expression; genre expectation | Authored station spaces are the readability and art-budget backbone (Pillar 1; modular pipeline). Players restore and configure, not architect. Permanently out. |
| C7 | **PC port & controller support** | Revenue, wishlist momentum | Divided input design attention during the phase where touch-first must be proven. Deferred until after mobile content-complete. |
| C8 | **Localization beyond English** | Reach | Text volume is still moving; localize once event/text pipeline is stable. Deferred to production stage decision. |

## 3. Vertical slice — "The First Count" (locked definition)

**Fixed frame:** Days 1–7. Begins the morning after Signal 45 is first heard; ends on **Relay Night** with the Hold-or-Count commitment choice and a state-reactive epilogue card. Playable start to finish with blockout art, and must be *fun and legible* in that state (quality gate).

**Note A (adjustment):** "Twenty meaningful events" includes the scripted finale (Relay Night) as event #20 — documented so later prompts don't add a 21st silently.
**Note B (adjustment):** "One ending" is implemented as one ending *frame* (Hold the Cross / Begin the Count epilogue card) with state-reactive text variants — the variants share one structure and one presentation, so this remains a single ending for scope purposes.

### 3.1 Slice content enumerations (canon)

**Survivors (4):**
| Name | Aptitude | Sketch | Slice function |
|---|---|---|---|
| Imka Vasser | Fitter | Ex-line engineer, 50s; value: *the station outlives us all* | Utility/repair backbone; conflict pole A |
| Ash Okonkwo | Medic | Former street-clinic nurse; value: *no one turned away* | Triage; carries the clinic decision's Mark |
| Teo Brandt | Runner | Restless courier, 20s; brother missing since the Char | Nightruns; conflict pole B (radio-time petition) |
| Maren Hale | Steward | Ran the station kiosk before; keeps the ledger | Accord anchor; canteen scenes; trade handling |

**Rooms (8):** Flywheel Room (charge) · Cistern (water) · Canteen (rations, Accord scenes) · Sleeper Car (rest — a stranded railcar) · Aid Car (medical — second railcar) · Fitters' Shop (crafting) · Listening Post (radio) · Scrubber Gate (air, decon, expedition door).

**Resources (5):** Water · Rations · Charge · Salvage · Meds. (HUD shows exactly these five + day/phase clock — within the 6-indicator gate.)

**Needs (4):** Hunger · Fatigue · Condition · Strain.

**Craftables (12):** mask filter cartridge · cool-vest · patch kit · purifier cartridge · trail rations · battery cell · storm lantern · pry bar · splint & dressing kit · ember tea (Strain relief) · spare-parts bundle · antenna wire spool.

**Nightrun locations (3):**
1. **Fenwick Parade Arcade** — flooded shopping arcade. Yields water/rations; hazards: deep water, unstable glass canopy. Low threat; teaches the run verbs.
2. **Depot 9 (Foundry Line)** — rail maintenance depot. Yields salvage/parts (incl. antenna wire); hazards: collapse, a feral dog pack (avoid/deter — no combat). Site of the scripted scavenging mission.
3. **Marrow Street Clinic** — meds; occupied by squatters (Tidemill kin). The slice's moral encounter and delayed-consequence flagship.

**Trader (1):** Linewalker Sable — walks the tunnels between holdouts; manifest and prices react to monitored beacon intel.
**Faction (1):** The Tidemill — harbor commune around a tidal generator; appears via envoy visit and the clinic consequence chain.
**Relationship conflict (1):** Teo vs. Imka over radio slots (personal signal vs. storm forecasting), escalating over Days 2–6 with an arbitration decision.
**Environmental/structural crisis (1):** Day 4–5 cinderfall storm + Scrubber Gate intake failure cascade (the Pillar 1 worked example).
**Active scavenging mission (1):** Depot 9 antenna-wire recovery — required for full Relay Night reception quality; teaches risk-pricing and carry commitment.

### 3.2 The twenty events (categorized; ≥5 delayed-consequence chains marked ⛓)

| # | Event | Category | Chain |
|---|---|---|---|
| 1 | Flywheel bearing whine (2-day power-failure telegraph) | Utility | ⛓ → 3 |
| 2 | Intake clog during storm (the crisis cascade) | Utility/structural | |
| 3 | Brownout night (if #1 unaddressed) | Utility | ⛓ from 1 |
| 4 | Cistern contamination scare (boil order decision) | Utility | |
| 5 | Teo's radio-time petition | Human | ⛓ → 16 |
| 6 | Ration skim discovery (arbitration: accuse, watch, or let lie) | Human | |
| 7 | Ash's nightmares (Mark aftermath of clinic choice) | Human | ⛓ from 13 |
| 8 | Imka's overwork collapse telegraph (fatigue warning → collapse if ignored) | Human | ⛓ |
| 9 | First gate arrival: two strangers from the distress call you did/didn't monitor | Visitor | ⛓ from radio choice |
| 10 | Sable's first arrival (trade tutorial) | Visitor/trade | |
| 11 | Sable's manifest shift (reacts to beacon intel; scam-filter check if unmonitored) | Visitor/trade | |
| 12 | Tidemill envoy visit (introduction + a request) | Faction | ⛓ → 13 |
| 13 | Clinic bill: squatters at the gate (consequence of Marrow Street choice) | Faction | ⛓ from run |
| 14 | Counterfeit filter cartridges in a trade lot | Trade | |
| 15 | Magpie's broadcast (doubt event; verification fork) | Radio | |
| 16 | Missing-persons band hit (Teo thread payoff — ambiguous) | Radio | ⛓ from 5 |
| 17 | Signal 45 carrier anomaly (verification clue) | Radio | |
| 18 | Storm-band forecast event (the telegraph for #2) | Radio | |
| 19 | Depot 9 aftermath: injury triage / dog-bitten runner | Expedition | |
| 20 | **Relay Night** (finale: reception quality + verified facts + Accord shape the choice scene) | Finale | closes 5, 15, 17 |

### 3.3 Vertical-slice feature table

*(Every slice feature: player value · dependencies · difficulty · content requirement · acceptance condition. Acceptance conditions are restated measurably in 07.)*

| Feature | Player value | Dependencies | Diff. | Content requirement | Acceptance condition |
|---|---|---|---|---|---|
| Four-phase day loop & time model | The rhythm; safe stops; no offline anxiety | Save system | M | Phase transition presentation ×4 | A full day playable in ≤12 min; autosave at each boundary; kill-app-anywhere resumes correctly |
| Station cutaway view & navigation | Pillar 1 readability | Camera/zoom framework | M | 3-level blockout, 8 rooms | All 8 rooms + all utility states readable at overview zoom on a 6.1" phone |
| Utility network (abstract) | Cascade drama, forecasting | Cutaway view | L | 5 subsystem states ×3 damage stages | Scripted Day-4 cascade passes through visible intermediate states; player can avert it 3 ways |
| Resource production/consumption | Scarcity that forces prioritization | Utilities, assignments | M | 5 resources, per-room rates | Stockpile trajectories visible; a deliberate 2-day water deficit is survivable via 2+ distinct plans |
| Survivor sim (needs ×4, aptitudes ×4) | Pillar 2 | — | L | 4 survivors, animation set, ledger pages | Swapping any two survivors' assignments produces measurably different outcomes and at least one different bark/event |
| Assignment & work orders | The core verb | Survivor sim, rooms | M | Order UI, acknowledgment barks | Any order issued in ≤3 taps from overview; refusal states function |
| Strain & Marks | Human ledger memory | Survivor sim | M | Mark definitions ×6 min. | Ash's clinic Mark and Teo's refusal Mark both alter later behavior observably |
| Accord (community meter) | Two-ledger stakes | Strain/Marks, events | M | Threshold scenes ×2 (warm/fractured) | Accord passes a threshold in normal play at least once; the withheld/granted canteen scene triggers correctly |
| Crafting (12 items, queue) | Preparation agency | Resources, Fitters' Shop | M | 12 recipes, icons | Craft-to-use chain (wire → antenna repair → reception) completable by Day 6 |
| Listening Post (slots, 6 categories, expiry) | **Signature hook** | Charge, events | L | ~14 authored signals across 7 days | Every night ≥1 more worthwhile signal than slots; ≥2 ignored signals visibly resolve off-screen later |
| Signal 45 verification track (slice-length) | Hook payoff; ending texture | Listening Post | M | 3 verification stages of content | Relay Night scene text provably differs across 0/1/2+ verified facts |
| Nightrun planning & provisioning | Pillar 4 ritual | Crafting, survivors | M | Planning UI, risk preview | Preparation measurably changes both active difficulty and delegated outcomes |
| Active nightrun (3 locations) | Optional intensity | Planning; location art | L | 3 authored locations, run verb set | Each location completable in 3–6 min; interruption-safe; no reflex-mandatory segment |
| Delegated nightrun resolution | Accessibility; session flexibility | Planning | M | Outcome-report templates | Delegating every run still yields a completable, coherent 7 days |
| Return & triage | Consequence ritual | Aid Car, needs | S | Triage scene staging | Injuries from run choices arrive, are treatable, and cost Meds/time believably |
| Trader (Sable) | Economy relief valve | Intel, resources | M | Manifest tables ×3 states | Manifest provably differs with/without beacon monitoring; counterfeit event functions |
| Faction (Tidemill) & gate visitors | Outside pressure | Events, Accord | M | Envoy + clinic-bill scenes | The clinic decision changes the Day-6 gate scene in all three choice branches |
| Event system (20 events, 2-crisis cap, telegraphs) | The week's drama | Most systems | L | 20 authored events | All 20 firable; cap never exceeded; every crisis shows its telegraph first |
| Relationship conflict (Teo/Imka) | Pillar 2 proof | Events, radio | M | 5-beat arc content | Arc reaches distinct outcomes from ≥3 different player approaches |
| 7-day mini-campaign & epilogue | Complete arc; slice proof | Everything | M | Epilogue card, variant text | New player reaches Relay Night in 60–100 min total; epilogue reflects ≥4 tracked state facts |
| Save/reload | Trust | All state | M | — | Save-kill-restore at 20 random points produces no observable divergence |
| Mobile controls & HUD | Playability | — | M | Touch layout, 5-resource HUD | All interactions one-handed-capable except pinch zoom; touch targets ≥ platform minimums |
| Sound & feedback baseline | Legibility, tone | — | M | ~20 SFX, 2 music states, alarm timbres | Each utility alarm identifiable by ear alone in a blind test; captions for all audio signals |
| Performance baseline | Mobile feasibility | Art blockout | M | — | 30 fps minimum on a 2022 mid-tier device; cold load ≤ 20 s; session battery draw within norms (target set in 07) |

## 4. Full base game (delta from slice — summary)

Act structure ×3 (35–50 days); survivors to 8–12 with arrival arcs; rooms to ~16 via restoration ladder; craftables to ~30–40; locations to 18–24 across three tunnel branches; factions to 3 (Tidemill, the Junction voice's crews, the Linewalkers as a network); events to 120–180 with act-gated pools; the five ending frames + two failure states; antenna/capacity ladder; storm seasons; commitment gates; cloud save; notification opt-in; full audio identity; store with single unlock at the Chapter One boundary (Day 7 — the slice *is* the free chapter's shape, by design).

## 5. Post-launch possibilities (unpromised)

Second-station scenario; storyteller/pacing variants; NG+ modifiers; PC/controller port (C7 graduates here); localization waves (C8); frequency-archive lore collection; OST and Higgsfield-pipeline marketing cinematics; accessibility extensions (full audio description).

## 6. Permanently cut (identity-level)

Everything in the monetization restrictions; combat systems (C5); free-form building (C6); physical utility routing (C3); population-scale simulation; offline simulation/yield; multiplayer; procedural core cast; portrait mode.
