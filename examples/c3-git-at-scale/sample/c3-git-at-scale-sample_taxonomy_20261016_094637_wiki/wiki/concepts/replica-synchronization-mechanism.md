---
title: Replica Synchronization Mechanism
type: dimension
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
- '[[synthesis/systems/cur-cont|Cursor Continuity and Origin]]'
- '[[synthesis/systems/gh-fs|GitHub filesystem distribution]]'
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
---

# Replica Synchronization Mechanism

Which mechanism distributes or applies repository state across replicas?

## Values

| Value | Status | Passages |
|---|---|---|
| [[entities/git-and-rsync-replication|Git-and-rsync replication]] | accepted | 1 |
| [[entities/packfile-level-application-replication|Packfile-level application replication]] | accepted | 1 |
| [[entities/git-level-distribution|Git-level distribution]] | mixed | 3 |
| [[entities/spokes-repository-replication|Spokes repository replication]] | mixed | 11 |
| [[entities/drbd-block-level-replication|DRBD block-level replication]] | rejected | 3 |

## Exclusivity

The values of a dimension are alternatives, so each system should adopt one of them. **1 of 2 systems** adopt one value (or a declared hybrid): exclusivity 0.50.

Values adopted together:

- [[entities/spokes-repository-replication|Spokes repository replication]] and [[entities/git-and-rsync-replication|Git-and-rsync replication]]: [[synthesis/systems/gh-spokes|GitHub Spokes]]
- [[entities/spokes-repository-replication|Spokes repository replication]] and [[entities/packfile-level-application-replication|Packfile-level application replication]]: [[synthesis/systems/gh-spokes|GitHub Spokes]]
- [[entities/git-and-rsync-replication|Git-and-rsync replication]] and [[entities/packfile-level-application-replication|Packfile-level application replication]]: [[synthesis/systems/gh-spokes|GitHub Spokes]]

*The sources combine this dimension's values in many different ways (few shared combinations): the dimension may group several concerns.*

## Evidence

24 open codes from 14 passages in 3 sources.

**Core dimension:** yes ★ (3 sources, 3 systems; core = ≥ 2 sources or ≥ 2 systems).
