---
title: Unhealthy-replica isolation
type: value
id: '3.10'
status: accepted
dimension: '[[concepts/replica-failure-repair-and-failover|Replica Failure Repair and Failover]]'
accepted_by:
- s03_p06
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
tags:
- value
- accepted
- replica-failure-repair-and-failover
---

# Unhealthy-replica isolation

Excluding replicas that lose a write vote from reads and writes until they are repaired.

## Evidence

- **s03_p06** (accepts) · [[sources/s3|Building resilience in Spokes]] · Durability
  > If a repository exists on exactly three replicas, then a successful write on two replicas constitutes both a durable set, and a majority. If a repository has four or five replicas, then three are required for a majority. In contrast, many other replication and consensus protocols have a single primary copy at any moment. The order that writes arrive at …
