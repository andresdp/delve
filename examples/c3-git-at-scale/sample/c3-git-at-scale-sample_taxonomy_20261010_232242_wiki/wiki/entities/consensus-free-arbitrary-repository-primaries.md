---
title: Consensus-free arbitrary repository primaries
type: value
id: '6.13'
status: accepted
dimension: '[[concepts/write-commitment-and-consistency|Write Commitment and Consistency]]'
accepted_by:
- s01_p11
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/cur-cont|Cursor Continuity and Origin]]'
design_points:
- '[[designs/p013|P013]]'
- '[[designs/p018|P018]]'
tags:
- value
- accepted
- write-commitment-and-consistency
---

# Consensus-free arbitrary repository primaries

Any healthy server may accept a push without election because durable compare-and-swap synchronization makes concurrent updates safe.

## Evidence

- **s01_p11** (accepts) · [[sources/s1|Git at any scale]] · Consensus
  > We've seen that one thing that makes a Spokes cluster hard to operate is that it's very important to keep track of the location of every repository on each server. \*Continuity\* does this very differently. Where does every repository live? The answer is "anywhere". It doesn't matter! We treat repositories like a warm cache on disk, but the source of …

## In design points

[[designs/p013|P013]], [[designs/p018|P018]]
