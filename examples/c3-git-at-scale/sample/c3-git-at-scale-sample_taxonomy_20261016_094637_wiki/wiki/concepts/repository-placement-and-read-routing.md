---
title: Repository Placement and Read Routing
type: dimension
id: '13'
core: true
values: 9
candidate_values: 9
outcomes: 0
evidence:
  codes: 10
  documents: 8
  sources: 3
relations: []
tags:
- dimension
- core
exclusivity: 0.0
systems:
- '[[synthesis/systems/cur-cont|Cursor Continuity and Origin]]'
- '[[synthesis/systems/gh-fs|GitHub filesystem distribution]]'
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
---

# Repository Placement and Read Routing

How are repositories placed and requests routed to suitable hosting replicas?

## Values

| Value | Status | Passages |
|---|---|---|
| [[entities/closest-sufficiently-fresh-replica-routing|Closest sufficiently fresh replica routing]] | accepted | 1 |
| [[entities/explicit-repository-location-tracking|Explicit repository-location tracking]] | accepted | 1 |
| [[entities/rendezvous-hashed-repository-routing|Rendezvous-hashed repository routing]] | accepted | 2 |
| [[entities/single-replica-read-routing|Single-replica read routing]] | accepted | 3 |
| [[entities/stale-routing-recovery|Stale-routing recovery]] | accepted | 2 |
| [[entities/stateless-repository-placement|Stateless repository placement]] | accepted | 1 |
| [[entities/external-routing-database-placement|External routing-database placement]] | rejected | 1 |
| [[entities/per-server-repository-location-tracking|Per-server repository location tracking]] | rejected | 1 |
| [[entities/single-on-disk-repository-behind-http|Single on-disk repository behind HTTP]] | rejected | 1 |

## Exclusivity

The values of a dimension are alternatives, so each system should adopt one of them. **0 of 2 systems** adopt one value (or a declared hybrid): exclusivity 0.00.

Values adopted together:

- [[entities/rendezvous-hashed-repository-routing|Rendezvous-hashed repository routing]] and [[entities/stale-routing-recovery|Stale-routing recovery]]: [[synthesis/systems/cur-cont|Cursor Continuity and Origin]], [[synthesis/systems/gh-spokes|GitHub Spokes]]
- [[entities/stateless-repository-placement|Stateless repository placement]] and [[entities/rendezvous-hashed-repository-routing|Rendezvous-hashed repository routing]]: [[synthesis/systems/cur-cont|Cursor Continuity and Origin]]
- [[entities/stateless-repository-placement|Stateless repository placement]] and [[entities/stale-routing-recovery|Stale-routing recovery]]: [[synthesis/systems/cur-cont|Cursor Continuity and Origin]]
- [[entities/explicit-repository-location-tracking|Explicit repository-location tracking]] and [[entities/rendezvous-hashed-repository-routing|Rendezvous-hashed repository routing]]: [[synthesis/systems/gh-spokes|GitHub Spokes]]
- [[entities/explicit-repository-location-tracking|Explicit repository-location tracking]] and [[entities/stale-routing-recovery|Stale-routing recovery]]: [[synthesis/systems/gh-spokes|GitHub Spokes]]
- 7 more pair(s)

*The sources combine this dimension's values in many different ways (few shared combinations): the dimension may group several concerns.*

## Evidence

10 open codes from 8 passages in 3 sources.

**Core dimension:** yes ★ (3 sources, 3 systems; core = ≥ 2 sources or ≥ 2 systems).
