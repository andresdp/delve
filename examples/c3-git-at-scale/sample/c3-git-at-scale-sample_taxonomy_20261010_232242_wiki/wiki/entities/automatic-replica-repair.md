---
title: Automatic replica repair
type: value
id: '6.23'
status: accepted
dimension: '[[concepts/write-commitment-and-consistency|Write Commitment and Consistency]]'
accepted_by:
- s03_p06
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
design_points:
- '[[designs/p024|P024]]'
tags:
- value
- accepted
- write-commitment-and-consistency
---

# Automatic replica repair

Unhealthy or lagging replicas are repaired automatically to restore redundancy and service capacity.

## Evidence

- **s03_p06** (accepts) · [[sources/s3|Building resilience in Spokes]] · Durability
  > If a repository exists on exactly three replicas, then a successful write on two replicas constitutes both a durable set, and a majority. If a repository has four or five replicas, then three are required for a majority. In contrast, many other replication and consensus protocols have a single primary copy at any moment. The order that writes arrive at …

## In design points

[[designs/p024|P024]]
