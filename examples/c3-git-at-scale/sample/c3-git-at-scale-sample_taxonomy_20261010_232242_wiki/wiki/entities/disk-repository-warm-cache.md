---
title: Disk repository warm cache
type: value
id: '10.11'
status: accepted
dimension: '[[concepts/replica-topology-and-persistence|Replica Topology and Persistence]]'
accepted_by:
- s01_p05
- s01_p11
rejected_by: []
passages: 2
systems:
- '[[synthesis/systems/cur-cont|Cursor Continuity and Origin]]'
- '[[synthesis/systems/gh-fs|GitHub filesystem distribution]]'
design_points:
- '[[designs/p005|P005]]'
- '[[designs/p011|P011]]'
tags:
- value
- accepted
- replica-topology-and-persistence
---

# Disk repository warm cache

Local disk repositories serve as reconstructible caches rather than fixed authoritative placement.

## Evidence

- **s01_p05** (accepts) · [[sources/s1|Git at any scale]] · GitHub and filesystems
  > Further attempts were made with (frankly, in retrospect, horrific) technologies that replicated the filesystem at the block level. A short-lived deployment with GFS. A longer-lived deployment based on DRBD. They all hit a wall. They were \*terrible\* to operate day to day, and they didn't make up for it with good performance. It all boils down to the design of …
- **s01_p11** (accepts) · [[sources/s1|Git at any scale]] · Consensus
  > We've seen that one thing that makes a Spokes cluster hard to operate is that it's very important to keep track of the location of every repository on each server. \*Continuity\* does this very differently. Where does every repository live? The answer is "anywhere". It doesn't matter! We treat repositories like a warm cache on disk, but the source of …

## In design points

[[designs/p005|P005]], [[designs/p011|P011]]
