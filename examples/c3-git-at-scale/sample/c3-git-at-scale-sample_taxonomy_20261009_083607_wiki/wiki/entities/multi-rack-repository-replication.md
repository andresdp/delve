---
title: Multi-rack repository replication
type: value
id: '1.9'
status: accepted
dimension: '[[concepts/repository-replica-placement|Repository Replica Placement]]'
accepted_by:
- s03_p05
- s03_p09
rejected_by: []
passages: 2
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
design_points:
- '[[designs/p013|P013]]'
- '[[designs/p014|P014]]'
- '[[designs/p017|P017]]'
tags:
- value
- accepted
- repository-replica-placement
---

# Multi-rack repository replication

Replicating repositories across distinct racks to tolerate rack-level failures.

## Evidence

- **s03_p05** (accepts) · [[sources/s3|Building resilience in Spokes]] · Availability
  > The figure below illustrates the MxN nature of failure detection and shows in red which failure detectors are true if a single file server, \`dfs4\`, is offline. In one recent incident, a single front-end application server in a staging environment lost its ability to resolve the DNS names of the file servers. Because it couldn’t reach the file servers to …
- **s03_p09** (accepts) · [[sources/s3|Building resilience in Spokes]] · Clean shutdowns
  > So instead, we prepare a server for retirement by removing it from the count of active replicas for any repository. Spokes can still use that server for both read and write operations. But when it asks if all repositories have enough replicas, suddenly some of them—the ones on the retiring server—will say no, and more replicas will be created. These …

## In design points

[[designs/p013|P013]], [[designs/p014|P014]], [[designs/p017|P017]]
