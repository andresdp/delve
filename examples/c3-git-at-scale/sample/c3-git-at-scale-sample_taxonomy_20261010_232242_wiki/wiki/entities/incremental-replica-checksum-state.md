---
title: Incremental replica checksum state
type: value
id: '10.6'
status: mixed
dimension: '[[concepts/replica-topology-and-persistence|Replica Topology and Persistence]]'
accepted_by:
- s01_p09
- s02_p05
- s03_p06
rejected_by:
- s02_p05
- s03_p06
passages: 3
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
merged_from:
- id: '10.9'
  label: Full checksum recomputation
tags:
- value
- mixed
- replica-topology-and-persistence
---

# Incremental replica checksum state

Maintain logical repository-state checksums incrementally rather than recomputing them from all references.

## Evidence

- **s01_p09** (accepts) · [[sources/s1|Git at any scale]] · Spokes and Consistency
  > Another flaw, impossible to see up front, but painfully obvious after having suffered through it, is that Spokes can be \*rough\* to operate at scale. Because the repositories on disk are always the source of truth for consensus, every copy of every repository is \*very important\*. You have to treat repositories as \*pets, not cattle\*. This means, for starters, that …
- **s02_p05** (both) · [[sources/s2|Stretching Spokes]] · Using checksums to compare replicas
  > To summarize the state of a replica, we use a checksum over the list of all of its references and their values, plus a few other things. We call this the “Spokes checksum”. If two replicas have the same Spokes checksums, then they definitely hold the same logical contents. We compute the Spokes checksum for every replica after every update …
- **s03_p06** (both) · [[sources/s3|Building resilience in Spokes]] · Durability
  > If a repository exists on exactly three replicas, then a successful write on two replicas constitutes both a durable set, and a majority. If a repository has four or five replicas, then three are required for a majority. In contrast, many other replication and consensus protocols have a single primary copy at any moment. The order that writes arrive at …

## Merged from

- {'id': '10.9', 'label': 'Full checksum recomputation'}
