---
type: Design Decision
title: Replica Synchronization Mechanism
description: Which mechanism distributes or applies repository state across replicas?
id: '22'
core: true
values: 5
candidate_values: 5
outcomes: 0
evidence:
  codes: 24
  documents: 14
  sources: 3
relations: []
tags:
- dimension
- core
exclusivity: 0.5
systems:
- /synthesis/systems/cur-cont.md
- /synthesis/systems/gh-fs.md
- /synthesis/systems/gh-spokes.md
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Replica Synchronization Mechanism

Which mechanism distributes or applies repository state across replicas?

## Values

| Value | Status | Passages |
|---|---|---|
| [Git-and-rsync replication](/entities/git-and-rsync-replication.md) | accepted | 1 |
| [Packfile-level application replication](/entities/packfile-level-application-replication.md) | accepted | 1 |
| [Git-level distribution](/entities/git-level-distribution.md) | mixed | 3 |
| [Spokes repository replication](/entities/spokes-repository-replication.md) | mixed | 11 |
| [DRBD block-level replication](/entities/drbd-block-level-replication.md) | rejected | 3 |

## Exclusivity

The values of a dimension are alternatives, so each system should adopt one of them. **1 of 2 systems** adopt one value (or a declared hybrid): exclusivity 0.50.

Values adopted together:

- [Spokes repository replication](/entities/spokes-repository-replication.md) and [Git-and-rsync replication](/entities/git-and-rsync-replication.md): [GitHub Spokes](/synthesis/systems/gh-spokes.md)
- [Spokes repository replication](/entities/spokes-repository-replication.md) and [Packfile-level application replication](/entities/packfile-level-application-replication.md): [GitHub Spokes](/synthesis/systems/gh-spokes.md)
- [Git-and-rsync replication](/entities/git-and-rsync-replication.md) and [Packfile-level application replication](/entities/packfile-level-application-replication.md): [GitHub Spokes](/synthesis/systems/gh-spokes.md)

*The sources combine this dimension's values in many different ways (few shared combinations): the dimension may group several concerns.*

## Evidence

24 open codes from 14 passages in 3 sources.

**Core dimension:** yes ★ (3 sources, 3 systems; core = ≥ 2 sources or ≥ 2 systems).
