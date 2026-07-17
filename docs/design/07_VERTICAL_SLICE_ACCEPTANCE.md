# 07 — VERTICAL-SLICE ACCEPTANCE CRITERIA

**Status:** LOCKED. The slice ("The First Count", Days 1–7) is accepted only when every criterion below passes — with one sanctioned exception: **if the R-01/R-06 descope ladder fires its first rung (delegated-only runs), the named reduced set "Delegated-Only Slice Acceptance" becomes authoritative** — it comprises every section below except §11 and the active-mode halves of §10 and §12, with §14's fully-delegated criteria promoted to primary. No other subsetting is legitimate. **§21 (base building) survives every descope rung** — the slice's construction proof is non-negotiable (D-038 completion gate); ladder rung 4 (one reclaim arc fully instead of both) adjusts §21's exclusive-choice test to a single-route verification, nothing else.
**Test device baseline:** one 2022 mid-tier Android (e.g. 4 GB RAM class) and one iPhone of similar vintage; 6.1" screen assumed for readability checks. "Blockout" throughout means the **readability blockout tier** defined in 03 §3.3 (proxy geometry + final lighting rig + ≤3 identifying props/signage per room + character color keys).
**Automation note:** every criterion marked "automated" maps to a rig in 03 §3.3's test-harness row; any rig not built for the slice downgrades its criterion to a written manual protocol, recorded here.

---

