---
title: Write-ahead-log repository persistence
type: value
id: '10.4'
status: accepted
dimension: '[[concepts/replica-topology-and-persistence|Replica Topology and Persistence]]'
accepted_by:
- s01_p10
- s01_p11
- s01_p15
rejected_by: []
passages: 3
systems:
- '[[synthesis/systems/cur-cont|Cursor Continuity and Origin]]'
tags:
- value
- accepted
- replica-topology-and-persistence
---

# Write-ahead-log repository persistence

Authoritative repository state and provenance persist in a durable write-ahead log rather than fixed host placement.

## Evidence

- **s01_p10** (accepts) · [[sources/s1|Git at any scale]] · Continuity
  > Continuity is the Git storage system we've developed at Cursor, with a very clear approach: learning from everything that Spokes did well, and fixing the things that, after many years, we now know are problems. \*Continuity\* is a simple system (a system cannot be easy to operate if it is not simple). The core primitive behind it is a write-ahead …
- **s01_p11** (accepts) · [[sources/s1|Git at any scale]] · Consensus
  > We've seen that one thing that makes a Spokes cluster hard to operate is that it's very important to keep track of the location of every repository on each server. \*Continuity\* does this very differently. Where does every repository live? The answer is "anywhere". It doesn't matter! We treat repositories like a warm cache on disk, but the source of …
- **s01_p15** (accepts) · [[sources/s1|Git at any scale]] · WAL as truth
  > S3 is a great piece of technology. The whole concept of blob storage that was pioneered with the S3 API has turned out to be a very powerful building block for large data storage systems, and this most definitely also applies to hosting Git repositories. The design presented here is novel on many ways, but it's not the first one …
