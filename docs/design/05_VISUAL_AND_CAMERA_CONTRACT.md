# Signal 45 — Visual and Camera Contract

## Non-negotiable presentation

Signal 45 uses a **predominantly side-on 2.5D cutaway presentation rendered from a true 3D world**. From the full shelter view, the station reads like a clear two-dimensional sliced-open map. This readability is the primary camera goal.

The world nevertheless contains:

- 3D room and construction geometry;
- 3D residents and props;
- authored physical depth and navigation lanes;
- layered foreground, playable plane, and background;
- real-time or baked/hybrid lighting as performance allows;
- shadows, particles, atmosphere, water, dust, smoke, sparks, and cinders;
- geometry/material states for construction, damage, reinforcement, and repair.

“True 3D” does not authorize free orbit, arbitrary behind-the-wall views, first-person interaction, or fully free character navigation.

## Shelter Overview

The overview is the default management state and must:

- show several station levels and wings at once;
- keep rooms, connections, blocked routes, residents, urgent issues, and visible transformation readable on a landscape phone;
- preserve a side-on camera angle with only a small fixed downward/yaw bias if needed for depth;
- use silhouettes, lighting, activity, symbols, and restrained overlays instead of requiring tiny prop inspection;
- keep the day/phase, five resources, portrait rail, urgent issue, simulation controls, Build access, and Listening Post/expedition access available without covering most of the station;
- allow drag-to-pan and pinch-to-zoom within authored bounds;
- allow one utility overlay at a time.

The overview is not a miniature Room Focus. Small decorative props may simplify, animation may use lower-cost variants, and residents may use silhouette-preserving LODs.

## Room Focus

Tapping a room or choosing **Focus** transitions to a bounded, closer inspection state over the same room and simulation.

Room Focus must:

1. center the selected room predictably;
2. zoom smoothly enough to reveal equipment, residents, construction, damage, and material depth;
3. allow additional pinch zoom within a safe range;
4. allow slight pan inside and immediately adjacent to the room;
5. support selecting residents, objects, machinery, blueprints, hazards, and damaged elements;
6. preserve simulation continuity and state—no duplicate “interior instance” exists;
7. expose a contextual panel rather than every possible command;
8. return to the previous overview framing with one clear Back/Overview action;
9. maintain an always-available pause and respect decision pauses;
10. offer a reduced-motion path that cuts or gently crossfades to the focused framing.

Room Focus reveals detail; it does not unlock separate hidden mechanics that the overview cannot represent or forecast.

## Camera limits

- **No free orbit.** The player cannot rotate around rooms or discover a rear gameplay face.
- **No first-person or over-the-shoulder mode.**
- **No uncontrolled perspective changes.** Focal length, tilt, and side angle remain within authored ranges.
- **No cinematic camera required for routine actions.** Focus transitions should be brief and interruptible.
- **No essential information at extreme zoom only.** A symbol, panel, or target chooser exposes critical state.
- **No pixel-perfect targets.** Invisible hit regions, target cycling, selection lists, and camera centering resolve overlaps.
- **No camera-dependent simulation.** Zoom level may change rendering/animation LOD, never production, pathing outcome, or incident logic.
- **No hiding urgent state behind foreground geometry.** Occlusion rules are deterministic and testable.

Exact zoom ratios, transition durations, projection choice, field of view, and maximum shelter span remain prototype questions.

## Foreground fading and cutaway rules

Columns, wall returns, ceilings, pipes, props, resident crowds, and equipment may obstruct valid interactions. The presentation system may fade, ghost, cut away, lower, or temporarily hide foreground elements when:

- the selected target is behind them;
- a placement footprint or connection path must be read;
- a resident’s task or treatment animation is the current focus;
- damage or hazard interaction is otherwise blocked;
- accessibility settings request stronger occlusion reduction.

Rules:

- transitions are quick, consistent, and reversible;
- faded objects retain a subtle silhouette when spatial context matters;
- collision and simulation do not change when rendering fades;
- hiding never reveals out-of-scope “backstage” art or breaks the station shell;
- critical structural supports retain an outline or overlay status;
- reduced-motion mode replaces sweeping reveals with near-instant opacity changes.

## Visual target

The target is **grounded, credible, and materially serious**, with enough stylization and modular discipline to be feasible on mobile.

### Materials and atmosphere

- worn concrete, glazed tile, rusted and painted metal, damp stone, old enamel signage;
- cloth, wood repairs, cables, pipes, pooled and dripping water, dust, grime, soot, cinder, smoke, sparks;
- strong value grouping and silhouettes before surface detail;
- practical lamps, work lights, emergency amber, railway red/amber/green accents, and deep darkness;
- cold cinder-filled surface light and damp green-gray abandoned tunnels;
- warm light, textiles, personal belongings, repaired paint, organized storage, and handmade signage gradually accumulating in inhabited spaces.

### Characters and motion

- believable adult proportions and physical weight;
- serious, economical work and injury motion rather than broad cartoon loops;
- a shared technical skeleton and reusable task library, with silhouette, clothing, posture, prop, timing, and behavior accents distinguishing residents;
- readable state at overview distance through posture and task, with face detail reserved for Room Focus and portraits;
- no resident rarity framing, collectible reveal, or combat-centric animation hierarchy.

### Damage and construction