## 1. Complete day loop
- [ ] A new player completes Day 1 (all four phases) in ≤ 15 minutes without external instruction, guided only by the in-fiction onboarding content budgeted in 03 §3.3 (Day 1's authored decision budget: ~8 loops, delegation pre-selected). A returning player completes a typical delegated-run day in ≤ 12 minutes.
- [ ] All four phases (Swelter, Slack, Nightrun, Graymorn) are visited in order; each phase boundary shows the safe-stop marker and autosaves (verified by file timestamp/state hash).
- [ ] Time provably does not advance while the app is closed: state hash before backgrounding equals state hash on resume, after 1 minute and after 24 hours.

## 2. Shelter interaction
- [ ] From overview zoom, every functional area — in both the Day-1 state (4 areas) and a Day-7 state (8–10 areas) — can be identified by silhouette/lighting alone (5 of 5 first-time testers name each area's function correctly within 10 seconds of inspection), and every *blocked* section reads as blocked-and-different (rubble vs. flood vs. jammed lift distinguishable at a glance).
- [ ] Any room panel opens in 1 tap from overview; any work order issues in ≤ 3 taps total.
- [ ] Zoom levels (overview ↔ room) transition at ≥ 30 fps with no state desync.

## 3. Resource production and consumption
- [ ] All 5 resources (Water, Rations, Charge, Salvage, Meds) have visible per-day trajectory indicators; a tester asked "will water last through Day 3?" answers correctly from the UI alone in ≥ 4 of 5 trials.
- [ ] A scripted 2-day water deficit (Day 2–3 tuning) is survivable by at least 2 mechanically distinct plans (e.g. purifier cartridge craft vs. arcade nightrun vs. Sable trade), each verified in playthrough — and no single plan is chosen by more than 70% of the exit-test cohort.
- [ ] At least two further deficit windows on different resources (Meds after Depot 9; Charge before the storm) occur in a normal playthrough, each with 2+ distinct answers.
- [ ] Scarcity telemetry: across playtests, the player never simultaneously holds more than X days of buffer in all five resources after Day 1 (X set at systems stage); the R-11 safety valve fires at most once per playthrough and never erases an active deficit.
- [ ] Labor over-subscription holds: on every slice day, available work + fabrication orders exceed available person-phases by ≥ 25%, and the day report lists what was deferred.
- [ ] No resource can silently go negative; hitting zero always triggers its authored consequence event, never a stalled simulation.

## 4. Utility failure and recovery
- [ ] The Day 4–5 storm cascade fires through its visible intermediate states on either route — west: intake clog → scrubber draw → flywheel dip → Pump Room stall; east/pre-breakthrough: the same chain ending in the transfer-pump tank-feed stall (10 §15) — and the event log names each link causally.
- [ ] Load-priority board usability (mirroring §10b): all board rows and their states visible on one screen at 130% text scale; a full re-prioritization commits in ≤ 5 taps; each setting's downstream consequence readable without a secondary screen.
- [ ] All 3 authored responses (cut hotplate / throttle scrubbers / hot repair) complete the crisis with distinct, state-recorded outcomes; each response is optimal under at least one plausible Day-4 state documented in the tuning sheet, and no single response is chosen by more than 70% of testers.
- [ ] **Two-tier storm warning (D-022):** with the storm band unmonitored, the free diegetic telegraph fires ≥ 1 phase before landfall (enough to seal, not to pre-stage); with the band monitored, the forecast lands ≥ 2 days ahead. Both tiers verified in playthrough.
- [ ] The charge load-priority board is live every Swelter with visible downstream consequences per setting; changing a priority mid-crisis produces the documented cascade change.
- [ ] Every utility subsystem exhibits all 3 damage stages (failing / jury-rigged / restored) somewhere in a normal 7-day playthrough, each visually and audibly distinct.
- [ ] A player who ignores a telegraphed utility warning experiences the failure no sooner than the telegraph promised (no untelegraphed catastrophe — quality gate).

## 5. Survivor assignment
- [ ] Assigning a survivor against aptitude produces measurably different speed/quality/accident numbers than with-aptitude (tunable constants exist and are logged).
- [ ] **Strengthened swap test:** for every one of the 6 pairings, the automated sim log shows at least one difference in event availability, event branch, or refusal state traceable to a *non-aptitude* character property (value, Mark, bond, petition) by Day 3. Bark differences and speed/quality deltas explicitly do not satisfy this criterion.
- [ ] A competent 7-day playthrough contains ≥ 5 assignment decisions in which the aptitude-matched survivor is *not* the best available choice (verified by tuning logs — the overlapping secondary aptitudes and scheduled collisions in 03 §3.1 supply these).
- [ ] At least two distinct survivors' value-line refusals are reachable in normal play; each refusal explains itself in one screen.

## 6. Character condition
- [ ] All 4 needs (Hunger, Fatigue, Condition, Strain) change from play, are readable on the ledger page, and foreshadow via posture/idle animation — guaranteed at room zoom; at overview zoom, need-state badges on the room's chalk plate are the sanctioned channel, and an explicit overview-distance readability check runs at blockout.
- [ ] Strain's three named effects are each verified in logs: high-Strain vs. low-Strain assignment of the same survivor to the same job produces measurably different accident odds; delegated-run reliability drops above the Strain threshold; refusal likelihood rises when ordering against a value at high Strain.
- [ ] Imka's overwork telegraph (event 8) fires when — and only when — the triggering condition is met; ignoring it produces her collapse with the promised timing.
- [ ] Strain relief mechanics (rest, ember tea, canteen scene) each produce logged, distinct recovery amounts.

## 7. Relationship consequence
- [ ] The Teo/Imka radio-time conflict reaches at least 3 distinct outcomes from different player approaches (grant / refuse / broker compromise), verified by distinct Day-6 states.
- [ ] Refusing Teo creates the "Signal Refused" Mark; the Mark demonstrably alters his nightrun reliability and at least one later bark/scene.
- [ ] The Teo/Imka grudge (when created) measurably degrades their joint assignment on the Day 4–5 storm repair (the slice's systemic pair modifier), verified in logs.
- [ ] Ash's clinic Mark applies its triage speed/quality penalty while unaddressed and hardens her refusal on any turn-away order, verified in at least one branch.
- [ ] Maren's Accord-anchor mechanics function: canteen-scene recovery amounts halve when she is incapacitated or grudge-bearing; her "Cooked Ledger" Mark branch (event 6 suppression path) fires and stamps its Accord warning card.
- [ ] At least one Accord threshold crossing occurs in normal play, and the correct (warm/withheld) gathering-scene variant triggers in its route-appropriate venue — the Canteen (east) or the cook-ring "canteen corner" (west), same Maren Accord-anchor mechanics — while the unconditional hope-floor beats fire regardless of Accord (see §13).

## 8. Room construction or repair
- [ ] Both slice restoration projects — the **antenna wire splice** and the **Level-1 seal** (03 §3.1) — are completable, each requiring resources + assigned labor + elapsed phases.
- [ ] A completed restoration visibly changes the room (lighting/animation state) and its function (the splice measurably improves Relay Night reception quality — never slot count; the seal measurably reduces storm-night intake load).

## 9. Crafting
- [ ] All 12 recipes craftable as fabrication orders in the work-order system; the queue supports reorder and cancel with refund.
- [ ] The wire → splice → Relay-Night reception chain is completable by Day 6 and its absence measurably degrades Relay Night (verified in both branches) — and completing it demonstrably requires deferring or skipping at least one survival craft in the same window (verified in playthrough logs, both branches).
- [ ] Input scarcity binds: slice-total salvage income supports at most ~60–70% of the worthwhile craft catalog by Day 7 (telemetry-verified).
- [ ] Crafting consumes the stated inputs exactly; interrupted crafting (phase end, save/reload) never duplicates or destroys materials.

## 10. Expedition planning
- [ ] The planning screen shows runner, destination, load-out, risk preview, and return window in one screen; a plan commits in ≤ 6 taps from Slack start.
- [ ] Provisioning provably changes outcomes: the same Depot 9 run with/without mask filters + lantern differs in both active hazard handling and delegated result distribution (logged simulation test, n ≥ 100).
- [ ] **Mode equivalence (D-024):** for each of the 3 locations at 2+ preparation tiers, paired simulation (delegated resolver vs. scripted-bot "on the wire" play, n ≥ 100 each) shows expected material yields and injury rates within the declared ±10% band.

## 10b. Listening Post (signature-hook acceptance)
- [ ] Automated board check: every night, available signals ≥ slots + 1, matching the 03 §3.1a table; each offer has an authored consequence for both taking and forfeiting it.
- [ ] On ≥ 4 of 7 nights the top offers force a cross-category tradeoff (material vs. human/verification), verified against the board.
- [ ] Schedule diversity (D-002's revisit trigger, operationalized): across 5 testers' recorded 7-night schedules, no identical schedule appears 4+ times, and no signal category is chosen by zero testers.
- [ ] At least one verified fact produces a mechanical, non-textual effect before Relay Night (V2's Depot 9 intel or V3's Accord/price effect), observable in normal play.
- [ ] Usability: the radio scheduler presents all candidate signals and both slots on one screen at 130% text scale; a full schedule commits in ≤ 5 taps; each signal's category, expiry, and stake are readable without a secondary screen. (The scheduler is the named exception to 09 A.9's one-decision-at-a-time rule — it is a single allocation decision.)
- [ ] Exit interview: ≥ 4 of 5 testers can name one signal they regret not taking.

## 11. Active scavenging ("on the wire")
- [ ] All 3 locations completable in 3–6 minutes each; timer histogram from playtests confirms the band.
- [ ] The player's inputs are calls only (route, node verb, exit/carry commitment) — no steered movement exists; the full verb set (reach/pry/wade, aid, barter, take, leave, avoid, flee) is exercised across the 3 locations; no segment requires reaction time under 1.5 s to avoid loss (accessibility gate).
- [ ] All hazards run on the shared node system and both standoff encounters (dog pack nonverbal, squatters verbal) run on the one template — a code/data audit confirms no per-location bespoke mechanics.
- [ ] Backgrounding mid-run pauses; the player may resume or convert to delegated resolution; conversion rewinds to the last completed node and costs nothing beyond the plan's stated risks.
- [ ] The Marrow Street Clinic encounter offers its 4 resolutions (aid, barter, take, leave) with no forced-combat path, and its opening framing provably differs by D2 monitoring (answered call vs. cold discovery).

## 12. Return and triage
- [ ] Every run ends in the Scrubber Gate return scene; injuries acquired on the run arrive as Condition states requiring treatment time + Meds at the station's medical point — the Aid Car when built, else the Camp/Staging bench at Ash's stated speed/quality penalty (10 §15) — with triage choices when two casualties compete for one bed (event 19 path), verified on both routes.
- [ ] Carried salvage over the commitment weight was genuinely left behind (verifiable against location state on a repeat visit).

## 13. Event consequence
- [ ] All 20 events fire under their conditions across a test matrix of playthroughs; none can fire twice unless authored as repeatable.
- [ ] The 2-crisis cap is never exceeded (automated scheduler test across 500 simulated days).
- [ ] **Scheduler-enforced rhythm rules (D-028), same rig:** a hope- or recovery-register beat occurs in every rolling 3-day window on both high- and low-Accord tracks (the unconditional floor covers the low track); sealed-storm days are always followed by a recovery day; Relay Night never coincides with a storm.
- [ ] All 5 delayed-consequence chains resolve: each later event correctly references its cause, and the cause's absence (different player choice) produces the alternate branch. The clinic chain (run choice → Day 6 gate scene) passes in **all 4 resolutions** (aid/barter/take/leave), each producing a distinct Day-6 scene.
- [ ] At least 2 ignored radio signals visibly resolve off-screen and return as world state (event 9 class).
- [ ] Both failure telegraphs function per the 03 §3.2 mapping: the exodus chain (events 1→3→brownout + storm damage) and the Toll Gate chain (event 6 suppression, event 13 take-then-refuse) each stamp their warning cards before their failure card can fire.

## 14. Seven-day progression
- [ ] A competent playthrough reaches Relay Night in 60–100 minutes of total play across sessions.
- [ ] A fully-delegated (never-active-run) playthrough completes the 7 days and reaches a coherent Relay Night (accessibility + R-06 hedge) — and the player still makes the clinic choice themselves via the gate-call card; no authored moral choice is ever auto-resolved.
- [ ] Both failure axes are reachable in the slice when played for them: utility collapse (surface exodus card) and Accord fracture (Toll Gate warning card at slice scale) — each with its telegraphed warning sequence intact.

## 15. Ending
- [ ] Relay Night presents the Hold-or-Count choice with epilogue text reflecting ≥ 4 tracked facts via the slotted assembly of 03 Note B (verification count, Accord band, survivor losses/Marks, clinic outcome) — tested at slot level.
- [ ] The 0-verified, 1-verified, and 2+-verified variants are all reachable and distinct; at 2+ verified facts the choice gains its third, knowledge-annotated option, and a key resident visibly advocates or objects in-scene.
- [ ] The choice delivers at least one immediate in-scene consequence (a resident's reaction; a station-state change on the epilogue card) — the climax is a payoff before it is anything else.
- [ ] **Monetization boundary (D-033):** the Relay Night choice, its epilogue card, and the safe-stop exhale are fully delivered with no store surface; any future purchase ask appears only after the epilogue's safe stop, never inside the scene or choice flow. Exit-interview probe: no tester describes the chapter ending as "a sales pitch."
- [ ] Across the tester pool, both Hold and Count are chosen at least once, and ≥ 3 of 5 testers report the decision felt difficult, citing at least one week event or verified fact as their reason.
- [ ] The epilogue card states consequences honestly (no false promises about the unbuilt full campaign).

## 16. Save and reload
- [ ] Save-kill-restore at 20 randomized points (including mid-phase, mid-run, mid-event) produces no observable divergence from an uninterrupted control run (automated) — including the save-kill-**convert** case: killing mid-run and choosing delegation on resume resolves correctly from the last completed node.
- [ ] One save slot + autosave rotation survives forced app kill, device restart, and out-of-storage write failure (graceful error, no corrupt state).
- [ ] A Day-7 save from build N loads in build N+1 within the slice period (migration policy exists).

## 17. Mobile controls
- [ ] All primary touch targets ≥ 48 dp/pt with ≥ 8 dp spacing (unified spec satisfying both Apple's 44 pt and Android's 48 dp minimums); secondary chrome ≥ 28 pt; verified by automated UI audit — **including alert badges at both zoom levels** (badges render ≥ 44 pt anchored to rooms at overview, docking to chalk plates at room zoom) **and all build-lens targets (sections, bays, ghost confirms, verb-card buttons, the "all works…" expander) at every zoom where they are tappable** — overview build interaction is section-granularity only (10 §16).
- [ ] Build-mode legibility: the lens shows its mode frame/tint and fixed exit affordance; decision cards queue while the lens is open; the monkey test cannot issue a construction order from normal mode; testers can state which mode they are in without prompting. Construction works orders commit in ≤ 6 taps including lens entry and confirm (auto-assignment default verified); Repurpose and Deconstruct are reachable on any built room in ≤ 2 taps from its verb card.
- [ ] Reach: no interaction requires simultaneous multi-touch except pinch (button alternative exists); all primary actions (confirm, back, crew strip, alerts) sit within a one-thumb reach zone; far-side world taps are reachable by pan or via the crew strip / room list without grip change.
- [ ] The persistent crew strip (4 portraits, thumb-reach corner — D-034) opens any resident's ledger page in ≤ 2 taps and doubles as the tap-tap assignment source; direct sprite-tap is a bonus affordance, never the required path.
- [ ] No accidental-tap catastrophe: all irreversible choices use confirm steps; a 200-tap monkey test on any screen causes no unintended irreversible action.

## 18. Performance
- [ ] ≥ 30 fps sustained (1% low ≥ 24) on both baseline devices at overview zoom during the Day-4 storm (worst case: particles + agents + alarms).
- [ ] Cold start ≤ 20 s; resume-from-background ≤ 3 s.
- [ ] A 12-minute session drains ≤ 4% battery on the Android baseline (screen-on norms); thermal state never reaches "serious" on iPhone baseline.
- [ ] Peak memory within platform comfort (no OS kills during a 30-minute soak with 5 background/resume cycles).

## 19. Accessibility baseline
- [ ] Reading surfaces (stationmaster's log, signal texts, event cards, ledger pages) scale to 200% without loss; dense HUD elements scale to at least 130%; no screen breaks at either setting (automated screenshot audit). Body text contrast ≥ 4.5:1 against its background.
- [ ] All color-coded states carry a redundant shape/icon channel; verified with a color-blind simulation pass (protanopia/deuteranopia/tritanopia). The **engineer's overlay** (09 B.7) is the canonical redundant channel at overview zoom.
- [ ] Every *intermediate warning state* (not just alarms) is perceivable with color removed and sound muted, verified in the blockout readability test.
- [ ] Every audio signal (alarms, radio, barks) has a caption or visible equivalent; the game is fully playable muted.
- [ ] No reflex requirement in base mode; active runs meet the 1.5 s floor (see §11) and delegation covers 100% of run content.
- [ ] Reduced-motion setting removes parallax/shimmer without information loss.

## 20. Slice-level experience gate (the point of it all)
- [ ] In a 5-tester blockout-art playtest: ≥ 4 of 5 correctly explain (a) why a chosen crisis happened, (b) what Signal 45 is and what they currently believe about it, and (c) one delayed consequence they caused — unprompted, in an exit interview.
- [ ] **Personhood (Pillar 2):** ≥ 4 of 5 testers can, unprompted, name all four residents and recount one specific thing that happened to each; ≥ 3 of 5 report at least one assignment or radio decision made because of *who a resident is* (value, Mark, conflict, petition) rather than their aptitude.
- [ ] **Tone (Pillar 5):** from a balanced descriptor card (tense / warm / bleak / hopeful / punishing / fair / exhausting), ≥ 3 of 5 include a warmth-family descriptor, ≤ 1 of 5 selects "punishing" or "exhausting" as dominant, and ≥ 4 of 5 can name one moment that felt good, unprompted.
- [ ] **Differentiation (R-13):** asked to "describe this game to a friend," ≤ 2 of 5 describe it primarily as a two-game hybrid without unprompted mention of the radio/listening choice; failure flags a concept-stage differentiation review.
- [ ] **Building fantasy (Pillar 6):** ≥ 4 of 5 testers agree, unprompted or on a neutral probe, that they "turned a ruin into a home this week"; ≥ 3 of 5 can name one layout decision they made and why (east vs. west; which railcar got the beds; where the Cold Store or the seal went; what they repurposed — all decisions the slice actually offers, 10 §15); ≥ 3 of 5 cite a construction moment (the Breakthrough, a first-lit room) among the week's best moments; ≥ 3 of 5 can name one thing they built (or didn't build) that affected a specific resident.
- [ ] ≥ 3 of 5 express desire to continue past Day 7 ("would you play Day 8?") — the slice's emotional proof, meaningful even with placeholder art.

## 21. Base building and expansion (Pillar 6 — the slice must prove the building fantasy)
- [ ] **Start state verified:** Day 1 presents exactly 4 functional areas (Scrubber Gate, Flywheel Room, Camp with its transfer pump, Listening Post), 2 blocked horizontal paths (east rubble, west flood), 1 blocked level (Deep Service lift), and visible unusable station space beyond them.
- [ ] **Survey:** both blocked paths (and the lift) are surveyable; each survey costs stated labor/intel and returns a one-screen section report (readable at 130% text scale) naming contents, hazards, requirements, **and its story hook**.
- [ ] **Story reveals:** each cleared/drained slice section surfaces its authored reveal (kiosk stall, silt line, shift log — 10 §15) as a staged non-event scene; in exit interviews, ≥ 3 of 5 testers can recount one thing they learned about the station's past by opening it up.
- [ ] **Clear:** at least one section is cleared in normal play, in visible stages (rubble shrinks / waterline falls) performed by assigned residents — never a bare progress bar. The west drain bootstrap (transfer-pump rig or planking) functions as documented.
- [ ] **Build:** ≥ 3 functional rooms are constructed or converted during the week (shell/conversion → furnish → staff), each drawing real utility load and generating work.
- [ ] **Upgrade & expand:** ≥ 1 room upgrade completes (visible + mechanical change), and ≥ 1 module expansion completes (pantry onto the Canteen or filtration module onto the Cistern Works, per route).
- [ ] **Utilities:** ≥ 1 trunk extension connects a new section's service node; the node's capacity is inspectable; at least one moment of insufficient capacity produces the causal "why is this room offline" panel with ≥ 2 viable responses. ≥ 1 monitored radio signal measurably cheapens or de-risks a construction step (V2 lift schematics / beacon pump-state intel), verified in logs.
- [ ] **Repair:** the Scrubber Gate intake repair (storm crisis) completes as a works order through the same construction framework.
- [ ] **Repurpose/rearrange (two-sided):** ≥ 1 room is repurposed or rearranged (the Camp → Staging Room, on either route's berth path) with fair refunds verified (no punitive loss) **and** a real price verified (person-phases spent plus ≥ 1 visible disruption or human-ledger echo in logs — free thrash-relayouting must not be possible).
- [ ] **Capacity & the fifth resident:** sleeping capacity increases during the week; a berth for **Juna Malek** can be prepared by Day 6 on either route; if prepared, she stays — appearing on the crew strip (+1) and in the day report by name; if not, turning her away is an explicit on-screen gate decision with witnesses that crosses Ash's value line. Both branches verified, and the outcome occupies its epilogue fact slot.
- [ ] **Exclusive choice (staged and balanced):** the east/west breakthrough is genuinely exclusive before the storm, per the **Slice Feasibility Sketch** (10 §15 — the blocking deliverable this criterion's math refers to); the choice is staged as the community scene with Ash and Imka's advocacy and the overruled resident's delayed echo; the unchosen path remains reachable late-week at documented higher cost; **both routes produce a completable, coherent week** (full playthrough each, including the west route's documented fallbacks: bench triage at Ash's stated penalty, the cook-ring warm-beat variant, the west-bay berth); **neither route is chosen by > 70% of the exit-test cohort**, and testers on each route cite that route's advantage.
- [ ] **Within-wing layout decisions:** the railcar-role choice, Cold Store siting, seal-bulkhead placement, and berth location all function as decisions with distinct outcomes (10 §15); across 5 testers' Day-7 saves, at least 3 placement/ordering differences appear (station-diversity check, mirroring §10b's schedule diversity).
- [ ] **Layout consequences (all four axes):** across the test matrix, each tension axis fires at least once as a consequence of a *player decision* — noise (railcar/berth siting; **mandatory in normal play**), travel (gate-distance effects on triage/hauling), cascade (overdrawn node brownout), storm isolation (seal-bulkhead choice on storm night) — and each self-explains causally, with its named in-slice recovery verb available (10 §9).
- [ ] **Construction touches people:** ≥ 1 construction or repurposing decision demonstrably changes a named resident's needs/Strain/value/Mark state, verified in logs and self-explaining causally.
- [ ] **Recovery scenario:** from an authored bad-state save (either route, fired layout consequence, storm inbound or just past), a tester reaches a coherent Relay Night with ≥ 3 of 4 residents functional, the R-11 valve firing at most once; the tuning sheet documents this scenario's person-phase math (the 10 §15 worst case).
- [ ] **Visible growth (screenshot test, specified):** at overview zoom with identical framing, using canonical competent-playthrough saves of **both** routes: shown unlabeled Day-1 and Day-7 screenshots, 5 of 5 first-time viewers identify which is later *and* name ≥ 2 visible differences — HUD hidden, and the pass achieved on lighting + geometry (new rooms, absent rubble/water) alone at the blockout tier, with the stage-delta prop vocabulary exempted from the blockout prop cap once it exists.
- [ ] **End state:** a normal playthrough on either route ends with 8–10 functional areas; the day report and epilogue reference what was built ("the week the east wing lit up").
- [ ] **No spam check (Anti-pillar 6, tightened):** a code/data audit confirms every slice room type interacts with ≥ 2 of: utility load, access/travel, resident behavior, structural state, human ledger — **and every habitable or community room counts resident behavior or the human ledger among its two**. No room is a pure timer box.
