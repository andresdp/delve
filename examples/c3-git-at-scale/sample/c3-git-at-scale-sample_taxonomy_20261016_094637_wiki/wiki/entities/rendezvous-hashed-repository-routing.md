---
type: Design Alternative
title: Rendezvous-hashed repository routing
description: Repository IDs are mapped to expected healthy servers using rendezvous hashing, with placement adjusted as membership changes.
id: '13.4'
dimension: /concepts/repository-placement-and-read-routing.md
accepted_by:
- s01_p11
- s03_p04
rejected_by: []
passages: 2
systems:
- /synthesis/systems/cur-cont.md
- /synthesis/systems/gh-spokes.md
design_points:
- /designs/p010.md
tags:
- value
- accepted
- repository-placement-and-read-routing
stance: accepted
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Rendezvous-hashed repository routing

Repository IDs are mapped to expected healthy servers using rendezvous hashing, with placement adjusted as membership changes.

## Evidence

- **s01_p11** (accepts) · [Git at any scale](/sources/s1.md) · Consensus
  > We've seen that one thing that makes a Spokes cluster hard to operate is that it's very important to keep track of the location of every repository on each server. \*Continuity\* does this very differently. Where does every repository live? The answer is "anywhere". It doesn't matter! We treat repositories like a warm cache on disk, but the source of …
- **s03_p04** (accepts) · [Building resilience in Spokes](/sources/s3.md) · Availability
  > Spokes uses heartbeats, too, but not as the primary failure-detection mechanism. Instead, heartbeats have two purposes: polling system load and providing the all-clear signal after a node has been marked as offline. As soon as a heartbeat succeeds, the node is marked as online again. If the heartbeat succeeds despite ongoing server problems (retrieving system load is almost a no-op), …

## In design points

[P010](/designs/p010.md)
