---
type: Design Alternative
title: Durability-gated write acceptance
description: Writes are accepted only after the required number of replicas have synchronously committed them.
id: '30.10'
dimension: /concepts/replica-write-coordination.md
accepted_by:
- s03_p02
- s03_p06
rejected_by: []
passages: 2
systems:
- /synthesis/systems/gh-spokes.md
tags:
- value
- accepted
- replica-write-coordination
stance: accepted
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Durability-gated write acceptance

Writes are accepted only after the required number of replicas have synchronously committed them.

## Evidence

- **s03_p02** (accepts) · [Building resilience in Spokes](/sources/s3.md) · Defining resilience
  > In any system or service, there are two key ways to measure resilience: availability and durability. A system’s availability is the fraction of the time it can provide the service it was designed to provide. Can it serve content? Can it accept writes? Availability can be partial, complete, or degraded: is every repository available? Are some repositories—or whole servers—slow? A …
- **s03_p06** (accepts) · [Building resilience in Spokes](/sources/s3.md) · Durability
  > If a repository exists on exactly three replicas, then a successful write on two replicas constitutes both a durable set, and a majority. If a repository has four or five replicas, then three are required for a majority. In contrast, many other replication and consensus protocols have a single primary copy at any moment. The order that writes arrive at …
