# Signal 45 — Scope Matrix

## Scope rules

- **Difficulty:** S = small, M = moderate, L = large, XL = exceptional multidisciplinary risk for a solo developer.
- A feature is not “done” because it exists in prose. Acceptance conditions require a prototype, build, content pass, or measured behavior as stated.
- The full-game ceiling of 20–24 room families is a guardrail, not a target. New families are admitted only when modules or specializations cannot express the required play.
- Normal full-campaign population is approximately 10–14. About 16 is a technical validation target; 20 is stretch only.
- Prompt 2 now authorizes only the deterministic feasibility tooling and documents recorded in this repository. It does not authorize full game implementation, final production assets, detailed resident AI, complete crafting balance, or store packaging.

## 1. Vertical slice — The First Count

| Feature | Dependency | Difficulty | Acceptance condition |
|---|---|---:|---|
| One authored station slice: central platform, East and West first wings, blocked vertical route | Modular shell; camera; save IDs | L | Overview shows all routes and 4 starting/8–10 ending functional areas; East or West can be chosen without hidden invalidation. |
| Side-on shelter overview with Room Focus | 3D room kit; selection; occlusion rules | L | Phone prototype supports tap, smooth focus, pinch zoom, slight pan, quick return, and reduced-motion transition without changing simulation state. |
| Seven room families: Rest, Medical, Food, Storage, Utility, Workshop, Operations | Room data model; equipment/modules | L | Temporary/permanent forms reuse family logic; at least one upgrade and one repurpose are playable. |
| Reclaim / Connect / Build / Operate / Adapt workflows | Context actions; placement; undo | L | No selection shows irrelevant verbs; a player can open and fit a bay without pixel-perfect taps. |
| Five stock resources and detailed component blockers | Inventory; forecasts | M | HUD shows only Food, Clean Water, Medicine, Materials, Charge; blocked projects name the missing component family. |
| Four utilities: Power, Air, Water, Structure | Network model; overlay; incidents | XL | Each overlay shows source/path/load/headroom/condition/priority/failure in plain language; one cascade is recoverable. |
| Four primary resident conditions | Resident state; task effects; treatment | L | Only Health, Hunger, Fatigue, Stress are permanent meters; respiratory exposure, injury, and waterborne illness are contextual. |
| Four starting residents plus Juna Malek admission candidate | Authored character data; portrait/rig | L | Skills, limits, preferences, relationships, promises, refusal reasons, and recovery behavior affect at least one slice decision each without rarity or overall levels. |
| Task assignment and visible work | Navigation lanes; animation set | L | Residents travel to and visibly perform representative rest, repair, carry, build, listen, treat, and operate tasks. |
| Forecasts and causal failure recap | Deterministic state changes; UI | L | Food/water/utility risks expose cause, time, intervention, and post-incident chain. |
| One Highball opportunity | Task/work model; promises; utilities | M | Known benefit/cost and labeled uncertain risk appear before commitment; using it is optional and creates a persistent human or utility consequence. |
| Listening Post with competing signals | Signal cards; time commitment; campaign flags | L | Following one signal changes storm, trader, expedition, route, or evidence state; ignoring another has an understandable opportunity cost. |
| One shared active/delegated nightrun graph | Node graph; loadout; resolution; scene | XL | Same route, time, noise, protection, carry, hazards, retreat, and persistent location state resolve consistently in either mode. |
| Trader, outside group, and Juna decision | Visitor framework; inventory; capacity | L | Admission is constrained by real capacity/air/relationship facts and has more than binary “good/evil” framing. |
| Seven-day authored event spine | All slice systems; narrative tools | XL | Day 1–7 can complete from both routes, includes storm, bounded cascade, preventable injury or Teo's no-new-injury treatment path, conflict, delayed consequence, recovery, and ending evaluation. |
| Offline pause, save, reload, and safe stopping | Serialization; app lifecycle; deterministic stream | XL | Automated and manual interruption tests reproduce exact state; no dangerous simulation advances while closed. |
| Mobile/accessibility baseline | UI framework; settings | L | Adjustable text, symbols+color, contrast, reduced motion/shake, subtitles/speaker labels, sound direction, haptics, speed/pause, tap alternatives, extended decisions, enhanced forecasts, confirmations. |
| Placeholder audio and cohesive prototype art | Asset registry; mixer | M | Functional cues communicate selections, warnings, direction, machinery, and state; placeholders are explicitly marked and provenance tracked. |

