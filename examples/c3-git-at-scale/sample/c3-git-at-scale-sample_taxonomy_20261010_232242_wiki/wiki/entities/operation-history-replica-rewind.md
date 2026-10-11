---
title: Operation-history replica rewind
type: value
id: '6.8'
status: accepted
dimension: '[[concepts/write-commitment-and-consistency|Write Commitment and Consistency]]'
accepted_by:
- s01_p11
- s01_p15
rejected_by: []
passages: 2
systems:
- '[[synthesis/systems/cur-cont|Cursor Continuity and Origin]]'
tags:
- value
- accepted
- write-commitment-and-consistency
---

# Operation-history replica rewind

Use recorded repository operations to rewind and fast-forward replicas without synchronizing through an external object or reference database.

## Evidence

- **s01_p11** (accepts) · [[sources/s1|Git at any scale]] · Consensus
  > We've seen that one thing that makes a Spokes cluster hard to operate is that it's very important to keep track of the location of every repository on each server. \*Continuity\* does this very differently. Where does every repository live? The answer is "anywhere". It doesn't matter! We treat repositories like a warm cache on disk, but the source of …
- **s01_p15** (accepts) · [[sources/s1|Git at any scale]] · WAL as truth
  > S3 is a great piece of technology. The whole concept of blob storage that was pioneered with the S3 API has turned out to be a very powerful building block for large data storage systems, and this most definitely also applies to hosting Git repositories. The design presented here is novel on many ways, but it's not the first one …
