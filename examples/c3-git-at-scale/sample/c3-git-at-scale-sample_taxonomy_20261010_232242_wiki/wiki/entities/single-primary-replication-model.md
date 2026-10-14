---
title: Single-primary replication model
type: value
id: '6.11'
status: rejected
dimension: '[[concepts/write-commitment-and-consistency|Write Commitment and Consistency]]'
accepted_by: []
rejected_by:
- s03_p06
passages: 1
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
tags:
- value
- rejected
- write-commitment-and-consistency
---

# Single-primary replication model

One elected primary copy determines authoritative write-arrival order for all replicas.

## Evidence

- **s03_p06** (rejects) · [[sources/s3|Building resilience in Spokes]] · Durability
  > If a repository exists on exactly three replicas, then a successful write on two replicas constitutes both a durable set, and a majority. If a repository has four or five replicas, then three are required for a majority. In contrast, many other replication and consensus protocols have a single primary copy at any moment. The order that writes arrive at …
