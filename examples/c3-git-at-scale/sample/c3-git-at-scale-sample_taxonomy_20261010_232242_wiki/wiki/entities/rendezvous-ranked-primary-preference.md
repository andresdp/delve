---
title: Rendezvous-ranked primary preference
type: value
id: '6.14'
status: accepted
dimension: '[[concepts/write-commitment-and-consistency|Write Commitment and Consistency]]'
accepted_by:
- s01_p11
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/cur-cont|Cursor Continuity and Origin]]'
tags:
- value
- accepted
- write-commitment-and-consistency
---

# Rendezvous-ranked primary preference

The highest-ranked healthy host is preferred to reduce compare-and-swap retries while other hosts remain valid.

## Evidence

- **s01_p11** (accepts) · [[sources/s1|Git at any scale]] · Consensus
  > We've seen that one thing that makes a Spokes cluster hard to operate is that it's very important to keep track of the location of every repository on each server. \*Continuity\* does this very differently. Where does every repository live? The answer is "anywhere". It doesn't matter! We treat repositories like a warm cache on disk, but the source of …
