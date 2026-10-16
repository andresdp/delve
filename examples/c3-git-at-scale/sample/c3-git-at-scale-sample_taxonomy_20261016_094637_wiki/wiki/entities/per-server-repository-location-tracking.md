---
type: Design Alternative
title: Per-server repository location tracking
description: The system tracks repository placement on every server as authoritative routing state.
id: '13.3'
dimension: /concepts/repository-placement-and-read-routing.md
accepted_by: []
rejected_by:
- s01_p11
passages: 1
systems:
- /synthesis/systems/cur-cont.md
design_points:
- /designs/p013.md
tags:
- value
- rejected
- repository-placement-and-read-routing
stance: rejected
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Per-server repository location tracking

The system tracks repository placement on every server as authoritative routing state.

## Evidence

- **s01_p11** (rejects) · [Git at any scale](/sources/s1.md) · Consensus
  > We've seen that one thing that makes a Spokes cluster hard to operate is that it's very important to keep track of the location of every repository on each server. \*Continuity\* does this very differently. Where does every repository live? The answer is "anywhere". It doesn't matter! We treat repositories like a warm cache on disk, but the source of …

## In design points

[P013](/designs/p013.md)
