# 16 — SURVIVAL ECONOMY

**Stage:** Prompt 3. **Status:** LOCKED at structural level. **All numeric values are PROVISIONAL** (D-043) and live in one place: `tools/data/resources.json` — this document explains structure and behavior; it never duplicates numbers the config owns. Validation: `tools/survival_model.py` (20 scenarios) + `tools/test_survival_model.py`.

---

## 1. Resource ontology (three layers)

**Layer 1 — five primary stock resources** (the whole HUD): **Food · Clean Water · Medicine · Materials · Charge**. This maps the mandated canonical set with one evidenced substitution (D-043): the *Fuel* role is filled by **Charge** (stored cell-hours from the Flywheel) because Signal 45's fiction has no combustion fuel — Charge already behaves exactly as Fuel must: it powers defined equipment, the load board names its primary consumer, and emergency reserve time is forecast ("Battery: ~1 phase if the Flywheel fails"). Aliases survive as fiction flavor (residents say *rations*, *meds*, *salvage*); the HUD uses the plain names. Population/beds are capacity, not stock; trust, labor, information, and utility capacity are never disguised as top-bar currencies.

**Layer 2 — flow and capacity systems** (never collectible): Power, Air, Water-network, Structure — four slice families (18). Thermal pressure modifies rooms and incidents without an independent network in the slice; sanitation derives from water + cleaning + crowding (both full-game candidates *only* if testing proves the decisions justify the interface cost — extension boundary recorded here).

**Layer 3 — item families** (storage/crafting/expedition detail): thirteen families architected in `resources.json → item_families`. The slice tracks **filters, tools, radio components** distinctly (they gate specific projects) and folds metal/parts/textiles into Materials. **The anti-lie rule:** a blocked project always names its missing family ("needs: antenna wire — Depot 9 or Sable"), never a bare "not enough Materials." Detailed recipes are the crafting stage's work.

## 2. Stock specifications (structure; values in config)

Each stock defines in config + here: sources/sinks, storage, reservation, forecast, shortage stages, emergency responses, room/resident/expedition/trade interactions, save representation (plain floats in the world-state object), slice scope, and full-game extension.

### Food (person-meals)
Consumed at the **two visible meal windows**; produced by runs, trade, and the Canteen's waste reduction. Storage caps at the pantry (Cold Store raises it). Perishables from runs must be eaten within 2 days or convert to stable rations at half value — **forecast, never silent loss**. Shortage stages: *thin* (forecast chip) → *short meals* (hunger + stress steps; no injury — one missed meal is never critical harm, asserted in tests) → *sustained shortage* (work efficiency down, health erosion begins with its own warning). Emergency: **ration** (fewer meals/day; saves stock, costs stress and a remembered decision), trade, an extra run. Full-game: ingredient variety, the Spore Beds/Grow Gallery production chain.

### Clean Water (person-days)
The **stock** is stored clean water; pumping/pressure/purification are Layer-2 processes (18). Consumed at meals + a works draw on heavy build days. Sources: tank duty (labor), purifier bonus, the cistern chain (west's strategic prize), runs. Contamination is a **defined incident** (19) whose warning names the failing link (storage vs. purification vs. supply). Shortage stages: *low* (≈days chip) → *rationing available* (stress cost) → *dry taps* (pressure, contextual dehydration condition — never instant harm). Emergency: ration, boil order (charge cost), source switch, manual hauling.

### Medicine (doses)
One top-level value in the slice. **Committed when treatment begins** (at triage — the lumpy-stock HUD shows free vs. booked doses); never passively lost; no expiration in the slice or the 45-day campaign (decision: expiry adds bookkeeping, not decisions). Sources: the clinic run (its moral branches yield differently), Sable. Emergency: triage priority (who waits), the clinic re-run, purchase.

### Materials (salvage units)
**The labor model owns this ledger** (15) — the survival layer mirrors it; one truth. Reservation canon (11 §5): reserved at confirmation, consumed at visible stages, unconsumed reserve refunds 100%, consumed stages never refund; **deconstruction recovers 50% of consumed materials once per installed component** — build/cancel/salvage loops are structurally profitless (asserted). The HUD chip shows free vs. reserved; tapping shows the family breakdown and why a specific project is blocked.

### Charge (cell-hours)
The stored buffer between the Flywheel (producer) and the load board (consumers). Surplus banks to the cell rack (cap visible); deficits shed the optional tier **with a banner, never silently**. The battery reserve bridges the critical tier one phase after producer failure — the canonical "14 minutes if the Flywheel fails" forecast. Emergency: shed tiers, battery, HIGHBALL overdrive (19), hand-cranking (brutal labor fallback).

## 3. The main HUD specification

Five chips + day/phase clock (unchanged budget): each chip shows **amount · trend arrow · ≈person-days/operating time · warning state**; one tap expands to the forecast contract (11 §4.1): steady stocks show top consumer + top idle producer; lumpy stocks (Medicine, Materials) show **free vs. reserved/booked** + the upcoming-draws list + earliest failing commitment. **Two-tap diagnosis rule (07-tested):** any major shortage's main source is identifiable in ≤2 taps. No formulas in normal play; the advanced inspect layer holds raw numbers.

## 4. Emergency substitutions (cross-stock)

Rationing (food/water) · tier-shedding (charge) · boil order (water↔charge) · manual labor for utility gaps (water hauling, hand-cranking — WU-expensive, always available) · breaking stored equipment for parts (once, 50%) · trade/faction purchase (premium prices in crisis — the R-11 valve's scope) · inferior-materials substitution (full game: quality states). Every substitution states immediate benefit, immediate cost, delayed cost, affected residents, reversibility, and any promise created (19 §6).

## 5. Slice vs. full game

Slice: exactly this document. Full game boundaries (explicitly deferred): ingredient-level food, water quality tiers, contextual medical items, item condition (functional/worn/broken applies to *equipment*, not every object), the sanitation/thermal networks if earned, market price drift. Data structures (config-driven stocks + families) already accommodate these without slice rework.
