---
title: Google JGit on a DHT
type: system
code: GOOG-DHT
organization: Google
dimensions: 3
tags:
- system
---

# Google JGit on a DHT

JGit with repository objects stored in a distributed hash table.

Values supported by passages whose primary system is `GOOG-DHT` (passage → system map).

| Dimension | Values (passages) |
|---|---|
| [[concepts/client-repository-workload-scaling|Client Repository Workload Scaling]] | • [[entities/dag-dependent-repository-traversal|DAG-dependent repository traversal]] (1) |
| [[concepts/git-hosting-and-acceleration-integration|Git Hosting and Acceleration Integration]] | • [[entities/gvfs-protocol-support-in-scalar|GVFS protocol support in Scalar]] (1)<br>• [[entities/jgit-repository-abstraction-for-distributed-storage|JGit repository abstraction for distributed storage]] (1)<br>• [[entities/packfile-based-git-network-transfer|Packfile-based Git network transfer]] (1) |
| [[concepts/write-coordination-and-replica-consistency|Write Coordination and Replica Consistency]] | • [[entities/distributed-object-level-git-storage|Distributed object-level Git storage]] (1) |

## Attested design points

[[designs/p016|P016]]
