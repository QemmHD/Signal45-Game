# 05 — RESEARCH NOTES

**Status:** COMPLETE for the concept-lock stage. Compiled from a parallel research sweep (8 tracks, primary-source-first) run 2026-07-17.

**Epistemic legend — read before citing this document:**
- **Verified** — a primary source (official page, developer interview/talk, platform documentation) was actually fetched and states it.
- **Likely** — stated by a credible secondary source (press, wiki, aggregator); not independently confirmed.
- **Unverified** — could not be confirmed; retained only where the uncertainty itself is useful. Never cite as fact.
- **Design inference** — our analysis, not a sourced fact.
- **Signal 45 decision** — a choice recorded in the decision log (08), influenced by but not attributable to any source.

No proprietary text is reproduced; observations are paraphrases. Nothing here is legal analysis.

---

## Track 1 — Fallout Shelter (inspiration #1: base readability, mobile sessions, monetization lessons)

| Source | Type | Relevant observation | Confidence |
|---|---|---|---|
| Fallout Shelter Steam page (Bethesda) | Official product page | Loop framed as: build vault, keep residents happy, match jobs to skills, craft, send explorers out; F2P with IAP packs; DICE Mobile GOTY 2016 | Verified |
| Same | Official product page | The Radio Room's function is *attracting new dwellers* — the radio is a passive population-recruitment faucet, not an information channel | Verified |
| Bethesda support docs | Official documentation | Nuka-Cola Quantum is a purchasable time-acceleration resource (added post-launch) | Verified |
| Player.One update coverage | Press (secondary) | Quantum + quests arrived in update 1.6 (~1 year post-launch), after earlier premium additions | Likely |
| Wikipedia | Wiki (secondary) | Cutaway grid vault; three same-type adjacent rooms merge; elevators as circulation; workers visible in rooms | Likely |
| Wikipedia | Wiki (secondary) | Assignment is a one-to-one S.P.E.C.I.A.L.-stat-to-room lookup; higher match = faster production + happier dweller | Likely |
| Wikipedia | Wiki (secondary) | Launch "rush" verb: instant completion gamble with incident risk — impatience priced in risk, not money (at launch) | Likely |
| Deconstructor of Fun analysis | Industry analysis (secondary) | Engagement collapse attributed to missing session cut-offs, a content ceiling reachable in days, and no long-term goals; Todd Howard's pitch lineage ("Little Computer People meets The Sims meets Fallout") | Likely |

**Design inferences (ours):** Shelter's readability comes from discipline (one function/color per room, workers always visible, one-glance status) — adoptable as a *rule*, not a look. Its stat-lookup assignment is legible but strategically flat and helped exhaust content. Its two most-cited failures — no session boundaries, no ending — are structural opportunities. Its launch goodwill came from *not* selling time; goodwill eroded when a time-skip currency arrived.

**Signal 45 decisions:** Keep the one-glance readability rule but express it through found-space station architecture, not grid cells (D-008, 09 §B). Assignment gains depth from the shared day/night personnel pool and relationship effects, not stat lookups (D-005). The fixed campaign supplies the ending Shelter lacked; phase boundaries supply session cut-offs without paywall timers (D-003). The radio is inverted from recruitment faucet to zero-sum information instrument (D-002). No time-skip purchases, ever (Anti-pillar 5).

---

## Track 2 — This War of Mine (inspiration #2: day/night structure, civilian tone, moral consequence)

| Source | Type | Relevant observation | Confidence |
|---|---|---|---|
| TWoM Steam page | Official product page | Strict day/night loop with diegetic lock (daytime snipers); night = send one civilian to one chosen location | Verified |
| 11 bit official site | Official product page | Explicit civilian-survival framing; "no good or bad choices, only survival" positioning | Verified |
| Steam page | Official product page | Charcoal-stylized aesthetic grounded in real wartime events; $19.99 PC | Verified |
| Game Developer interview (P. Miechowski) | Developer interview | Moral consequence built as simulation: survivors become depressed after theft/selfish acts; the player self-judges, systems respond | Verified |
| Same | Developer interview | Early playtesters treated bland survivors as expendable; backstories + individual skills were added specifically to force engagement with them as people; UI language reworded communally ("Our Things") | Verified |
| Game Developer talk coverage (M. Drozdowski) | Developer talk coverage | Dilemmas deliberately lack win-win outcomes; symbolic minimal-explicitness art ("half a face") relies on player imagination | Verified |
| Apple App Store listing | Official store listing | Mobile remains premium today: $13.99 + $1.99 expansion; 18+ rating | Verified |
| Pocket Gamer | Press (secondary) | Mobile launched tablet-first premium (~$14 regular); phone version ~4 months later with a redesigned small-screen UI | Likely |
| Wikipedia | Wiki (secondary) | The in-game radio is a free ambient feed (weather, prices, war news); siege length randomized, ends in ceasefire; psychology feeds per-character endings; 9M+ copies by 2024 | Likely |

