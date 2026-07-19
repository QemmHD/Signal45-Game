# Signal 45 — Mobile Build Mode and Camera

Status: Prompt 4 mobile interaction and presentation contract. A playable landscape-phone graybox must validate all thresholds.

## Information architecture

The shelter remains visible. The interface uses:

- **Top/edge HUD:** day/phase, five stocks, urgent alert, Pause/Normal/Fast.
- **Resident rail:** portrait, location, current task, most important warning.
- **Build workflow bar:** Reclaim, Connect, Build, Operate, Adapt.
- **Context panel:** selected target, valid commands, cost/work, blockers, forecast effect, structured invalid reason.
- **Placement controls:** Rotate, Confirm, Cancel, Undo planning action, utility preview.
- **Camera controls:** Overview, Focus, Return, optional Center Selection.

Only one utility overlay is active. Panels collapse instead of stacking over most of the station.

## Five contextual workflows

| Workflow | Commands shown only when relevant |
|---|---|
| Reclaim | Survey, clear, drain, reinforce, remove hazard, salvage |
| Connect | Open/repair passage, restore stair/ladder/lift, connect/isolate/reconnect utility branch |
| Build | Room blueprint, equipment, furniture, partition, valid door, module, decoration |
| Operate | Staff, priority, supply, repair, maintain, utility priority, room policy |
| Adapt | Upgrade, add module, specialize, move, store, repurpose, deconstruct |

The player never receives every subcommand at once.

## Placement interaction

1. Tap a section, room, or object.
2. Choose the contextual workflow and blueprint/object.
3. Move a snapped preview; the camera may pan only after crossing its drag threshold.
4. Use a separate Rotate button.
5. Inspect highlighted validity, utility, access, and forecast effects.
6. Confirm or cancel. Undo applies to the latest uncommitted planning action.
7. Activate an inactive blueprint separately when ready to reserve resources.

Provisional gesture separation:

- tap: movement under 3 mm and release under 300 ms;
- camera drag: one pointer, movement over 4 mm from unselected space;
- object drag: selected preview plus movement over 4 mm;
- long inspection: 500 ms with an accessible tap alternative;
- pinch: two pointers; never confirms placement;
- confirm: explicit button; no timed precision.

These thresholds are hypotheses for device testing, not validated constants.

## Touch and selection

The platform-neutral target floor is 9 mm, with 2 mm separation between unrelated destructive actions. The preferred common-action target is 10–12 mm. Physical props remain believable; invisible padded hit regions provide the touch size.

When targets overlap, selection is deterministic and offers a compact chooser or cycling order. Supports include target chooser, selection cycling, context priority, camera centering, layer filter, selected-entity/room outline, and portrait-driven resident selection. Color is never the only selection or invalid-state indicator.

## Camera states

### Shelter Overview

Predominantly side-on 2.5D cutaway, several wings/levels visible, bounded pan and zoom, no free orbit. Critical actions, alerts, isolation, evacuation, staffing, and utility priority remain possible here.

### Section Focus

Optional intermediate framing for a wing, route, or incident. It is a convenience, not another simulation.

### Room Focus

Focuses the selected logical room, reveals true 3D depth, residents, props, construction and damage, supports slight local pan and closer pinch zoom, and returns to the previous framing predictably. Each room’s bounds and occlusion groups come from machine data.

Camera state never changes work, production, stocks, utilities, incidents, construction, or paths. Saving presentation state is optional.

## Foreground and occlusion

An occluding foreground group may fade, ghost, cut away, lower, or hide when it blocks selection, placement, repair, treatment, a service point, or an important resident action. Collision and simulation remain unchanged. Important support status retains an outline. Reduced motion may change opacity immediately. Art production must not rely on hiding unfinished contradictory geometry.

## Accessibility

- Reduced motion uses an immediate/gentle focus reposition and preserves every function.
- Reduced camera shake affects only presentation.
- Large text can expand/collapse the context panel without hiding Confirm/Cancel.
- Invalidity uses symbol, outline/pattern, text, and highlighted cell list.
- Critical decisions auto-pause and can be made from Overview.
- Tap alternatives exist for hold gestures.
- No build action requires rapid response or pixel-perfect placement.

## Viewport behavior

| Viewport | Contract |
|---|---|
| 844 × 390 | Compact stock labels; collapsible resident rail; one-third-width context sheet; bottom workflow bar inside safe areas |
| 932 × 430 | Full five-stock labels where legible; context sheet no wider than 36%; persistent workflow icons + labels |
| Tablet landscape | More shelter remains visible; do not scale panels to cover it; optional two-column context detail |
| Portrait | Pause and show a rotate-device fallback with save-safe Resume; no dangerous simulation continues behind it |

Notches, home indicators, and system gestures define device-safe insets. No essential control may enter those insets.

## Safe exit

Closing build mode discards preview-only state or saves an inactive blueprint after explicit choice. It never silently activates/reserves. Backgrounding commits the last completed transaction, serializes any partial project, and pauses all simulation. Room Focus closing cannot dismiss a blocking decision or alter the selected project.
