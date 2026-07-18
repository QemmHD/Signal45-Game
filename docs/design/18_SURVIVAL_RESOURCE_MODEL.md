# Signal 45 — Survival Resource Model

> Prompt 3 contract. Numerical values are provisional. `tools/feasibility/data/model.json` is authoritative if this explanatory document and executable data ever differ.

## Locked ceiling

The shelter overview has exactly five primary stocks: **Food, Clean Water, Medicine, Materials, and Charge**. Power, Air, Water, and Structure are utility states rather than currencies. Detailed components remain blockers beneath Materials and do not become additional HUD stocks.

No stock drains while the application is closed. Consumption, gain, loss, reservation, and release occur at named transactions or ledger boundaries.

## Five-stock ontology

| Stock | Internal unit | Player interpretation | Primary sources | Primary sinks | Storage and reservation |
|---|---|---|---|---|---|
| Food | ration-equivalent | one ordinary adult daily meal issue | starting stores, trader, Harbor Annex carry choice | Graymorn meal, packed nightrun ration, aid/admission | sealed dry-store capacity; packed rations reserve at expedition commitment |
| Clean Water | person-issue equivalent | stored clean water ready for drinking or care | starting storage, West treatment throughput, trader | daily issue, named treatment, Juna stabilization | only clean connected or declared isolated reserve counts; treatment and packed water reserve by ID |
| Medicine | treatment-use equivalent | general medical supplies consumed by named care | starting locker, medical trader, declared cache | examination, stabilization, respiratory, injury, and waterborne care | one top-level locker; active treatment reservations are unavailable elsewhere |
| Materials | common-build bundle | mixed common construction and repair stock | starting stores, reclamation salvage, annex salvage | projects, repair, trade, bypasses, Highball wear | common capacity; project reservation and delivered stage persist separately |
| Charge | reserve unit before conversion loss | stored energy in the flywheel and cells | starting charged reserve; no routine slice recharge | connected-load backup, Relay Load Test, storm, Highball | one finite reserve; each discharge names its consumer and commits atomically |

## Shared stock rules

Every stock record contains:

- current amount, capacity, warning, minimum viable, and comfortable thresholds;
- confirmed reservations keyed by transaction ID;
- committed use and confirmed gain for the next ledger;
- primary source, primary drain, likely consequence, and available responses;
- a named cause for any loss;
- an idempotent save representation.

Forecasts use `current − committed use + confirmed gain`. Estimates never invent gains. A reservation is not a debit twice: a transaction either reserves/consumes once or resumes the existing committed state.

## Food

The First Count uses stored rations; it does not add agriculture.

| Issue | Canonical amount per resident | Immediate effect | Repeated effect |
|---|---:|---|---|
| Normal | 1.00 | Fed | none |
| Restricted | 0.75 | Hunger advances one step; Stress rises | two days become Restricted; three become Prolonged shortage |
| Missed | 0.00 | Hunger advances; no immediate critical Health loss | continued shortage can strain Health after warning |
| Emergency | 0.50 | visible small meal; Hunger and Stress | not a sustainable default |
| Packed nightrun | 1.00 per traveler | reserved at loadout | returned only if the committed departure is cancelled safely |

Juna consumes aid immediately when admitted or stabilized. She is not a Food reward and does not repay the added person-day during the slice.

Ordinary responses are a restricted meal window, a trader purchase, or selecting Food instead of other annex carry value. Emergency response may use a half issue or defer the shared meal. Neither creates Food. The +20% ignored case ends below the minimum reserve; rationing or trade restores viability with Hunger, Stress, Materials, or opportunity cost.

Spoilage is not passive. It may occur later only as a forecast incident with a named amount, response window, and physical cause.

## Clean Water

Clean Water is the stored stock; the Water utility controls whether source water becomes safely stored stock.

| Issue | Canonical amount per resident | Consequence |
|---|---:|---|
| Normal | 1.50 | ordinary daily issue |
| Restricted | 1.10 | saves stock, raises Stress, and constrains treatment/cleaning |
| Packed nightrun | 1.50 | reserved at loadout |
| Named treatment | condition-defined | reserved with the treatment transaction |
| Emergency use | 2.00 representative | cleanup, manual filter service, or stabilization |

The Water utility remains a five-link chain: source → pumping → treatment → delivery → clean storage. A link failure may prevent new clean stock without erasing stored reserve. Contaminated storage is isolated and does not count as usable Clean Water.