## 2. Full base game

| Feature | Dependency | Difficulty | Acceptance condition |
|---|---|---:|---|
| 45-day three-act campaign with authored Signal 45 scenario packages | Valid slice loop; narrative/state tools | XL | Every day contributes a meaningful decision or recovery beat; multiple ending plans are prepared physically before Day 45. |
| One excellent full interchange with larger wings and vertical areas | Slice shell pipeline; performance budgets | XL | Expansion remains readable on target phones; each major section supports more than one viable use. |
| Approximately 12–18 likely room families; hard ceiling 20–24 | Proven seven-family architecture | XL | Each additional family passes the unique-system test and has temporary/permanent/module paths where appropriate. |
| Normal population 10–14; validated target about 16 | Resident LOD; navigation; UI; save | XL | Target-device stress test holds performance and resident comprehension; no design requires 20. |
| Deeper named-resident arcs and relationship network | Authored tools; bounded memory rules | XL | Specific memories affect play without combinatorial dialogue explosion or runtime generation. |
| Trade and several factions | Visitors; signals; promises; endings | L | Factions offer conflicting practical relationships and infrastructure consequences, not a single reputation ladder. |
| Equipment, item crafting, repair, and protective loadouts | Workshop family; inventory; expedition | XL | Recipes are bounded, readable, and tied to station/expedition needs; no combat-loot treadmill. |
| Several compact nightrun locations | Proven shared graph and content budget | XL | Each location changes persistently, supports active/delegated resolution, and serves a shelter objective. |
| Security, intrusion, sabotage, and nonlethal response | Layout; incidents; relationship/faction state | XL | Preparation and negotiation dominate; harm is brief, legible, and consequential. |
| Weather/heat/cinder incident variety | Forecast/cascade framework | L | Incidents remix known systems and recovery tools instead of introducing arbitrary exceptions. |
| Ending infrastructure and evaluator | Campaign evidence; station state | XL | Evacuate/remain/relay/costly-survival outcomes are earned through accumulated state, not one final dialogue selection. |
| Premium or seven-day-intro/full-unlock entitlement | Store/platform integration | M | No survival resource, energy, relief, revival, resident, ad requirement, or speedup is monetized. |
| Localization-ready text and UI | String pipeline; font/layout testing | L | Pseudolocalization and representative longer-language tests pass before content lock. |
| Production audio, music, and limited voiced efforts/reactions | Audio budget; localization policy | L | Key systems are legible without sound; audio supports atmosphere and direction without committing to full voice acting. |

## 3. Post-launch possibility

| Feature | Dependency | Difficulty | Acceptance condition before approval |
|---|---|---:|---|
| PC adaptation | Stable mobile release; input/UI abstraction | L | Demand and support budget justify keyboard/mouse, aspect ratio, save, and storefront work. |
| Additional authored station map | One complete excellent campaign/map; modular tools | XL | New shell creates genuinely different railway mechanics and can reuse most systems/content pipelines. |
| Endless or challenge mode | Campaign balance and retention evidence | XL | Mode has a distinct goal and does not dilute authored Day 45 resolution. |
| Additional Signal 45 scenario package | Evidence/ending authoring tools | L | Variant remains internally coherent and preparations are never rendered meaningless by a hidden swap. |
| Additional compact nightrun sites | Proven expedition usage and completion data | L | Each adds shelter decisions rather than combat or content filler. |
| Pets | Resident/animation/performance headroom | XL | A defined care, recovery, or station role justifies AI, animation, narrative, and accessibility cost. |
| Optional curated voice expansion | Successful localization/audio production | XL | Coverage can remain consistent across supported languages and does not delay systemic polish. |
| Community scenario tools | Stable data schemas and support capacity | XL | Security, moderation, platform policy, save compatibility, and documentation are funded. |

