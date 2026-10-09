---
title: Single-primary write ordering
type: value
id: '2.13'
status: rejected
dimension: '[[concepts/write-coordination-and-replica-consistency|Write Coordination and Replica Consistency]]'
accepted_by: []
rejected_by:
- s03_p06
passages: 1
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
tags:
- value
- rejected
- write-coordination-and-replica-consistency
---

# Single-primary write ordering

Using one elected primary whose arrival order determines authoritative write ordering.

## Evidence

- **s03_p06** (rejects) · [[sources/s3|Building resilience in Spokes]] · Durability
  > If a repository exists on exactly three replicas, then a successful write on two replicas constitutes both a durable set, and a majority. If a repository has four or five replicas, then three are required for a majority. In contrast, many other replication and consensus protocols have a single primary copy at any moment. The order that writes arrive at …
