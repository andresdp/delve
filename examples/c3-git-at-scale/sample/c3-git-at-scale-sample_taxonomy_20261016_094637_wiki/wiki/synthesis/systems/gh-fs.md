---
title: GitHub filesystem distribution
type: system
code: GH-FS
organization: GitHub
dimensions: 0
tags:
- system
---

# GitHub filesystem distribution

GitHub before Spokes: NFS, GFS and DRBD filesystem distribution, then single-copy RPC fileservers.

Values adopted by passages whose primary system is `GH-FS` (passage → system map), and the alternatives they considered and rejected. ⚠ marks a dimension where the system adopts several values: values of a dimension should be alternatives.

| Dimension | Adopted (passages) | Considered and rejected |
|---|---|---|
| [[concepts/large-repository-object-acquisition|Large-Repository Object Acquisition]] |  | • [[entities/gvfs-without-cache-infrastructure|GVFS without cache infrastructure]] (1)<br>• [[entities/packfile-based-git-networking|Packfile-based Git networking]] (1) |
| [[concepts/replica-synchronization-mechanism|Replica Synchronization Mechanism]] |  | • [[entities/drbd-block-level-replication|DRBD block-level replication]] (1) |
| [[concepts/repository-placement-and-read-routing|Repository Placement and Read Routing]] |  | • [[entities/external-routing-database-placement|External routing-database placement]] (1) |