**Design inferences (ours):** The day/night split works because each phase has distinct decision texture *and* a credible in-fiction lock — Signal 45 needs its own (it has one: lethal daytime heat). Moral consequence lands via simulation, not karma meters. Premium ~$14 is viable on mobile *with imported prestige*. TWoM's radio is passive flavor — making information scarce and chosen is a genuine structural departure. Named, specific survivors are the proven antidote to spreadsheet play. A randomized end-date sustains dread but frustrates planning; a fixed-but-doubtable deadline inverts this.

**Signal 45 decisions:** The swelter is our diegetic day-lock — ours, not borrowed (D-003, 00 §5). Consequence lives in Strain/Marks/Accord simulation; no moralizing UI (D-001, D-018). Four decision-driven phases with an optional, delegable night differ structurally from TWoM's fixed two-phase real-time day (D-003, D-007; divergence tracked as risk O2). Signal 45's *investigable* truth replaces the randomized ceasefire pattern (D-002). Charcoal-monochrome treatment is on the forbidden list (04 §3).

---

## Track 3 — Frostpunk & Frostpunk: Beyond the Ice (society metrics, telegraphed crises, deadline campaigns, mobile cautionary tale)

| Source | Type | Relevant observation | Confidence |
|---|---|---|---|
| GOG/11 bit official pages | Official product pages | "Society survival" positioning; pillars: city survival, hope, law, moral choices, exploration | Verified |
| Game Developer interview (M. Fijak) | Developer interview | Hope/discontent are bottom-up aggregates of individual agents with ~13–14 Maslow-style needs — the meter is diagnosable, not arbitrary | Verified |
| Same | Developer interview | Law system designed as "boiling frog" escalation — each step small and justified; players author their own slide | Verified |
| Same | Developer interview | Tone calibration lesson: too subtle → unnoticed; too graphic → unintentionally comic; restrained middle register required | Verified |
| Official Beyond the Ice site | Official product page | Mobile adaptation is a NetEase-developed, Com2uS-published, 11-bit-licensed product (Oct 2024) | Verified |
| Apple App Store listing | Official store listing | Beyond the Ice restructured around retention/social systems (industries, guilds, trading, rankings, minigames); IAP $0.99–$99.99 | Verified |
| TapTap editorial (I. Boudreau) | Press review (secondary) | Press verdict: timers/battle passes/boosters converted scarcity into spending prompts; moral layer effectively removed; "cynical" — while the store rating sat at 4.5/5 | Likely |
| Fandom wiki | Wiki (secondary) | Main scenario ≈45–48 days, three acts, finale storm announced days ahead | Likely |
| — | — | Claim that intermediate cold snaps are always forecast on-screen | Unverified |

**Design inferences (ours):** Society meters earn trust only when visibly derived from individuals — surface *whose* grievance moved the needle. Telegraphed catastrophe with re-planning time is the crisis rhythm that works; Signal 45 can go further by making the *forecast itself* a scarce, allocated resource (a layer Frostpunk never had). Decision systems should pair instant relief with a deferred bill and a position on an escalation track. The genre is uniquely allergic to monetizing scarcity — scarcity *is* the emotional core; store ratings understate the press/core-audience damage.

**Signal 45 decisions:** Accord aggregates from named individuals and always names its movers (D-018). Telegraph law is scheduler-enforced (D-019). Forecast-as-a-choice is core to the Listening Post (D-002). Monetization never touches simulation; the Beyond the Ice pattern is the canonical counter-example recorded against Anti-pillar 5 (D-010). A ~45-day, three-act, storm-crescendo deadline campaign is genre-shared structure; ours differentiates by making the deadline's truth the investigable variable (00 §12, 02 §7).

---

## Track 4 — RimWorld (small-cast character simulation, incident pacing, feasibility lessons)

