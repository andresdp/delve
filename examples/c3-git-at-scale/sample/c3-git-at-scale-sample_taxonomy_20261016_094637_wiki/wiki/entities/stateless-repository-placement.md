---
type: Design Alternative
title: Stateless repository placement
description: Any healthy server can materialize repository state without authoritative per-repository placement records.
id: '13.1'
dimension: /concepts/repository-placement-and-read-routing.md
accepted_by:
- s01_p11
rejected_by: []
passages: 1
systems:
- /synthesis/systems/cur-cont.md
design_points:
- /designs/p001.md
- /designs/p007.md
- /designs/p014.md
tags:
- value
- accepted
- repository-placement-and-read-routing
stance: accepted
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Stateless repository placement

Any healthy server can materialize repository state without authoritative per-repository placement records.

## Evidence

- **s01_p11** (accepts) · [Git at any scale](/sources/s1.md) · Consensus
  > We've seen that one thing that makes a Spokes cluster hard to operate is that it's very important to keep track of the location of every repository on each server. \*Continuity\* does this very differently. Where does every repository live? The answer is "anywhere". It doesn't matter! We treat repositories like a warm cache on disk, but the source of …

## In design points

[P001](/designs/p001.md), [P007](/designs/p007.md), [P014](/designs/p014.md)
