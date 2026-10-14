---
title: Relational reference database persistence
type: value
id: '10.5'
status: rejected
dimension: '[[concepts/replica-topology-and-persistence|Replica Topology and Persistence]]'
accepted_by: []
rejected_by:
- s01_p11
- s01_p15
passages: 2
systems:
- '[[synthesis/systems/cur-cont|Cursor Continuity and Origin]]'
tags:
- value
- rejected
- replica-topology-and-persistence
---

# Relational reference database persistence

Store repository references in an external relational database alongside blob or packfile storage.

## Evidence

- **s01_p11** (rejects) · [[sources/s1|Git at any scale]] · Consensus
  > We've seen that one thing that makes a Spokes cluster hard to operate is that it's very important to keep track of the location of every repository on each server. \*Continuity\* does this very differently. Where does every repository live? The answer is "anywhere". It doesn't matter! We treat repositories like a warm cache on disk, but the source of …
- **s01_p15** (rejects) · [[sources/s1|Git at any scale]] · WAL as truth
  > S3 is a great piece of technology. The whole concept of blob storage that was pioneered with the S3 API has turned out to be a very powerful building block for large data storage systems, and this most definitely also applies to hosting Git repositories. The design presented here is novel on many ways, but it's not the first one …