| Source | Type | Relevant observation | Confidence |
|---|---|---|---|
| rimworldgame.com / Steam | Official product pages | Officially framed as a "story generator"; events dealt by an AI storyteller; selectable pacing personas (random / rising tension / relaxed) | Verified |
| Steam page | Official product page | Mood-driven colonists with cause-legible stressors; mental breaks when stress exceeds tolerance; traits/backstories hard-gate which work a colonist will do | Verified |
| Official site | Official product page | Relationships run on a compact per-pair opinion value driving love/fights | Verified |
| GDC 2017 talk (T. Sylvester) | Developer talk | Deliberately left features out for players to imagine; rejected heavy pre-planning; defined the product as a story generator, not a game | Verified |
| "The Simulation Dream" (Sylvester essay) | Developer essay | Player Model Principle (simulation only matters if it reaches the player's mental model); apophenia (players project depth onto simple systems); design for story-richness, primal stakes | Verified |
| RimWorld wiki | Wiki (secondary) | Threat sizing from colony wealth + count with caps; "adaptation" mercy rule after losses; ~1–2 major threats per 7–10 days with cooldowns | Likely |
| Wikipedia | Wiki (secondary) | ~5 years of public iteration by a 2–3 person team to 1.0; Unity; >$100M by 2020 | Likely |

**Design inferences (ours):** Legibility beats depth for a small cast — any state the player can't see is wasted cost; list mood causes in plain language. Signal 45's radio can be a *diegetic* pacing instrument (what you monitor shapes which "cards" reach you) — an in-fiction evolution of storyteller selection. Adopt the pattern (grace period, 1–2 majors/week, cooldowns, escalation to finale, mercy after a death), not a scoring AI: event decks with cooldowns are tunable by a small team; RimWorld's pacing took years of public iteration.

**Signal 45 decisions:** Every survivor state is surfaced with stated causes (Pillar 2, 07 §6). The event system is an inspectable deck/scheduler with cooldowns, caps, and telegraphs — no opaque director (D-019). A quiet mercy rule after a death is adopted into full-game tuning goals (02 §6 anti-monotony; noted for systems stage). "Storyteller"/"AI director" branding is avoided (04 adjacency hygiene).

---

## Track 5 — Sheltered (family-scale shelter, utility upkeep, micromanagement failure modes)

| Source | Type | Relevant observation | Confidence |
|---|---|---|---|
| Steam page | Official product page | Family in a bunker; needs, crafting, recruiting, turn-based combat, trauma-affected stats | Verified |
| TGG developer interview (Unicube) | Developer interview | Family premise chosen specifically for emotion/story; two-person team; positioned as harder than Fallout Shelter | Verified |
| PCGamesN review | Press review | 5/10: progression halts after ~a month; collapses into repetitive maintenance; family members "faceless bots" whose deaths carry no weight | Verified |
| GameWatcher review | Press review | 6.5/10: too many simultaneous maintenance demands; loot too random (27 in-game days waiting for one hinge) | Verified |
| TheSixthAxis review | Press review | 8/10: praised difficulty and the *option to automate inhabitants* — players choose their engagement depth; flagged RNG hard-locks (water droughts) | Verified |
| Apple App Store listing | Official store listing | Mobile: $3.99 premium, no IAP; 4.1/5 (~355 ratings); listing feedback cites save bugs, overlapping UI, steep learning curve | Verified |
| Analog Addiction review | Press review | Needs-servicing overwhelming at scale (tracking which of 8 survivors needs the toilet); expedition loop itself judged sound | Verified |
| — | — | Mobile users complained of unresponsive/unclear touch targets; Android delisting ~2024 | Unverified |

**Design inferences (ours):** Upkeep-as-content is the genre's central failure mode — utility pressure must escalate/mutate across the arc, not repeat at constant frequency. Default-on automation of routine servicing is the single best-liked mitigation. An emotional community premise *fails* if characters are mechanically interchangeable — this is the direct cautionary proof for Pillar 2. Pure-RNG gating of deterministic goals reads as unfair; information should convert scarcity from lottery to decision. 3–4 interlocking utility clocks beat 7+ independent timers. Always leave a costly recovery path.

**Signal 45 decisions:** Standing orders/automation for anything done three times (Anti-pillar 4). Five interlocked subsystems with escalation via storm cycles, not constant-frequency decay (D-009, 02 §5). Radio intel is the designed answer to loot-lottery frustration — spend capacity to *know where the hinge is* (D-002). Diegetic safety-valve events (Sable arrives with what's scarcest, at a price) prevent RNG dead-ends (R-11 contingency). Survivor deaths must alter systems and story, not just a roster count (Pillar 2; 07 §14).

---

## Track 6 — Oxygen Not Included (utility networks, cascading failure, readability, what mobile must abstract)

| Source | Type | Relevant observation | Confidence |
|---|---|---|---|
| Steam page (Klei) | Official product page | System visualization marketed as a feature (watch air move; monitor CO₂); failure modes (overloads, meltdowns) part of the fantasy | Verified |
| Game Developer interview (G. Jans) | Developer interview | Difficulty emerges from *layered simultaneous needs*, each individually manageable; neglected systems degrade | Verified |
| Same | Developer interview | Cascading interdependence in a closed loop — tuning one resource ripples outward; constant rebalancing by designer and player | Verified |
| Same | Developer interview | Much perceived depth is engineered illusion: simple visible behaviors + implied off-screen events | Verified |
| Game Developer interview (J. Seidenz) | Developer interview | No-tutorial philosophy: tune systems/UI until players feel they discovered mechanics; sim-management sits "a few steps from feeling like work" | Verified |
| Klei on X (Dec 2022) | Official developer statement | Console port would need major work: heavy simulation + mouse/keyboard-dependent UI; the game has never shipped on mobile | Verified |
| ONI wiki | Wiki (secondary) | ~14 full-screen overlays isolate one system each by recoloring the base | Likely |
| — | — | Cutaway ant-farm presentation (evident from screenshots; no fetched text states it) | Unverified |

**Design inferences (ours):** The one-system-per-lens recolor pattern transfers to mobile, but at 3–4 lenses, not 14. Klei's own port-blocker statement argues *against* per-tile simulation on mobile: a graph/zone abstraction (rooms as nodes, cables/ducts as edges, scalar states) preserves the felt interconnection at mobile budgets. Player value lies in chains of consequence, not emergent physics — hand-authored cascades with tuned propagation delays deliver the drama deterministically. Invest in feedback (flow particles, flicker, steam, audio) over fidelity. The cutaway-with-visible-networks is itself a marketable screenshot.

**Signal 45 decisions:** Abstract network model confirmed (D-009) — ONI's port-blocker statement is the strongest external evidence for cut C3. Authored cascades with visible intermediate states (Pillar 1, D-019). "Illusion of complexity" feedback investment is an art-stage directive (09 §B.4, B.8). Optional overlay lenses deferred to full game as a possibility, capped at 3–4 if adopted (noted for systems stage). Discovery-over-tutorial onboarding: the slice's Day 1–2 teach in fiction (03 §3; 07 §1).

---

## Track 7 — Mobile platform guidance (Apple HIG, Android quality guidelines)

| Source | Type | Relevant observation | Confidence |
|---|---|---|---|
| Apple HIG — Game controls | Platform documentation | Frequent touch controls ≥ 44×44 pt; secondary controls ≥ 28×28 pt | Verified |
| Android core app quality | Platform documentation | Touch targets ≥ 48 dp; accessibility guidance repeats 48×48 dp minimum | Verified |
| Apple HIG — Accessibility | Platform documentation | Spacing matters as much as size (~12–24 pt padding); contrast 4.5:1 (small text) / 3:1 (large); text enlargeable **≥ 200%**; respect Reduce Motion (replace zoom/scale with fades) and Dim Flashing Lights; convey information with more than color; avoid auto-dismissing timed UI; consider difficulty accommodations | Verified |
| Apple HIG — Layout | Platform documentation | Full-bleed games must respect safe areas (cutouts, Dynamic Island); menus must adapt across 4:3 to 19.5:9+; landscape games must support both rotations | Verified |
| Android — display cutout / Play games guidelines | Platform documentation | Cutout modes; SDK 35 forces edge-to-edge; no critical controls in cutouts; landscape full-screen at 4:3/16:10/21:9 anchors | Verified |
| Apple HIG — Notifications | Platform documentation | Consent required; no repeated notifications for one event; badges only for unread counts; foreground arrivals surfaced subtly | Verified |
| Android 13+ notification permission | Platform documentation | POST_NOTIFICATIONS runtime permission; request *in context* after familiarity; no cross-promo/ad notifications | Verified |
| Android core quality / Apple lifecycle / Play Level Up | Platform documentation | State preservation on interruption is a *requirement*; exact-state resume from Recents/lock; cloud save with conflict resolution mandatory for Play's Level Up program; iCloud saved games recommended | Verified |

**Design inferences (ours):** Adopt the stricter platform as a single spec (≥48 dp/pt primary targets with 8–12 dp spacing) — disproportionately important for a dense management UI. Build the HUD as full-bleed art with an inset interaction frame reflowing 4:3→21:9. Interruption-safety is a mechanic constraint, not polish (never a real-time moment that can't survive a phone call). The radio is a natural, compliant *diegetic* moment for the notification-permission ask — and denial must cost nothing, which Signal 45's design already guarantees. Dark-palette games fail contrast first: commit to 4.5:1 body text now. Text-heavy surfaces need ~200% scaling support.

**Signal 45 decisions:** Unified touch spec set to ≥48 dp/pt (07 §17, 09 A.6 updated; amendment D-021). Reading surfaces (log, signals, events) scale to 200%; dense HUD floors at 130% with a high-contrast option (07 §19 updated; D-021). Notification opt-in framed diegetically at Listening Post activation, still defaulting to zero notifications (09 A.7; D-021). Interruption/resume behavior was already designed to this bar (02 §8; A.4); cloud save confirmed full-game scope (03 §4).

---

## Track 8 — Premium & trial-then-unlock mobile market evidence

| Source | Type | Relevant observation | Confidence |
|---|---|---|---|
| TWoM App Store listing | Official store listing | $13.99 premium + $1.99 expansion; 4.4/5 (~2.2K ratings) | Verified |
| Rebel Inc. App Store listing | Official store listing | $1.99 entry + optional expansions/unlocks; 4.8/5 (~41K ratings) — largest volume in the set | Verified |
| Ndemic official FAQ | Official developer FAQ | Android model: free to start, "Premium Version" upgrade; main game fully unlockable through play | Verified |
| 60 Seconds! App Store listing | Official store listing | $3.99 flat, no IAP; 4.3/5 (~2.9K) | Verified |
| Bad North App Store listing | Official store listing | $3.99, no IAP, Apple Editors' Choice — yet 3.8/5 (~1.7K): featuring ≠ user-score success | Verified |
| Game Developer breakdown (L. Saada, Playdigious) | Developer postmortem | Dead Cells mobile premium "no argument" — F2P ruled out to preserve positioning | Verified |
| Playdigious interview (X. Liard) | Developer interview | Premium-only ≈ giving up ~99% of the mobile market — the developer's own niche sizing | Verified |
| Apple App Store Review Guidelines 3.1.1 | Platform documentation | Free time-based trial before full unlock is explicitly sanctioned (Tier-0 non-consumable + required disclosure of boundary and price) | Verified |
| Frostpunk: Beyond the Ice listing + TapTap editorial | Store listing + press | The F2P conversion of a morally-serious survival brand: $0.99–$99.99 IAP, loot boxes — 4.5/5 store rating alongside "cynical/soulless" press framing | Verified / Likely |

**Design inferences (ours):** The verified premium band is $1.99–$13.99, with ~$14 sustained only by imported prestige; a new IP realistically enters at $3.99–$6.99 flat *or* free-entry hybrid. The Ndemic hybrid shows the best reception-per-reach in the set. Trial-then-unlock is platform-sanctioned, not a workaround; the paywall belongs at a designed narrative cliff with the boundary disclosed upfront. Store ratings understate core-audience damage from monetized scarcity. Expansion-shaped DLC at $1.99–$4.99 is the accepted second revenue line for this audience.

**Signal 45 decisions:** D-010 confirmed and sharpened: free Chapter One → single permanent unlock, boundary disclosed upfront, placed at the Relay Night hope beat (Day 7 — at the early edge of the research-inferred day 8–12 window; accepted because Relay Night is the arc's natural cliff-of-meaning, revisit trigger recorded in D-010). Post-launch monetization is expansion-shaped only (03 §5). Nothing consumable, ever (Anti-pillar 5).

---

## Cross-track synthesis (all design inference — no single source)

1. **The Listening Post's originality claim is externally supported:** in both main comparisons the radio is passive (recruitment faucet; ambient flavor feed). No surveyed title makes *allocating what to know* a core scarce verb. This is Signal 45's clearest open ground.
2. **The genre's two proven killers are unbounded upkeep and interchangeable people.** Every relevant postmortem/review converges on these. Signal 45's counters (escalating-not-constant pressure, automation defaults, named-cast ceiling, Marks) are direct responses.
3. **Monetized scarcity is the genre's third rail** — evidenced from both the restraint-praise direction (Fallout Shelter's launch, TWoM, Dead Cells) and the backlash direction (Quantum, Beyond the Ice). Signal 45's restrictions are a market position, not just an ethical one.
4. **Mobile feasibility hinges on abstraction discipline:** the deepest-simulation comparison (ONI) has never shipped on a phone, per its developer, for exactly the reasons Signal 45's C3 cut and graph-abstraction model avoid.
5. **Fixed-deadline + telegraphed-crisis campaigns are proven** (≈45-day three-act arcs exist in the genre), so Signal 45's differentiation must come — and by design does come — from the deadline's investigable truth, not from the deadline's existence.
