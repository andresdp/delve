---
title: Per-write voting without a primary
type: value
id: '30.5'
status: accepted
dimension: '[[concepts/replica-write-coordination|Replica Write Coordination]]'
accepted_by:
- s03_p06
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
design_points:
- '[[designs/p013|P013]]'
tags:
- value
- accepted
- replica-write-coordination
---

# Per-write voting without a primary

Each write directly determines its winning order and outcome rather than following a primary's global ordering.

## Evidence

- **s03_p06** (accepts) · [[sources/s3|Building resilience in Spokes]] · Durability
  > If a repository exists on exactly three replicas, then a successful write on two replicas constitutes both a durable set, and a majority. If a repository has four or five replicas, then three are required for a majority. In contrast, many other replication and consensus protocols have a single primary copy at any moment. The order that writes arrive at …

## In design points

[[designs/p013|P013]]
