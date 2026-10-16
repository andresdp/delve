---
title: Stale-routing recovery
type: value
id: '13.5'
status: accepted
dimension: '[[concepts/repository-placement-and-read-routing|Repository Placement and Read Routing]]'
accepted_by:
- s01_p11
- s03_p04
rejected_by: []
passages: 2
systems:
- '[[synthesis/systems/cur-cont|Cursor Continuity and Origin]]'
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
design_points:
- '[[designs/p023|P023]]'
tags:
- value
- accepted
- repository-placement-and-read-routing
---

# Stale-routing recovery

Routing may be stale after failures, and the system restores service by materializing repository state on a newly selected server.

## Evidence

- **s01_p11** (accepts) · [[sources/s1|Git at any scale]] · Consensus
  > We've seen that one thing that makes a Spokes cluster hard to operate is that it's very important to keep track of the location of every repository on each server. \*Continuity\* does this very differently. Where does every repository live? The answer is "anywhere". It doesn't matter! We treat repositories like a warm cache on disk, but the source of …
- **s03_p04** (accepts) · [[sources/s3|Building resilience in Spokes]] · Availability
  > Spokes uses heartbeats, too, but not as the primary failure-detection mechanism. Instead, heartbeats have two purposes: polling system load and providing the all-clear signal after a node has been marked as offline. As soon as a heartbeat succeeds, the node is marked as online again. If the heartbeat succeeds despite ongoing server problems (retrieving system load is almost a no-op), …

## In design points

[[designs/p023|P023]]