Post-launch possibility is not a promise or roadmap commitment.

## 4. Cut or deferred

| Feature | Status | Why |
|---|---|---|
| Multiplayer | Deferred indefinitely | Networking, synchronization, social safety, pause rules, and ownership conflict with the authored offline campaign. |
| PvP | Cut | Contradicts community survival and no-combat-power-fantasy boundary. |
| Online raids | Cut | Encourages combat/loot progression, always-online pressure, and hostile offline consequences. |
| Runtime-generated dialogue | Cut for base game | Consistency, safety, localization, performance, testing, narrative control, and cost are unacceptable; use authored conditional text. |
| Fully procedural stations | Cut | Weakens railway identity, authored composition, visual quality, layout meaning, narrative staging, and testability. |
| Direct shooter combat | Cut | Creates a second control/AI/animation game and makes violence the mastery path. |
| Children | Deferred beyond base game | Requires exceptional ethical, animation, narrative, rating, harm, and care treatment. |
| Pregnancy | Cut/deferred indefinitely | Not necessary to a 45-day campaign and introduces substantial ethical and simulation scope. |
| Generational simulation | Cut | Incompatible with campaign length and population scale. |
| Vehicles | Deferred | Adds traversal physics, art, animation, maps, and repair systems outside the slice proof. |
| Pets | Deferred unless post-launch gate passes | High emotional, AI, animation, performance, and content obligations. |
| Hundreds of residents | Cut | Destroys named-person focus, mobile readability, performance, and authored consequence. |
| Forty independent room systems | Cut | Unsustainable production, balance, art, UI, save, and learning burden. |
| Realistic fluid simulation | Cut | Mobile cost and engineering complexity exceed the value; use readable network/state abstraction. |
| Particle-level air simulation | Cut | Use room/branch capacity, condition, connection, and contamination states. |
| Freehand wall drawing | Cut | Touch precision, navigation, occlusion, art, and authored-shell conflicts. |
| Full voice acting | Deferred | Narrative volume and localization cost are disproportionate; prioritize text, efforts, barks, radio texture, and key moments. |
| Multiple station maps before one is excellent | Cut from base scope | One map must validate the complete physical and campaign fantasy first. |
| Endless mode before campaign validation | Cut from base scope | The Day 45 arc is the product promise; endless balance cannot lead production. |
| Free camera orbit | Cut | Breaks the sliced-map readability and multiplies art/occlusion requirements. |
| Combustion fuel as a primary stock | Cut | No systemic need; Charge and Power cover the intended energy decisions. |
| Paid supplies, energy, revivals, residents, speedups, mandatory ads, loot boxes | Prohibited | Violates the business and ethical contract. |

## Cross-tier dependencies and gates

1. **Prompt 3 survival-feasibility gate — passed provisionally:** 176 deterministic scenarios match expectation, 144 local tests pass, both routes complete Full Proof without Highball, explicit response cases work at a cost, and expected adverse cases remain. This is arithmetic/serialization evidence, not playable validation.
2. **Graybox gate:** side cutaway, Room Focus, bay placement, resident selection, and one utility overlay on a representative phone.
3. **System gate:** one complete forecast → cascade → intervention → recovery chain.
4. **Human gate:** one Highball promise and one Juna admission path persist across save/reload and change later willingness.
5. **Expedition gate:** one graph resolves actively and through delegation from the same state model.
6. **Content gate — deterministic portion passed:** East and West finish Day 7 at ten areas without Highball. Aggregate unused WU is reported separately from daily/phase slack; Day 5 has zero uncommitted WU and remains a spatial revalidation risk.

Prompt 3 adds no new production-scale feature tier. Medical, forecast, utility, incident, and emergency-action detail is bounded to reusable slice architecture. Conflict resolution, extra weather families, individual networks, and extra need bars remain deferred.
7. **Production gate:** measured art/animation/content time supports a credible schedule before Act II content expands.
8. **Full-game gate:** do not approve more maps, endless mode, or post-launch systems before one 45-day campaign is coherent and tested.
