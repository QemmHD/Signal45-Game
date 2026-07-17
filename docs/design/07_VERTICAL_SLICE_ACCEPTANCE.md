# 07 — VERTICAL-SLICE ACCEPTANCE CRITERIA

**Status:** LOCKED. The slice ("The First Count", Days 1–7) is accepted only when every criterion below passes. Criteria are written to be testable with blockout art — none depends on final assets.
**Test device baseline:** one 2022 mid-tier Android (e.g. 4 GB RAM class) and one iPhone of similar vintage; 6.1" screen assumed for readability checks.

---

## 1. Complete day loop
- [ ] A new player completes Day 1 (all four phases) in ≤ 12 minutes without external instruction, guided only by in-fiction onboarding.
- [ ] All four phases (Swelter, Slack, Nightrun, Graymorn) are visited in order; each phase boundary shows the safe-stop marker and autosaves (verified by file timestamp/state hash).
- [ ] Time provably does not advance while the app is closed: state hash before backgrounding equals state hash on resume, after 1 minute and after 24 hours.

## 2. Shelter interaction
- [ ] From overview zoom, every one of the 8 rooms can be identified by silhouette/lighting alone (5 of 5 first-time testers name each room's function correctly within 10 seconds of inspection).
- [ ] Any room panel opens in 1 tap from overview; any work order issues in ≤ 3 taps total.
- [ ] Zoom levels (overview ↔ room) transition at ≥ 30 fps with no state desync.

## 3. Resource production and consumption
- [ ] All 5 resources (Water, Rations, Charge, Salvage, Meds) have visible per-day trajectory indicators; a tester asked "will water last through Day 3?" answers correctly from the UI alone in ≥ 4 of 5 trials.
- [ ] A scripted 2-day water deficit (Day 2–3 tuning) is survivable by at least 2 mechanically distinct plans (e.g. purifier cartridge craft vs. arcade nightrun vs. Sable trade), each verified in playthrough.
- [ ] No resource can silently go negative; hitting zero always triggers its authored consequence event, never a stalled simulation.

## 4. Utility failure and recovery
- [ ] The Day 4–5 storm cascade (intake clog → scrubber draw → flywheel dip → pump stall) fires through its visible intermediate states; the event log names each link causally.
- [ ] All 3 authored responses (cut hotplate / throttle scrubbers / hot repair) complete the crisis with distinct, state-recorded outcomes.
- [ ] Every utility subsystem exhibits all 3 damage stages (failing / jury-rigged / restored) somewhere in a normal 7-day playthrough, each visually and audibly distinct.
- [ ] A player who ignores a telegraphed utility warning experiences the failure no sooner than the telegraph promised (no untelegraphed catastrophe — quality gate).

## 5. Survivor assignment
- [ ] Assigning a survivor against aptitude produces measurably different speed/quality/accident numbers than with-aptitude (tunable constants exist and are logged).
- [ ] Swapping any two survivors on Day 1 produces at least one different event, bark, or outcome by Day 3 (automated sim test across all 6 pairings).
- [ ] A refusal state (value-line conflict) can be reached and resolved in normal play; the refusal explains itself in one screen.

## 6. Character condition
- [ ] All 4 needs (Hunger, Fatigue, Condition, Strain) change from play, are readable on the ledger page, and foreshadow via posture/idle animation before reaching critical.
- [ ] Imka's overwork telegraph (event 8) fires when — and only when — the triggering condition is met; ignoring it produces her collapse with the promised timing.
- [ ] Strain relief mechanics (rest, ember tea, canteen scene) each produce logged, distinct recovery amounts.

## 7. Relationship consequence
- [ ] The Teo/Imka radio-time conflict reaches at least 3 distinct outcomes from different player approaches (grant / refuse / broker compromise), verified by distinct Day-6 states.
- [ ] Refusing Teo creates the "Signal Refused" Mark; the Mark demonstrably alters his nightrun reliability and at least one later bark/scene.
- [ ] At least one Accord threshold crossing occurs in normal play, and the correct (warm/withheld) canteen scene variant triggers.

## 8. Room construction or repair
- [ ] At least 2 restoration projects (e.g. antenna mast, Level-1 seal) are completable in the slice, each requiring resources + assigned labor + elapsed phases.
- [ ] A completed restoration visibly changes the room (lighting/animation state) and its function (measurable capacity/quality change).

## 9. Crafting
- [ ] All 12 recipes craftable; queue supports reorder and cancel with refund.
- [ ] The wire → antenna repair → Relay-Night reception chain is completable by Day 6 and its absence measurably degrades Relay Night (verified in both branches).
- [ ] Crafting consumes the stated inputs exactly; interrupted crafting (phase end, save/reload) never duplicates or destroys materials.

## 10. Expedition planning
- [ ] The planning screen shows runner, destination, load-out, risk preview, and return window in one screen; a plan commits in ≤ 6 taps from Slack start.
- [ ] Provisioning provably changes outcomes: the same Depot 9 run with/without mask filters + lantern differs in both active hazard handling and delegated result distribution (logged simulation test, n ≥ 100).

## 11. Active scavenging
- [ ] All 3 locations completable in 3–6 minutes each; timer histogram from playtests confirms the band.
- [ ] The full verb set (reach, take, talk, avoid, flee) is exercised across the 3 locations; no segment requires reaction time under 1.5 s to avoid loss (accessibility gate).
- [ ] Backgrounding mid-run pauses; the player may resume or convert to delegated resolution without loss beyond the plan's stated risks.
- [ ] The Marrow Street Clinic encounter offers its 4 resolutions (approach, barter, take, leave) with no forced-combat path.

## 12. Return and triage
- [ ] Every run ends in the Scrubber Gate return scene; injuries acquired on the run arrive as Condition states requiring Aid Car time + Meds, with triage choices when two casualties compete for one bed (event 19 path).
- [ ] Carried salvage over the commitment weight was genuinely left behind (verifiable against location state on a repeat visit).

## 13. Event consequence
- [ ] All 20 events fire under their conditions across a test matrix of playthroughs; none can fire twice unless authored as repeatable.
- [ ] The 2-crisis cap is never exceeded (automated scheduler test across 500 simulated days).
- [ ] All 5 delayed-consequence chains resolve: each later event correctly references its cause, and the cause's absence (different player choice) produces the alternate branch. The clinic chain (run choice → Day 6 gate scene) passes in all 3 branches.
- [ ] At least 2 ignored radio signals visibly resolve off-screen and return as world state (event 9 class).

## 14. Seven-day progression
- [ ] A competent playthrough reaches Relay Night in 60–100 minutes of total play across sessions.
- [ ] A fully-delegated (never-active-run) playthrough completes the 7 days and reaches a coherent Relay Night (accessibility + R-06 hedge).
- [ ] Both failure axes are reachable in the slice when played for them: utility collapse (surface exodus card) and Accord fracture (Toll Gate warning card at slice scale) — each with its telegraphed warning sequence intact.

## 15. Ending
- [ ] Relay Night presents the Hold-or-Count choice with epilogue text reflecting ≥ 4 tracked facts (verification count, Accord band, survivor losses/Marks, clinic outcome).
- [ ] The 0-verified, 1-verified, and 2+-verified variants of the scene are all reachable and textually distinct.
- [ ] The epilogue card states consequences honestly (no false promises about the unbuilt full campaign).

## 16. Save and reload
- [ ] Save-kill-restore at 20 randomized points (including mid-phase, mid-run, mid-event) produces no observable divergence from an uninterrupted control run (automated).
- [ ] One save slot + autosave rotation survives forced app kill, device restart, and out-of-storage write failure (graceful error, no corrupt state).
- [ ] A Day-7 save from build N loads in build N+1 within the slice period (migration policy exists).

## 17. Mobile controls
- [ ] All touch targets ≥ 44 pt / platform minimum; verified by automated UI audit.
- [ ] Every base-mode interaction operable with one thumb in landscape except pinch-zoom (which has a button alternative).
- [ ] No accidental-tap catastrophe: all irreversible choices use confirm steps; a 200-tap monkey test on any screen causes no unintended irreversible action.

## 18. Performance
- [ ] ≥ 30 fps sustained (1% low ≥ 24) on both baseline devices at overview zoom during the Day-4 storm (worst case: particles + agents + alarms).
- [ ] Cold start ≤ 20 s; resume-from-background ≤ 3 s.
- [ ] A 12-minute session drains ≤ 4% battery on the Android baseline (screen-on norms); thermal state never reaches "serious" on iPhone baseline.
- [ ] Peak memory within platform comfort (no OS kills during a 30-minute soak with 5 background/resume cycles).

## 19. Accessibility baseline
- [ ] Text scaling to 130% breaks no screen (automated screenshot audit).
- [ ] All color-coded states carry a redundant shape/icon channel; verified with a color-blind simulation pass (protanopia/deuteranopia/tritanopia).
- [ ] Every audio signal (alarms, radio, barks) has a caption or visible equivalent; the game is fully playable muted.
- [ ] No reflex requirement in base mode; active runs meet the 1.5 s floor (see §11) and delegation covers 100% of run content.
- [ ] Reduced-motion setting removes parallax/shimmer without information loss.

## 20. Slice-level experience gate (the point of it all)
- [ ] In a 5-tester blockout-art playtest: ≥ 4 of 5 correctly explain (a) why a chosen crisis happened, (b) what Signal 45 is and what they currently believe about it, and (c) one delayed consequence they caused — unprompted, in an exit interview.
- [ ] ≥ 3 of 5 express desire to continue past Day 7 ("would you play Day 8?") — the slice's emotional proof, meaningful even with placeholder art.
