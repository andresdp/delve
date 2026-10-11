---
title: Pet-repository operational burden
type: value
id: '10.30'
status: outcome
dimension: '[[concepts/replica-topology-and-persistence|Replica Topology and Persistence]]'
accepted_by: []
rejected_by: []
passages: 2
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
tags:
- value
- outcome
- replica-topology-and-persistence
---

# Pet-repository operational burden

Continuously tracking repository locations, validity, failures, and repairs creates substantial operational cost at scale.

## Evidence

- **s01_p09** (supports) · [[sources/s1|Git at any scale]] · Spokes and Consistency
  > Another flaw, impossible to see up front, but painfully obvious after having suffered through it, is that Spokes can be \*rough\* to operate at scale. Because the repositories on disk are always the source of truth for consensus, every copy of every repository is \*very important\*. You have to treat repositories as \*pets, not cattle\*. This means, for starters, that …
- **s03_p08** (supports) · [[sources/s3|Building resilience in Spokes]] · Clean shutdowns
  > We don’t perform “chaos monkey” testing on the Spokes file servers, for the same reasons we prefer to quiesce them before rebooting them: to avoid interrupting long-running reads. That is, we do not reboot them randomly just to confirm that sudden, single-node failures are still (mostly) harmless. Instead of “chaos monkey” testing, we perform rolling reboots as needed, which accomplish …
