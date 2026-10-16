---
title: Stateless repository placement
type: value
id: '13.1'
status: accepted
dimension: '[[concepts/repository-placement-and-read-routing|Repository Placement and Read Routing]]'
accepted_by:
- s01_p11
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/cur-cont|Cursor Continuity and Origin]]'
design_points:
- '[[designs/p001|P001]]'
- '[[designs/p007|P007]]'
- '[[designs/p014|P014]]'
tags:
- value
- accepted
- repository-placement-and-read-routing
---

# Stateless repository placement

Any healthy server can materialize repository state without authoritative per-repository placement records.

## Evidence

- **s01_p11** (accepts) · [[sources/s1|Git at any scale]] · Consensus
  > We've seen that one thing that makes a Spokes cluster hard to operate is that it's very important to keep track of the location of every repository on each server. \*Continuity\* does this very differently. Where does every repository live? The answer is "anywhere". It doesn't matter! We treat repositories like a warm cache on disk, but the source of …

## In design points

[[designs/p001|P001]], [[designs/p007|P007]], [[designs/p014|P014]]
