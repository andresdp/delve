---
type: Outcome
title: Idle-replica resource overhead
description: A fixed replica floor consumes substantial resources on numerous small or inactive repositories.
id: '21.3'
dimension: /concepts/replica-topology.md
accepted_by: []
rejected_by: []
passages: 3
systems:
- /synthesis/systems/gh-spokes.md
tags:
- value
- outcome
- replica-topology
stance: outcome
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Idle-replica resource overhead

A fixed replica floor consumes substantial resources on numerous small or inactive repositories.

## Evidence

- **s01_p08** (supports) · [Git at any scale](/sources/s1.md) · Spokes and Consistency
  > This is essentially how Spokes works, and it has been working quite well for the past 13 years. Of course, Spokes is not perfect — no system is. In 2026, the way people use Git repositories has changed drastically, and we have learned many important lessons about building distributed systems along the way. Time and experience have shown which of …
- **s03_p06** (supports) · [Building resilience in Spokes](/sources/s3.md) · Durability
  > If a repository exists on exactly three replicas, then a successful write on two replicas constitutes both a durable set, and a majority. If a repository has four or five replicas, then three are required for a majority. In contrast, many other replication and consensus protocols have a single primary copy at any moment. The order that writes arrive at …
- **s03_p09** (supports) · [Building resilience in Spokes](/sources/s3.md) · Clean shutdowns
  > So instead, we prepare a server for retirement by removing it from the count of active replicas for any repository. Spokes can still use that server for both read and write operations. But when it asks if all repositories have enough replicas, suddenly some of them—the ones on the retiring server—will say no, and more replicas will be created. These …
