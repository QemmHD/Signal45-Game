# Prompt 4 Spatial Scenario Summary

> Deterministic logical validation; this does not prove camera comfort, touch usability, or measured travel time.

- Scenarios: 111
- Passed: 111
- Failed: 0

| ID | Category | Scenario | Result |
|---|---|---|---:|
| P4-001 | coordinates | Valid global address | pass |
| P4-002 | coordinates | Invalid section | pass |
| P4-003 | coordinates | Invalid level | pass |
| P4-004 | coordinates | Invalid depth lane | pass |
| P4-005 | coordinates | Section-local to global conversion | pass |
| P4-006 | coordinates | Rotated footprint | pass |
| P4-007 | coordinates | Save and restore coordinate equality | pass |
| P4-008 | fixed_architecture | Reject column overlap | pass |
| P4-009 | fixed_architecture | Reject track-edge overlap | pass |
| P4-010 | fixed_architecture | Reject outside station shell | pass |
| P4-011 | fixed_architecture | Permit valid convertible shell | pass |
| P4-012 | fixed_architecture | Reject duplicate fixed feature | pass |
| P4-013 | rooms | Place valid Rest room | pass |
| P4-014 | rooms | Place valid Medical room | pass |
| P4-015 | rooms | Place valid Utility room | pass |
| P4-016 | rooms | Reject invalid room family for section | pass |
| P4-017 | rooms | Repurpose valid area | pass |
| P4-018 | rooms | Reject repurpose during active incident | pass |
| P4-019 | rooms | Apply valid module | pass |
| P4-020 | rooms | Reject module chain | pass |
| P4-021 | rooms | Enforce socket limit | pass |
| P4-022 | objects | Place bed | pass |
| P4-023 | objects | Place cot | pass |
| P4-024 | objects | Place workstation | pass |
| P4-025 | objects | Rotate nonsquare object | pass |
| P4-026 | objects | Reject object outside room | pass |
| P4-027 | objects | Reject blocked interaction point | pass |
| P4-028 | objects | Move object | pass |
| P4-029 | objects | Store object | pass |
| P4-030 | objects | Deconstruct once | pass |
| P4-031 | objects | Prevent deconstruction profit | pass |
| P4-032 | objects | Save/reload moved object | pass |
| P4-033 | blueprints | Preview spends nothing | pass |
| P4-034 | blueprints | Saved blueprint reserves nothing | pass |
| P4-035 | blueprints | Activation reserves once | pass |
| P4-036 | blueprints | Delivery consumes once | pass |
| P4-037 | blueprints | Partial construction persists | pass |
| P4-038 | blueprints | Cancel refunds once | pass |
| P4-039 | blueprints | Completion grants capability once | pass |
| P4-040 | routes | Day 1 essential access | pass |
| P4-041 | routes | East Day 7 essential access | pass |
| P4-042 | routes | West Day 7 essential access | pass |
| P4-043 | routes | East alternate validity | pass |
| P4-044 | routes | West alternate validity | pass |
| P4-045 | routes | Poor-but-valid layout | pass |
| P4-046 | routes | Reject only-route blockage | pass |
| P4-047 | routes | Reject stranded resident | pass |
| P4-048 | routes | Reject stranded essential room | pass |
| P4-049 | routes | Reject blocked main gate | pass |
| P4-050 | routes | Reject blocked emergency path | pass |
| P4-051 | routes | Recover access by removing valid object | pass |
| P4-052 | navigation | Normal walk | pass |
| P4-053 | navigation | Material carry | pass |
| P4-054 | navigation | Heavy carry | pass |
| P4-055 | navigation | Patient escort | pass |
| P4-056 | navigation | Patient carry | pass |
| P4-057 | navigation | Emergency evacuation | pass |
| P4-058 | navigation | Utility service | pass |
| P4-059 | navigation | Closed portal | pass |
| P4-060 | navigation | Isolated section | pass |
| P4-061 | navigation | Hazard avoidance | pass |
| P4-062 | navigation | Future vertical route unavailable | pass |
| P4-063 | navigation | Repath after portal restoration | pass |
| P4-064 | medical_access | East gate-to-stabilization | pass |
| P4-065 | medical_access | East gate-to-primary-Medical | pass |
| P4-066 | medical_access | West gate-to-stabilization | pass |
| P4-067 | medical_access | Patient path during storm warning | pass |
| P4-068 | medical_access | Treatment route blocked and alternate response shown | pass |
| P4-069 | utilities | Power connection | pass |
| P4-070 | utilities | Disconnected branch | pass |
| P4-071 | utilities | Platform lighting sheds | pass |
| P4-072 | utilities | Platform lighting restores | pass |
| P4-073 | utilities | Platform Lighting Upgrade does not create another consumer | pass |
| P4-074 | utilities | Charge backup requires connection | pass |
| P4-075 | utilities | Air isolation | pass |
| P4-076 | utilities | Water isolation | pass |
| P4-077 | utilities | Structure closure | pass |
| P4-078 | utilities | Utility service point reachable | pass |
| P4-079 | incidents | Filter service route | pass |
| P4-080 | incidents | Water isolation route | pass |
| P4-081 | incidents | Structural evacuation | pass |
| P4-082 | incidents | Medical evacuation | pass |
| P4-083 | incidents | Second major incident remains queued | pass |
| P4-084 | incidents | Cascade adjacency stops at configured limit | pass |
| P4-085 | day5 | East prepared response | pass |
| P4-086 | day5 | West prepared response | pass |
| P4-087 | day5 | Filter Materials delivery | pass |
| P4-088 | day5 | Charge-control access | pass |
| P4-089 | day5 | Water-isolation access | pass |
| P4-090 | day5 | Medically restricted resident evacuation | pass |
| P4-091 | day5 | Coordinate-derived travel fits or produces named failure | pass |
| P4-092 | route_identity | West has shorter Water-service metric | pass |
| P4-093 | route_identity | West has better drain/isolation metric | pass |
| P4-094 | route_identity | East has better Rest-access metric | pass |
| P4-095 | route_identity | East has better quiet-recovery metric | pass |
| P4-096 | route_identity | East has longer gate-Medical metric | pass |
| P4-097 | route_identity | Neither route dominates every metric | pass |
| P4-098 | hope | East minimal hope anchor | pass |
| P4-099 | hope | West minimal hope anchor | pass |
| P4-100 | hope | Full hope setup | pass |
| P4-101 | hope | Hope anchor survives reload | pass |
| P4-102 | hope | Hope grants no stock | pass |
| P4-103 | feasibility_integration | Replace East travel allowance without double counting | pass |
| P4-104 | feasibility_integration | Replace West travel allowance without double counting | pass |
| P4-105 | feasibility_integration | Re-run Full East proof | pass |
| P4-106 | feasibility_integration | Re-run Full West proof | pass |
| P4-107 | feasibility_integration | Re-run East mistake | pass |
| P4-108 | feasibility_integration | Re-run West mistake | pass |
| P4-109 | feasibility_integration | Re-run prepared storm | pass |
| P4-110 | feasibility_integration | Re-run Juna cases | pass |
| P4-111 | feasibility_integration | Re-run all Prompt 2 and Prompt 3 mandatory scenarios | pass |
