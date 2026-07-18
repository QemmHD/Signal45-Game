# Signal 45 — Work and Construction Model

## Purpose and authority

The work-unit model is the smallest internal abstraction able to test seven-day capacity. It is not a complete resident AI and is not presented as a player-facing currency. Canonical values are loaded from `tools/feasibility/data/model.json`.

One **work unit (WU)** is a normalized share of useful resident effort after task setup. It can represent reclamation, installation, repair, production support, treatment, hauling, or incident response. It does not represent one minute or one animation cycle.

## Resident capacity

Each of the four starting residents has a provisional base of **12 WU per day**. A resident may perform at most **8 WU of useful continuous work** before a rest or task change. Prompt 3 corrects the emergency rule: a Critical, collapsed, unconscious, medically incapacitated, or severely respiratory-restricted resident supplies **zero productive WU**. The **available shelter labor pool**, not each person, must supply a two-WU emergency survival minimum.

Daily project capacity is calculated as:

`sum(condition-adjusted resident capacity) − personal overhead − travel − hauling − essential work − treatment − incidents − promise repayment − rework`

Personal upkeep reserves 1.5 WU per available resident. Baseline essential shelter operation reserves 10 WU per day, plus 3 WU for nightrun preparation on Day 3 and 2 WU for visitor processing on Day 6.

### Condition multipliers

The four locked resident conditions multiply capacity. They do not create additional need bars.

| Condition | Light state | Middle state | Severe state | Critical contextual state |
|---|---:|---:|---:|---:|
| Health | healthy 1.00 | strained 0.85 | impaired 0.65 | critical 0.40 |
| Hunger | fed 1.00 | restricted 0.95 | missed 0.85 | prolonged 0.65 |
| Fatigue | rested 1.00 | tired 0.85 | exhausted 0.60 | collapse risk 0.40 |
| Stress | steady 1.00 | elevated 0.90 | high 0.75 | acute 0.55 |

Prompt 2 uses only bounded task-fit tags: Strong 1.15, Capable 1.00, Poor 0.75, and Ineligible 0.00. Full preferences, boundaries, memories, and negotiation belong to later resident-system prompts.

## Travel, delivery, setup, and observation

Work performed is separate from travel and hauling. East uses an 8% compact-layout travel allowance; West uses a 10% typical-layout allowance. A poor-but-valid layout test uses 16%. Hauling reserves another 4% of gross capacity. A sensitivity multiplier tests higher overhead without pretending exact path lengths are known.

Setup is represented by project activation and material reservation, not by visible construction work. Material delivery is a committed stage. Observation animation consumes player-facing time but not extra WU. A resident walking animation never decides whether progress was committed.

Mandatory spatial revalidation must measure average and vertical travel, carrying trips, congestion, lift/stair delay, material delivery, and path failures. A 50% travel-overhead increase leaves East viable at 9.7% buffer but makes West infeasible at 7.0%, so this is a critical prototype gate.

## Multi-worker behavior

Worker contribution is capped by project class and uses diminishing efficiency:

| Class | WU range | Useful workers | Efficiencies | Materials and components | Interruptibility |
|---|---:|---:|---|---|---|
| Planning/placement | 0 | 0 | immediate | none unless activation follows | preview is freely reversible |
| Short install | 3–6 | 1 | 100% | small delivery | interruptible; partial where useful |
| Standard project | 7–14 | 2 | 100%, 65% | delivery plus possible component | interruptible; exact remainder saved |
| Major reclamation | 20–32 | 3 | 100%, 70%, 40% | staged delivery and blocker | interruptible across multiple days |

Adding a worker beyond the cap produces no work. Small objects do not invoke major-project ceremony.

## Canonical seven-day project schedule

Target day is the desired beat. Hard day is the last viable completion checkpoint. Missing a target creates visible carryover pressure; missing a hard day fails the relevant proof. This distinction replaced an early hard-cliff model that made one ordinary mistake unrecoverable.

### Mandatory for both routes

| Project | Class | Available | Target / hard | WU | Materials | Blocker | Benefit |
|---|---|---:|---:|---:|---:|---|---|
| Platform lamp install | Short | 1 | 1 / 1 | 4 | 1 | — | first visible improvement |
| Triage cot install | Short | 1 | 1 / 1 | 5 | 1 | — | Medical area and tutorial path |
| Route survey | Short | 2 | 2 / 2 | 4 | 0 | lamp | visible risk forecast |
| Concession repurpose | Standard | 3 | 4 / 5 | 7 | 2 | survey | room adaptation and one area |
| Storm filter preparation | Standard | 3 | 4 / 5 | 9 | 3 | filter material | storm preparation |
| Workshop install | Standard | 5 | 6 / 7 | 13 | 5 | repurpose | Workshop proof and one area |
| Storage fit-out | Standard | 5 | 6 / 7 | 9 | 3 | repurpose | Storage proof and one area |
| Triage upgrade | Standard | 5 | 6 / 7 | 11 | 3 | triage cot | room upgrade proof |
| Forecast board | Short | 5 | 6 / 7 | 6 | 2 | survey | forecast and signal evidence |
| Storm recovery repairs | Standard | 5 | 7 / 7 | 9 | 3 | survey | visible recovery |
| Hope-beat setup | Short | 7 | 7 / 7 | 5 | 1 | recovery and storage | recovery/hope beat |

