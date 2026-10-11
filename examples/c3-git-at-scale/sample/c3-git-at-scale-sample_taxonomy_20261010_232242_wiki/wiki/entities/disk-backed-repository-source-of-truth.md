---
title: Disk-backed repository source of truth
type: value
id: '10.24'
status: mixed
dimension: '[[concepts/replica-topology-and-persistence|Replica Topology and Persistence]]'
accepted_by:
- s01_p09
rejected_by:
- s01_p11
passages: 2
systems:
- '[[synthesis/systems/cur-cont|Cursor Continuity and Origin]]'
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
tags:
- value
- mixed
- replica-topology-and-persistence
---

# Disk-backed repository source of truth

Repository data on local disks is treated as authoritative state rather than merely a reconstructible cache.

## Evidence

- **s01_p09** (accepts) · [[sources/s1|Git at any scale]] · Spokes and Consistency
  > Another flaw, impossible to see up front, but painfully obvious after having suffered through it, is that Spokes can be \*rough\* to operate at scale. Because the repositories on disk are always the source of truth for consensus, every copy of every repository is \*very important\*. You have to treat repositories as \*pets, not cattle\*. This means, for starters, that …
- **s01_p11** (rejects) · [[sources/s1|Git at any scale]] · Consensus
  > We've seen that one thing that makes a Spokes cluster hard to operate is that it's very important to keep track of the location of every repository on each server. \*Continuity\* does this very differently. Where does every repository live? The answer is "anywhere". It doesn't matter! We treat repositories like a warm cache on disk, but the source of …
