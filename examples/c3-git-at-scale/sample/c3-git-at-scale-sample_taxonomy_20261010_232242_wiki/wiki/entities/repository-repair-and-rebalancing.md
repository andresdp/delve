---
title: Repository repair and rebalancing
type: value
id: '10.23'
status: accepted
dimension: '[[concepts/replica-topology-and-persistence|Replica Topology and Persistence]]'
accepted_by:
- s03_p01
- s03_p09
rejected_by: []
passages: 2
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
tags:
- value
- accepted
- replica-topology-and-persistence
---

# Repository repair and rebalancing

Repairing and redistributing repository copies as servers and networks fail or topology changes.

## Evidence

- **s03_p01** (accepts) · [[sources/s3|Building resilience in Spokes]] · Building resilience in Spokes
  > Spokes is the replication system for the file servers where we store over 38 million Git repositories and over 36 million gists.It keeps at least three copies of every repository… Spokes is the replication system for the file servers where we store over 38 million Git repositories and over 36 million gists.It keeps at least three copies of every repository …
- **s03_p09** (accepts) · [[sources/s3|Building resilience in Spokes]] · Clean shutdowns
  > So instead, we prepare a server for retirement by removing it from the count of active replicas for any repository. Spokes can still use that server for both read and write operations. But when it asks if all repositories have enough replicas, suddenly some of them—the ones on the retiring server—will say no, and more replicas will be created. These …
