---
title: Per-server repository location tracking
type: value
id: '13.3'
status: rejected
dimension: '[[concepts/repository-placement-and-read-routing|Repository Placement and Read Routing]]'
accepted_by: []
rejected_by:
- s01_p11
passages: 1
systems:
- '[[synthesis/systems/cur-cont|Cursor Continuity and Origin]]'
design_points:
- '[[designs/p013|P013]]'
tags:
- value
- rejected
- repository-placement-and-read-routing
---

# Per-server repository location tracking

The system tracks repository placement on every server as authoritative routing state.

## Evidence

- **s01_p11** (rejects) · [[sources/s1|Git at any scale]] · Consensus
  > We've seen that one thing that makes a Spokes cluster hard to operate is that it's very important to keep track of the location of every repository on each server. \*Continuity\* does this very differently. Where does every repository live? The answer is "anywhere". It doesn't matter! We treat repositories like a warm cache on disk, but the source of …

## In design points

[[designs/p013|P013]]