- authored stage changes: rubble → cleared shell → reinforced bay → functional room → adapted/personalized room;
- leaks, cracks, corrosion, soot, failed lamps, water lines, temporary bracing, cable runs, patch plates, and repaired finishes;
- damage must identify a system or incident rather than function as randomized visual noise;
- construction geometry and worker activity appear in the world instead of only a progress ring.

## Distinction from references

Signal 45 may pursue the emotional seriousness and material credibility associated with survival-management games, but must not reproduce another title’s:

- charcoal or hand-sketched rendering treatment;
- monochrome/limited palette structure;
- exact cutaway composition, zoom, vignette, or camera movement;
- character silhouettes, clothing designs, animation sets, rooms, props, maps, icons, or effects;
- interface layout, typography, notification behavior, or color grammar.

The original visual language is **railway signal order emerging from climate-collapse disorder**: functional colored signals, route maps, maintenance markings, old civic tile, and improvised community signs against cinder darkness. A comparative visual audit is required at concept-art lock. No legal-clearance claim is made.

## Mobile UX contract

- Landscape is primary; minimum touch targets and enlarged invisible hit regions are mandatory.
- Tap selects; drag pans; pinch zooms; placement uses a rotation button, Confirm, Cancel, and Undo rather than gesture precision.
- When targets overlap, show a chooser or cycle selection and center the camera.
- Common contextual actions fit within the five workflows: Reclaim, Connect, Build, Operate, Adapt.
- Context panels preserve a majority view of the selected room and collapse when not needed.
- Forecasts use plain language and symbols plus color; no state relies on color alone.
- The portrait rail prioritizes urgent resident condition and current assignment without showing more than four permanent need indicators.
- The selected room or resident panel replaces, rather than stacks over, the prior context.

## Accessibility contract

Accessibility affects rendering and interaction architecture from the first prototype:

- adjustable text size with reflow and truncation avoidance;
- high-contrast mode and user-tested value separation;
- symbols, labels, patterns, and animation in addition to color;
- reduced motion and reduced camera shake;
- Room Focus without mandatory cinematic travel;
- subtitles and speaker labels for all speech/radio information;
- visual sound-direction indicators for important off-screen cues;
- independent haptic settings and no haptic-only information;
- adjustable simulation speed and pause during decisions;
- tap alternatives for holds and repeated gestures;
- extended or paused expedition decision time;
- enhanced forecasts with explicit cause and response steps;
- confirmations for irreversible actions and optional repeat-action confirmations;
- plain-language failure reasons and causal recap;
- target chooser and selection cycling for motor/vision accessibility.

## Production boundaries

Prompt 2 does not redesign this camera. Its timing model budgets five seconds of a normal interaction for camera/selection and reduces transition time under reduced motion, while every simulation result remains invariant to Overview, zoom, and Room Focus. Those budgets require playable measurement.

- Higgsfield and other generative tools may support mood boards, anchors, room/lighting studies, motion reference, marketing concepts, and trailer planning.
- Generated output is not automatically a runtime asset. Record prompt/tool/source/version and rights notes, then apply consistency review, modeling or cleanup, rigging, animation, texturing, pivots, collision, optimization, and export validation.
- Use a modular station kit, trim/material sets, decals, authored damage variants, shared resident rigs, prop atlases, and LODs.
- “Realistic” means convincing scale, material response, motion weight, and damage logic—not photoreal textures, unique assets for every room, or unlimited dynamic lights.
- Performance, memory, battery, thermal, load-time, draw-call, bone, particle, and texture budgets are not yet validated and must be established on representative lower/mid target devices.

## Future graphics-stage questions

These remain unanswered until the appropriate graphics and camera prototype stage:

1. Orthographic, weak perspective, or constrained perspective projection?
2. Exact overview and Room Focus zoom bounds and transition timings?
3. Baked, mixed, or real-time light allocation per room and incident?
4. Resident/room LOD distances, update frequency, animation culling, and crowd cap?
5. Maximum simultaneous transparent/faded surfaces without mobile overdraw failure?
6. Modular bay dimensions and how many unique shell variants are affordable?
7. Material/texture atlas strategy, decal limits, and authored damage-state count?
8. Particle and volumetric substitutes for cinder, dust, water, steam, smoke, and light shafts?
9. Portrait production method and consistency with in-world characters?
10. Accessibility-safe palette and overlay patterns?
11. Asset provenance and rights-review workflow for every generated or sourced reference?
12. Representative device frame-time, memory, storage, battery, and thermal budgets?

## Camera acceptance prototype

Before final graphics production, a graybox build must show four adjacent functional areas, two levels, at least four moving residents, one placement action, one repair, one utility overlay, and one incident. It must demonstrate overview readability, Room Focus selection, obstruction fading, zoom/pan bounds, reduced motion, target choosing, rapid return, and uninterrupted save/pause. Results must be measured on representative phones; a desktop capture alone is not validation.

## Prompt 3 physical-state amendment

The graybox must also distinguish powered/shed/disconnected equipment; the five Air stages; clean/suspect/contaminated/isolated Water; Safe through Closed Structure; treatment occupancy; evacuation; and incident recovery aftermath. The Day 4 Relay Load Test must visibly dim and restore the canonical Platform Work Lamp. Prompt 4 now supplies machine-readable Overview/Room Focus bounds and occlusion groups; camera state remains non-authoritative. These are presentation requirements for one camera-independent simulation, not authorization for final assets.
