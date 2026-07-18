# 11 — CORE LOOP AND TIME SYSTEM

**Stage:** Prompt 2 — playable rhythm lock.
**Status:** LOCKED at structural level; numeric values are tuning baselines validated by the feasibility model (15, `tools/simulate_vertical_slice.py`), not final balance.
**Reading order:** this document owns the loop hierarchy, time rules, resource cadence, the work-order model, and resident behavior. 12 owns the phase-by-phase and session flow. 13 owns the first session. 14/15 own the seven-day plan and its evidence. **Prompt-3 layer (D-043):** stock specifications in 16, needs/medical in 17, utilities/forecasts in 18, weather/incidents/HIGHBALL in 19, survival-model evidence in 20 — §4 below uses the canon names.

---

## 1. What the player actually does (the identity check)

Signal 45 is a **base-building and community-management game first**. A normal stretch of play is: read the station's condition → identify the most important shortage, opportunity, or danger → assign people and resources → repair, construct, upgrade, or reclaim part of the station → watch residents visibly do the work → handle complications → prepare for night → choose what to listen for → send or guide the nightrun → take the consequences at dawn → begin the next day in a station that has *visibly changed*. The regular feeling is **"I made this station work better."** The recurring, quieter feeling is **"I improved the station — and the way I did it changed the people living here."** The Listening Post, expeditions, and relationships sharpen this loop; they never replace it.

## 2. Loop hierarchy (five scales)

### 2.1 The 20–40 second loop (atomic)

**Notice → Inspect → Decide → Act → Confirm → Watch.**

1. **Notice** — one signal: a gauge trend, a chalk-plate badge, a resident's posture, a completed works stage, a visitor silhouette.
2. **Inspect** — one tap opens the one relevant panel (room, ledger page, node, work order). The panel states cause, trajectory, and stakes in one screen. *Never a chain of unrelated menus.*
3. **Decide** — one understandable decision, 2–4 options, physical cost quoted.
4. **Act** — assign, reprioritize, place, queue, or respond; one confirming tap.
5. **Confirm** — immediate audiovisual acknowledgment (bark, chalk tick, gauge nudge).
6. **Watch** — the assigned resident walks over and begins; the world shows the decision taking hold.

Budget: 8–14 of these per day (D-027), supplied by events (~3/day), the radio schedule, run planning and gate calls, triage, and the three standing generators (load-priority board, over-subscribed orders, the construction queue).

### 2.2 The 2–5 minute loop (safe segment)

One complete *unit of intent*, always ending at a durable state: finish a small repair · set up a work team on a project · place and activate a small facility · resolve one visitor · review the signal board · prep a nightrun · triage a return · handle one incident. Every confirmed decision persists instantly; a safe-stop marker follows each unit. **Safe stopping opportunities therefore occur every 2–5 minutes**, not only at phase edges.

### 2.3 The 5–12 minute session loop

