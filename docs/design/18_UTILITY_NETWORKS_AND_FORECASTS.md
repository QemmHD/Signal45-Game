# 18 — UTILITY NETWORKS AND FORECASTS

**Stage:** Prompt 3. **Status:** LOCKED at structural level; values PROVISIONAL in `tools/data/utilities.json` (D-043). Four slice families — **Power · Air · Water · Structure** — as flows/capacity/priority/condition, never currencies. The trunk/node architecture from 10 §8 stands; this document completes it.

---

## 1. The utility graph

Trunks run through real cable galleries; each **section** has a service node; each **room** declares only the utilities it uses (demand, priority tier, degraded-operation mode per 10 §7). Sections connect via authored works orders — no pipe-drawing, ever. **Isolation controls:** bulkhead doors (air/flood), node shutoffs (power), and the Level-1 seal are the player's cascade-breakers. Local backup exists where the fiction earns it: the battery (critical tier, one phase), the transfer pump (water fallback), lanterns (light without grid).

## 2. Power

Generation (Flywheel: partial → stabilized) vs. demand (named loads) with **four priority tiers: Critical (scrubbers) · Essential (lights, radio, pumps) · Normal (hotplate, tools) · Optional** — set per load-class on the ≤8-row board, never per appliance. Overload sheds lowest tier first **with a banner**; the battery bridges Critical one phase after producer failure. HUD/board answers: current load, headroom, top consumer, "what turns off next."

## 3. Air

Filtration capacity (Scrubber Gate states: damaged/repaired/+module) vs. occupancy load, **per section** (core/east/west); storms add intake load. **Air degrades over a 3-phase window, never instantly** — the response window is the design (evacuate, mask, temp filter, restore power priority). Doors and the seal isolate sections; unprotected exposure yields the respiratory condition (17). Filter condition (functional/worn/clogged) drives replacement orders.

## 4. Water (the five-link chain)

**Source → Pumping → Purification → Delivery → Storage.** Every warning names its failing link: "Pump Room offline — purification idle, storage draining" is a different problem from "storage contaminated — boil order available." East's chain is tank+transfer-pump+purifier (labor-backed); west's is cistern+Pump Room (infrastructure-backed). Contamination flags the specific link and its responses (19).

## 5. Structure

**Per bay/section, never global:** safe → strained → unstable → critical → collapsed, with load source, warning signs (dust, creak audio, overlay flag), affected spaces, required reinforcement, evacuation need, and propagation limited to **adjacent unreinforced bays** — reinforcement permanently halts it. Slice hotspots are authored (east canopy bay, west gallery arch); unstable bays block access to their section's node (the structure→utility cross-effect).

## 6. Cross-system effects (bounded)

The five canon couplings from config: power→scrubbers (battery-bridged) · flood→west node · structure→node access · water→sanitation effectiveness · air overload→respiratory risk. Cascade depth caps at 3 (19 §3); every link is one of these five, so chains are always readable from known parts.

## 7. Overlays and diagnosis (mobile readability)

Four overlays — Power / Air / Water / Structure — **one active at a time**, riding the existing engineer's-overlay surface (09 B.7; the build lens force-enables capacity as before). Each shows: source, connected areas, capacity vs. demand, current warning, unconnected/restricted rooms, **likely time-to-failure, and the single most useful response** (the "do this next" line). A selected room answers: requires / receives / why impaired / what restores it / what happens if ignored — plain language first (**"AIR FILTRATION — SCRUBBER GATE"**, never raw telemetry); numbers behind the optional inspect layer. The two-tap diagnosis rule applies to utilities as to stocks.

## 8. The forecast framework (one system for everything)

Five confidence classes, used by stocks, utilities, needs, construction, and weather alike: **Fact** ("Battery: 1 phase") · **Projection** ("Clean water ≈1.8 days at current use") · **Estimate** ("Structural deterioration *likely* during the storm") · **Radio intel** (badged with its source and age) · **Unknown** (shown as unknown — never false precision). Presentation encodes confidence (solid vs. hatched trend, wording: "≈", "likely", "if the band was heard"). The survival model logs every warning with its class and asserts no shortage stage ever lands unwarned.

## 9. Listening Post integration

Monitored bands upgrade forecast **class and lead time**, never create the only warning: weather (2-day forecast vs. the free 1-phase telegraph — D-022), contamination advisories (upstream ash-wash warnings), route closures, supply opportunities, and construction intel (pump-state, schematics — D-039). The radio makes the station *smarter*, the free tier keeps it *fair*.