East remains Water-fragile. Its +20% ignored case falls below reserve; one deliberate restriction plan restores Full Proof at a resident cost, while reserve plus deferral supports Recover First. West remains stronger: it retains treated throughput and ends the comparative pressure case with slightly more Water even when East responds.

## Medicine

Medicine has no unexplained passive expiration. It is consumed only through named care:

1. examination;
2. stabilization;
3. minor treatment;
4. serious treatment;
5. respiratory treatment;
6. waterborne treatment;
7. Juna stabilization when needed.

Starting a treatment atomically reserves its Medicine and Clean Water once. Interruption preserves the reservation. Completion has a separate idempotency key. If care cannot start because the room or capable staff is unavailable, no stock is consumed.

Medicine pressure is answered by protecting stabilization and deferring nonurgent follow-up, accepting Stress and delayed recovery, or by obtaining declared supply. Ignoring the tested temporary pressure falls below the minimum reserve; prioritization produces Recover First without free Medicine.

## Materials and component blockers

Materials summarize common bundles, not every object. These route-critical families remain distinct:

- filter material;
- structural brace;
- electrical relay;
- pump seal;
- radio component.

A blocked project names the missing family. Common Materials cannot impersonate a pump seal or relay.

Project activation reserves common Materials once. Partial delivery and work persist. Cancellation returns only the configured class fraction; repeating cancellation returns nothing. Deconstruction and inferior substitution cannot create profit. Inferior substitution must declare reduced reliability, strain, or later repair before commitment.

Under tested shortage, deferring the five-WU authored hope setup and using the earned zero-WU fallback preserves survival as Recover First. Ignoring the shortage falls below the repair reserve.

## Charge

Charge and Power are deliberately different:

- **Power** is live source capacity, branch connection, demand, priority, condition, and fault.
- **Charge** is finite stored reserve with a per-stage discharge ceiling and conversion loss.

The slice starts with 24 of 30 reserve units. A discharge can deliver at most 3 units per stage and loses 10% during conversion. The player sees the named consumer, delivered amount, stock draw, loss, duration, and remaining reserve.

Charge cannot:

- energize a disconnected branch;
- repair a failed source;
- remove a fault;
- conceal an indefinite deficit;
- be claimed twice after reload.

The Relay Load Test, storm, critical Air/medical backup, and Highball may consume Charge. Load shedding or delay may preserve it. There is no routine seven-day recharge; later recharge equipment is a full-game extension of the same stock, not a sixth resource.

## Route, visitor, expedition, and trader interactions

| Context | Food | Clean Water | Medicine | Materials | Charge |
|---|---|---|---|---|---|
| East | same ration burden | weaker reserve/throughput | better early treatment work | normal salvage | same finite reserve |
| West | cold-meal Stress context | stronger treatment and storm recovery | rougher early care | better salvage | same finite reserve |
| Juna admitted | aid and fifth-person issue | stabilization and fifth-person issue | only if named care requires it | temporary accommodation may displace a project | no automatic gain |
| Active expedition | packed ration; optional Food choice | packed water | declared cache only | route component/salvage choice | no exclusive reward |
| Delegated expedition | identical graph facts and stock rules | identical | identical | identical required objective | identical |
| Trader | transparent exchange | transparent exchange | transparent exchange | payment/opportunity cost | no premium replenishment |

## Save representation

Each stock serializes amount, capacity-relevant state, reservations, committed transaction IDs, and named loss/gain records. Mid-animation closure resumes the committed logical state. Rewards, refunds, treatment reservations, Relay discharge, and expedition returns are idempotent.

## Slice and full-game boundary

The slice proves discrete issues, named care, reservations, route components, finite Charge, emergency responses, and forecasts. It does not add farming, a large crafting inventory, individual pipe simulation, passive expiration, or routine Charge generation. Full-game rooms may extend sources and specializations while preserving the five-stock HUD ceiling.

## Prototype gates

- Verify that “ration-equivalent,” “person-issue,” and Charge duration language is understood without decimals.
- Test whether the Water stock/utility distinction is diagnosable within two taps.
- Measure whether visible meal and issue moments feel consequential without excessive ceremony.
- Confirm that Materials blockers feel informative rather than arbitrary.
- Revalidate all consumption after resident movement and animation timings exist.
