---
title: Per-write voting protocol
type: value
id: '2.11'
status: accepted
dimension: '[[concepts/write-coordination-and-replica-consistency|Write Coordination and Replica Consistency]]'
accepted_by:
- s03_p06
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
design_points:
- '[[designs/p011|P011]]'
tags:
- value
- accepted
- write-coordination-and-replica-consistency
---

# Per-write voting protocol

Selecting each write’s order and outcome through voting rather than through a permanently designated primary.

## Evidence

- **s03_p06** (accepts) · [[sources/s3|Building resilience in Spokes]] · Durability
  > If a repository exists on exactly three replicas, then a successful write on two replicas constitutes both a durable set, and a majority. If a repository has four or five replicas, then three are required for a majority. In contrast, many other replication and consensus protocols have a single primary copy at any moment. The order that writes arrive at …

## In design points

[[designs/p011|P011]]
