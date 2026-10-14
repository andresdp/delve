---
title: Compare-and-swap retry delay
type: value
id: '6.35'
status: outcome
dimension: '[[concepts/write-commitment-and-consistency|Write Commitment and Consistency]]'
accepted_by: []
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/cur-cont|Cursor Continuity and Origin]]'
tags:
- value
- outcome
- write-commitment-and-consistency
---

# Compare-and-swap retry delay

Competing durable compare-and-swap updates can delay pushes when arbitrary hosts concurrently act as primaries.

## Evidence

- **s01_p11** (supports) · [[sources/s1|Git at any scale]] · Consensus
  > We've seen that one thing that makes a Spokes cluster hard to operate is that it's very important to keep track of the location of every repository on each server. \*Continuity\* does this very differently. Where does every repository live? The answer is "anywhere". It doesn't matter! We treat repositories like a warm cache on disk, but the source of …
