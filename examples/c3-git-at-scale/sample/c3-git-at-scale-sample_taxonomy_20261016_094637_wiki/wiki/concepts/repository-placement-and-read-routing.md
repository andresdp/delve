---
type: Design Decision
title: Repository Placement and Read Routing
description: How are repositories placed and requests routed to suitable hosting replicas?
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
- /synthesis/systems/cur-cont.md
- /synthesis/systems/gh-fs.md
- /synthesis/systems/gh-spokes.md
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Repository Placement and Read Routing

How are repositories placed and requests routed to suitable hosting replicas?

## Values

| Value | Status | Passages |
|---|---|---|
| [Closest sufficiently fresh replica routing](/entities/closest-sufficiently-fresh-replica-routing.md) | accepted | 1 |
| [Explicit repository-location tracking](/entities/explicit-repository-location-tracking.md) | accepted | 1 |
| [Rendezvous-hashed repository routing](/entities/rendezvous-hashed-repository-routing.md) | accepted | 2 |
| [Single-replica read routing](/entities/single-replica-read-routing.md) | accepted | 3 |
| [Stale-routing recovery](/entities/stale-routing-recovery.md) | accepted | 2 |
| [Stateless repository placement](/entities/stateless-repository-placement.md) | accepted | 1 |
| [External routing-database placement](/entities/external-routing-database-placement.md) | rejected | 1 |
| [Per-server repository location tracking](/entities/per-server-repository-location-tracking.md) | rejected | 1 |
| [Single on-disk repository behind HTTP](/entities/single-on-disk-repository-behind-http.md) | rejected | 1 |

## Exclusivity

The values of a dimension are alternatives, so each system should adopt one of them. **0 of 2 systems** adopt one value (or a declared hybrid): exclusivity 0.00.

Values adopted together:

- [Rendezvous-hashed repository routing](/entities/rendezvous-hashed-repository-routing.md) and [Stale-routing recovery](/entities/stale-routing-recovery.md): [Cursor Continuity and Origin](/synthesis/systems/cur-cont.md), [GitHub Spokes](/synthesis/systems/gh-spokes.md)
- [Stateless repository placement](/entities/stateless-repository-placement.md) and [Rendezvous-hashed repository routing](/entities/rendezvous-hashed-repository-routing.md): [Cursor Continuity and Origin](/synthesis/systems/cur-cont.md)
- [Stateless repository placement](/entities/stateless-repository-placement.md) and [Stale-routing recovery](/entities/stale-routing-recovery.md): [Cursor Continuity and Origin](/synthesis/systems/cur-cont.md)
- [Explicit repository-location tracking](/entities/explicit-repository-location-tracking.md) and [Rendezvous-hashed repository routing](/entities/rendezvous-hashed-repository-routing.md): [GitHub Spokes](/synthesis/systems/gh-spokes.md)
- [Explicit repository-location tracking](/entities/explicit-repository-location-tracking.md) and [Stale-routing recovery](/entities/stale-routing-recovery.md): [GitHub Spokes](/synthesis/systems/gh-spokes.md)
- 7 more pair(s)

*The sources combine this dimension's values in many different ways (few shared combinations): the dimension may group several concerns.*

## Evidence

10 open codes from 8 passages in 3 sources.

**Core dimension:** yes ★ (3 sources, 3 systems; core = ≥ 2 sources or ≥ 2 systems).
