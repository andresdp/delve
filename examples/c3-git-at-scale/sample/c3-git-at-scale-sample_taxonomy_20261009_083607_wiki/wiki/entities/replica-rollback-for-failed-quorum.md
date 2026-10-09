---
title: Replica rollback for failed quorum
type: value
id: '2.12'
status: accepted
dimension: '[[concepts/write-coordination-and-replica-consistency|Write Coordination and Replica Consistency]]'
accepted_by:
- s02_p04
- s03_p06
rejected_by: []
passages: 2
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
tags:
- value
- accepted
- write-coordination-and-replica-consistency
---

# Replica rollback for failed quorum

Reverting writes that were not identically applied at a majority of replicas.

## Evidence

- **s02_p04** (accepts) · [[sources/s2|Stretching Spokes]] · Git reference update transactions
  > Three-phase commit is a core part of keeping the replicas in sync. Implementing it requires each of the replicas to be able to answer the question “can you carry out the following reference updates?”, and then to either commit or roll back the transaction based on the coordinator’s instructions. To make this possible, we implemented transactions for Git reference updates …
- **s03_p06** (accepts) · [[sources/s3|Building resilience in Spokes]] · Durability
  > If a repository exists on exactly three replicas, then a successful write on two replicas constitutes both a durable set, and a majority. If a repository has four or five replicas, then three are required for a majority. In contrast, many other replication and consensus protocols have a single primary copy at any moment. The order that writes arrive at …