### East route-mandatory

| Project | Class | Target / hard | WU | Materials | Blocker | Benefit |
|---|---|---:|---:|---:|---|---|
| East reclamation | Major | 3 / 4 | 26 | 8 | structural brace | opens wing and adds one area |
| East utility connection | Standard | 4 / 5 | 10 | 4 | electrical relay from annex | connects branch |
| Quiet berths | Standard | 4 / 5 | 12 | 5 | connection | Rest upgrade, +2 beds, one area |
| East water reserve | Standard | 4 / 5 | 7 | 2 | reclamation | reduces storm Water loss |

### West route-mandatory

| Project | Class | Target / hard | WU | Materials | Blocker | Benefit |
|---|---|---:|---:|---:|---|---|
| West reclamation | Major | 3 / 4 | 26 | 8 | structural brace | opens wing, salvage, one area |
| West utility connection | Standard | 4 / 5 | 10 | 4 | reclamation | connects branch |
| Water treatment | Standard | 4 / 5 | 12 | 5 | pump seal from annex | Water upgrade and one area |
| Drain isolation | Short | 4 / 5 | 4 | 2 | reclamation | storm Water protection |

### Optional and stretch work

| Project | Tier | WU | Cost | Value | Hidden dependency status |
|---|---|---:|---:|---|---|
| Comfort lighting | Optional | 10 | 4 Materials and 1 Power load | comfort/load-shedding lesson | never required |
| Relay upgrade | Optional ending preparation | 8 | 4 Materials + radio component | Strengthen Relay eligibility | never required for slice survival |
| Visitor screen | Optional | 6 | 2 Materials | one temporary rest place | useful for prepared West admission, not required to survive or refuse |

No optional project is included in the required-project set. Starting and cancelling Comfort Lighting scenarios remain viable.

## Partial work, interruption, cancellation, and recovery

- Activation reserves Materials and named components once against a stable project ID.
- Partial progress stores exact remaining WU after every committed increment.
- Interrupted workers return to the labor pool at the next scheduling boundary; work is neither duplicated nor erased.
- Standard cancellation returns 50% of reserved Materials; short installs return 75%; major reclamation returns 35%. Components already delivered are not silently duplicated.
- The refund has its own claim ID, so reopening or replaying an animation cannot grant it twice.
- Completion benefits fire once after the completion transaction, before celebration animation.
- Target misses queue a warning and carryover; hard misses state the exact failed project.

## Highball feasibility

Highball remains optional: S01 and S02 complete both routes with zero uses. Candidate speed benefits are **25%, 35%, and 50%**, all provisional.

| Case | WU saved | Later capacity loss | Charge | Material wear | Net WU before resource valuation | Verdict |
|---|---:|---:|---:|---:|---:|---|
| One use, 25% | 5.20 | 6 | 2 | 1 | -0.80 | creates timing shift, not free output |
| One use, 35% | 6.74 | 6 | 2 | 1 | +0.74 | useful margin candidate; not selected as final |
| One use, 50% | 8.67 | 6 | 2 | 1 | +2.67 | fastest candidate; requires playtest scrutiny |
| 35%, promise broken | 6.74 | 11 over two days | 2 | 1 | -4.26 | viable but costly; next order refused |
| Two consecutive 35% uses | 11.73 | 18 | 6 | 3 | -6.27 | escalating cost defeats indefinite spam |

The emotional Stress and refusal effects are explicit Prompt 5 placeholders. The model proves only that repayment exists, repeated use loses capacity, and competent play does not require it. It does not prove which speed feels fair.

## Feasibility result

Prompt 3 keeps the 12-WU base and project schedule. The old ten-WU daily survival allowance is now eight essential WU plus two explicit incident-reserve WU, with no capacity increase. East and West still end at ten areas without Highball. Aggregate unused project WU is 36.788 East and 27.108 West, but both have **zero daily/phase slack on Day 5** after the prepared storm response; this replaces the earlier practice of presenting one weekly percentage as the full margin. A 10% global work loss or 15% construction increase remains a high-severity revalidation case.
