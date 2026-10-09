---
title: Majority-based write acceptance
type: value
id: '2.10'
status: accepted
dimension: '[[concepts/write-coordination-and-replica-consistency|Write Coordination and Replica Consistency]]'
accepted_by:
- s01_p07
- s03_p02
- s03_p05
- s03_p06
- s03_p09
rejected_by: []
passages: 5
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
tags:
- value
- accepted
- write-coordination-and-replica-consistency
---

# Majority-based write acceptance

Considering a write durable or a push acceptable only after acknowledgement by a replica majority.

## Evidence

- **s01_p07** (accepts) · [[sources/s1|Git at any scale]] · Spokes and Consistency
  > Spokes is a \*consensus-based\* distributed system. It works by storing several copies of your Git repository on different servers. Whenever you push new data, an orchestrator fans out your push so that every instance of your repository receives a copy. The "fan-out" is synchronized with a classic consensus algorithm called 3PC (three-phase commit) so that a push is only accepted …
- **s03_p02** (accepts) · [[sources/s3|Building resilience in Spokes]] · Defining resilience
  > In any system or service, there are two key ways to measure resilience: availability and durability. A system’s availability is the fraction of the time it can provide the service it was designed to provide. Can it serve content? Can it accept writes? Availability can be partial, complete, or degraded: is every repository available? Are some repositories—or whole servers—slow? A …
- **s03_p05** (accepts) · [[sources/s3|Building resilience in Spokes]] · Availability
  > The figure below illustrates the MxN nature of failure detection and shows in red which failure detectors are true if a single file server, \`dfs4\`, is offline. In one recent incident, a single front-end application server in a staging environment lost its ability to resolve the DNS names of the file servers. Because it couldn’t reach the file servers to …
- **s03_p06** (accepts) · [[sources/s3|Building resilience in Spokes]] · Durability
  > If a repository exists on exactly three replicas, then a successful write on two replicas constitutes both a durable set, and a majority. If a repository has four or five replicas, then three are required for a majority. In contrast, many other replication and consensus protocols have a single primary copy at any moment. The order that writes arrive at …
- **s03_p09** (accepts) · [[sources/s3|Building resilience in Spokes]] · Clean shutdowns
  > So instead, we prepare a server for retirement by removing it from the count of active replicas for any repository. Spokes can still use that server for both read and write operations. But when it asks if all repositories have enough replicas, suddenly some of them—the ones on the retiring server—will say no, and more replicas will be created. These …