Reviewed in one sentence: *arrive, fix or build one real thing, leave at an exhale.* A session covers one to two phases: re-orient (≤60 s, stationmaster's log) → work the phase's decision set → close at an autosaved stop with the next phase's headline previewed. A session **does not need to complete a full day**; stopping mid-day costs nothing. Typical accomplishments per session: one shortage addressed, one construction started or finished, one human matter handled.

### 2.4 The in-game day loop

Four phases (plain labels + canon names, D-040): **DAY SHIFT — Swelter → EVENING WINDOW — Slack → NIGHT OPERATION — Nightrun → RETURN & REPORT — Graymorn.** Full definitions in 12. Model-validated durations: delegated day **8–12 min** (model: 10.6–11.6), active-run day **11–16 min** (model: 14.9), Day 1 ≈ 11 min at guided pace, the relay finale ≈ 13 min.

### 2.5 The campaign loop

Days accumulate into: a physically larger station (sections reclaimed, stages climbing Refuge → Home), more named residents (berths gate arrivals), stronger utilities (trunks, capacity, the antenna ladder), better information (verification, contacts, transmission), deeper or damaged relationships (bonds, grudges, Marks, Accord), faction posture, and rising confidence or doubt about Signal 45 — converging on the commitment gates and the five ending frames (02 §5–7). Storm cycles and Relay Nights remain the campaign's metronome.

## 3. Simulation philosophy and time rules (LOCKED)

One clock, one rule: **simulated time advances only while the app is active and the simulation is running.** Specifically:

- Phases advance on player confirmation; within a phase, ambient simulation runs gently and can always be paused.
- Opening any major decision panel (event card, gate call, survey report, radio scheduler, trade screen) **auto-pauses** the simulation. Room/ledger inspection panels slow simulation to 25% rather than hard-pausing (the world stays alive behind quick glances); a visible pause chip always shows the current state and *why* ("Paused — decision open").
- **Closing or backgrounding the app saves and pauses immediately.** No food, water, medicine, health, or construction time is consumed while away. Returning after an hour or a month resumes the identical state. No catch-up, no punishment, no offline yield (Anti-pillar 1).
- Construction, crafting, and treatment progress **only through resident work** in simulated time. Recovery happens only during simulated rest. Nothing progresses by wall-clock absence.
- Expedition results are never computed in the background: a delegated run resolves when the player confirms advance; an interrupted active run resumes or converts from the last completed node (D-024) — already-committed node outcomes are serialized before display, so reloading can neither lose nor duplicate them.
- The player can always inspect why time is advancing or paused (the pause chip expands to a one-line explanation).

### 3.1 Simulation speeds (evaluated; D-040)

| Speed | Rate | Use |
|---|---|---|
| **Paused** | 0× | Decisions, inspection, planning; unlimited |
| **Normal** | 1× | Default; residents visibly work |
| **Fast** | 3× | Letting queued work run when no decision is pending |

**No "very fast" tier in the slice.** Two active speeds cover the need; a 10× tier would blur the visible-work identity (Pillar 6) and invite skipping telegraphs. Revisit only with playtest evidence of dead waiting. Fast drops to Normal **once per warning onset** (not continuously while a warning persists — Fast stays usable during a long grind with a standing warning).

**Sim rate and end-shift semantics (D-042):** at Normal, **1 real second ≈ 1 simulated minute** (a 4–7-minute Swelter ≈ 4–7 simulated hours of station activity; Fast = 3×). **Ending a shift resolves remaining queued work at accelerated resolution** — banner/modal interrupts still fire, and the shift report itemizes what completed — so the WU economy never depends on real-time watching, an impatient player never silently under-produces, and the no-detached-timer contract holds (the work is still resident-performed and visible while it runs). The safe-stop rhythm is measurable: 07 §1 gains a max-interval criterion (≤5 min between consecutive safe-stop markers in a recorded playthrough).

### 3.2 Interruption tiers (what pauses, what waits)

| Tier | Behavior | Examples |
|---|---|---|
| **Auto-pause** (modal card) | Simulation stops; card must be answered or explicitly deferred | A resident may die; utility network enters imminent-failure; major structural incident begins; irreversible visitor/faction decision; expedition gate call; information about to be lost (signal expiring tonight unheard) |
| **Banner** (continue) | Colored strip + audio cue; play continues; tap to open | Warning-state onset (browning lamps), work paused for missing supplies, resident refusal, Fast→Normal drops |
| **Queue** (badge) | Joins the ≤3-badge queue for the player's convenience | Completions, arrivals at the gate not demanding immediate answer, minor need thresholds |
| **Phase report** | Held for the next report (Graymorn log or phase close) | Routine production tallies, minor mood shifts, background flavor |

Routine completions never modal-interrupt. **If an auto-pause-tier event fires while the build lens is open, the simulation pauses immediately even though the card queues** (pause chip: "Paused — urgent card waiting"); the card presents on lens exit. Banner/queue-tier events queue without pausing.

**Attention caps (D-042 — new caps, now with an owner):** ≤2 active crises (the pre-existing D-019 scheduler cap) · **≤1 major crisis demanding immediate modal attention** · **≤3 urgent (banner-tier) decisions live** — these two are introduced here as scheduler rules, tested alongside the 2-crisis cap in 07 §13's rig. Mapping to 09 A.9's badge budget: urgent banners and queued badges are distinct surfaces; worst-case legal attention load is 1 modal + 3 banners + 3 queued badges, and the modal always fronts alone.

## 4. Resource cadence (LOCKED structure)

Three categories, three change-rhythms — no hidden formulas:

### 4.1 Stock resources (the 5-item HUD: Food · Clean Water · Medicine · Materials · Charge*)
*Canon plain names per 16 §1 (D-043); residents say "rations," "meds," "salvage" as fiction flavor — the HUD does not. Charge is a stored buffer (flywheel + cells) fed and drained by the flow layer — it is the one stock with continuous flow coupling, and it fills the classic "Fuel" role (16 §1).*

| Stock | Consumed | Produced |
|---|---|---|
| Food | At the two visible meal moments (morning, evening) | Cooking work; nightruns; trade |
| Clean Water | At meals + a daily works draw (visible line items) | Water duty (tank) or Cistern Works cycle |
| Medicine | When a treatment begins (committed at triage) | Nightruns, trade, later production |
| Materials | **Reserved when a project is confirmed, consumed in visible stages** | Clearing/draining yields, nightruns, trade |
| Charge | Continuous drain by powered loads (visible on the board) | Flywheel duty cycles, flywheel cells |

**HUD forecast contract (each stock, one tap):** *steady stocks* (Clean Water, Food, Charge): current amount · net trend arrow · "≈ N days to shortage at current use" · top consumer · top idle/underperforming producer. *Lumpy stocks* (Medicine, Materials — consumed in commitments, not rates): **free vs. reserved** shown on the HUD chip itself ("8 (2 free)"), the list of known upcoming draws (booked treatments, confirmed project stages, queued crafts), and the earliest committed draw that would fail. Shortage diagnosis is a read, never a hunt — including "can I afford to start this project right now?" (07 §3 tests it). Full stock specifications, shortage stages, and emergency substitutions: **16**.

### 4.2 Flow / capacity systems (never collectible currencies)
**Power, Air, Water-network, Structure** — the four slice families (D-043, 18) — = **production vs. demand vs. capacity vs. priority** on the trunk/node network (10 §8); heat is a load/modifier and sanitation derives from water + cleaning + crowding (16 §1). They update continuously while simulation runs, hold state while paused, and telegraph before failing (Pillar 1) using the five forecast confidence classes (18 §8). The load-priority board (≤8 load-class rows) is the standing control; per-room shutoffs live on room panels.

### 4.3 Human conditions
*(Canon need names per 17 §1, D-043: Health · Hunger · Fatigue · Stress. "Condition" and "Strain" in earlier text refer to Health and Stress.)*

| Condition | Changes |
|---|---|
| Hunger | At meal moments (steps, not per-second decay) |
| Fatigue | Accrues through work blocks; recovers only in simulated rest |
| Health | At events, treatment starts/completions, and rest cycles |
| Stress | At events, refusals, scene beats, and nightly rest quality; vents visibly first |
| Trust/Accord | At witnessed decisions and scene beats — never silent background drift |

## 5. The shared work-order model (one system for all labor)

Construction, clearing, draining, reinforcement, repair, crafting (fabrication), treatment, cleaning, hauling, production, and utility restoration are all **works orders** in one queue with one schema:

`id · type · location · required/reserved materials · required tools · required skills · min/max useful workers · work units · progress · priority · hazards · utility requirements · access requirements · interruptibility · completion effects · cancellation effects · refund behavior`

**Task classes (D-040 — not everything is a ceremony):**

| Class | Examples | Cost | Ceremony |
|---|---|---|---|
| **Placement** | Move bedrolls, set a sign, choose a berth spot | 0 WU | Instant, free, undoable |
| **Short install** | Berth prep, a bench, the staging repurpose | ≤3 WU | One worker, minutes, no concurrency slot |
| **Project** | Room conversion, trunk extension, seal install | 4–8 WU | Staged, 1–2 workers, visible stages |
| **Major reclamation** | Clear the east rubble, drain the west gallery | 12+ WU | Multi-day, staged spectacle, yields salvage |

**Visible-work contract:** materials are carried to site; workers start, and the environment shows stages (rubble shrinks, framing rises, waterline falls); work pauses visibly for fatigue, hazard, missing supplies, or utility loss with a banner naming the reason; a second qualified worker accelerates projects up to the max-useful cap; completion changes the room physically and functionally. **"Press build and wait" cannot occur** — there is no detached timer anywhere in the model.

**Construction detail (D-046):** the room-creation flow, blueprint lifecycle, and visible stage grammar are specified in 23 and executable in `tools/spatial_model.py` — blueprints reserve nothing until activation, matching the policy below.

**Cancellation and reservation policy (D-042):** materials consumed at completed stages are non-refundable; the unconsumed reserve refunds 100%; cancellation's price is the sunk labor plus a visible-disruption echo (mirroring the two-sided repurpose rule). Events and bills draw on total holdings, taking reserved stock **last** and pausing the affected order with a named banner — reservation is never a shield, and scarcity telemetry counts reserved stock as held. Cancel/reissue churn yields zero net gain (07 §9 tests it).

**Task class is authored, not computed:** an order's class (placement / short install / project / major reclamation) is set per order type at definition time, never derived from remaining WU at runtime; player-scoped sub-orders inherit the parent's class, and no player action can decompose a project into short installs (anti-cheese, 15 §1).

**Work units:** 1 WU ≈ 45 simulated minutes of focused work — **design vocabulary only; never shown on screen** (players see plain effort language: "about half a shift"). A resident's day yields ~7.5 WU gross **at matched aptitude** — the aptitude modifier band (matched 1.0× / secondary ~0.8× / off-aptitude ~0.6–0.7×, per D-031 and 07 §5) is a systems-stage layer the feasibility model declares as a limitation. The model applies an 0.85 efficiency factor (travel, switching). Full arithmetic and validation: 15.

## 6. Resident time, priorities, and refusal

**A resident's day:** wake → morning meal → Swelter work blocks (the main labor supply) → evening meal → night (sleep, or run, or quiet-shift watch) → rest recovery. Treatment, personal needs, and scenes claim blocks visibly.

**Priorities:** five tiers — **Emergency · High · Normal · Low · Suspended** — set per works order (and per load-class on the power board), not per footstep. Standing orders absorb anything done three times (Anti-pillar 4). **Essential duties have a floor (D-042):** cooking, water duty, and cleaning can be *reduced* (rationing — a real emergency lever with its own costs) but **suspending one starts a telegraphed consequence chain** on the six-step ladder (cleanliness → accident-odds multiplier on works, infection risk at treatment starts, Strain drift) whose price exceeds the labor saved — modeled and verified net-negative in 15 §3's neglect run.

**Task selection:** residents pick their next task by role fit → skill → distance → urgency → risk → fatigue → traits → existing reservation → player priority. **Commitment rule (anti-thrash):** a resident finishing a task's current stage will not abandon it for a merely higher-scored task; tasks ≥70% complete are abandoned only for Emergency-tier interrupts. Reservations persist across interruptions.

**Refusal** stays meaningful and *rare*: it triggers only on value-line crossings, active trauma (Marks), relationship conflicts, genuine danger, or exhaustion — never as random flavor. A refusal always self-explains in one screen ("Ash won't turn Juna away — 'no one gets turned away, not by me'") and always offers the player a real response (reassign, insist at Accord cost where permitted, or resolve the cause). Emergency behavior overrides normal priorities (fire, flood, collapse: residents drop work, help, and regroup at the muster point).

## 7. The Listening Post loop (support role, restated)

The signal-board loop stands as specified (01 Pillar 3, 03 §3.1a): signals appear from prior choices, weather, factions, exploration, and seeded events; each shows category, source, confidence, age, stake, expiry, and commitment; the player fills **2 slots** during Slack; processing happens across the night; results land at Graymorn or days later; the unheard persists, degrades, expires, resolves without you, or returns changed — and consequences are always embodied (weather prep, expansion intel, traders, rescues, faction behavior, run safety, missing people, structural risks, the truth of Signal 45, endings). **Day 1 presents a curated three-signal board** (13); complexity grows with the week. The radio is one Slack decision among the shelter's many — it whets the loop; it does not replace it.

## 8. Nightrun integration (support role, restated)

The runner's absence is real: no construction, repair, guarding, treatment, production, scenes, or emergency response from them that night, and a −3 WU morning-after cost (model-validated). Equipment taken is unavailable inside. Everything comes home: injuries, fatigue, intel, rescued people, goods, promises, faction consequences. Active mode is "on the wire" decision-making (route, timing, continue/withdraw, tools, noise, contact, enter/bypass, help/ignore, reveal/conceal, carry risk, radio contact, abandon objective) — never steered movement. **Node-quantized run accounting (D-042):** the air/heat clock and consumables checkpoint at each node entry; interruption rewinds to the checkpoint exactly (being interrupted is free), and node re-entry is deterministic under a persisted seed (same hazards, same offers, same outcomes for the same calls) — kill-and-retry yields nothing. Delegated mode resolves the same node graph with gate calls preserving every moral choice; it trades detail for speed and leans on preparation and trust — **it is not a punishment mode** (±10% equivalence band, 07 §10). Active runs occupy ≤ ~1/3 of a week's playtime by construction (model: three scripted runs = 13.5 of 90.1 minutes = **15%**).

## 9. Failure and recovery (process, never surprise)

Failure axes: physical collapse · community fracture · unsustainable population loss · essential-utility loss · legitimacy loss · no viable ending. Every axis walks the same six-step ladder: **Forecast → Warning → Visible deterioration → Emergency options → Serious consequence → Failure only if still unresolved.** Emergency options always include several of: rationing, shutting down rooms (load board), total labor reassignment (Emergency tier), running damaged equipment, burning stored materials, faction help at a price, abandoning a section (bulkheads), evacuating a room, repurposing, cancelling an expedition, accepting a social cost — the full fifteen-action vocabulary with per-action cost cards is 19 §4, and the one sanctioned overdrive is the **HIGHBALL ORDER** (one per day, priced in a named resident's fatigue + a promise-of-rest debt + labeled breakdown risk; never mandatory — 19 §5). One bad building decision can never end a campaign (10 §9's two-sided recovery guarantees); the model's mistake scenarios prove the slice absorbs a major error and still lands (15).

## 10. A complete player day (delegated, mid-slice, ~11 minutes)

*Day 5, east route.* **(0:00)** Open: Graymorn report from overnight — storm passed, seals held; the log ends on Ash sleeping badly (clinic Mark). Autosave chip visible. **(0:45)** DAY SHIFT: the cutaway shows the storm's bill — Scrubber Gate intake at jury-rigged, east wing lit but Canteen unfurnished. Load board: hotplate still off from storm rationing → one tap restores it (Rations trend updates). **(1:30)** Works queue: finish Canteen furnishing (Imka+Maren), start the freight-lift job with Depot 9 tools (Teo) — two decisions, costs quoted, workers walk. **(2:45)** Banner: Sable's return beacon was monitored — manifest preview arrives; queue it. **(3:15)** Event card (auto-pause): Teo asks again about the missing-persons band — grant tonight's slot, refuse, or promise Relay eve. Choose. **(4:30)** Watch/Fast: rubble baskets, canteen shutter rising; a chalk tick — Canteen DONE; the warm-beat scene plays (first shared table). Safe stop offered. **(6:00)** EVENING WINDOW: signal board — storm tail (expiring), Sable beacon, carrier anomaly, Teo's band; 2 slots. Provision tonight's arcade run (delegated), lantern + filters. **(8:00)** NIGHT OPERATION: confirm delegated run; one gate call arrives ("stall shutters ajar — pry or move on?") — answer; advance. **(9:00)** RETURN & REPORT: runner back — salvage +5, minor scrape; triage books 2 WU tomorrow; report shows the week's growth silhouette, Juna's berth ready, splice tomorrow. Autosave; stop. **(≈11:00)** Done — the station is visibly one room bigger, one promise deeper.
