---
type: System
title: GitHub filesystem distribution
description: 'GitHub before Spokes: NFS, GFS and DRBD filesystem distribution, then single-copy RPC fileservers.'
code: GH-FS
organization: GitHub
dimensions: 0
tags:
- system
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# GitHub filesystem distribution

GitHub before Spokes: NFS, GFS and DRBD filesystem distribution, then single-copy RPC fileservers.

Values adopted by passages whose primary system is `GH-FS` (passage → system map), and the alternatives they considered and rejected. ⚠ marks a dimension where the system adopts several values: values of a dimension should be alternatives.

| Dimension | Adopted (passages) | Considered and rejected |
|---|---|---|
| [Large-Repository Object Acquisition](/concepts/large-repository-object-acquisition.md) |  | • [GVFS without cache infrastructure](/entities/gvfs-without-cache-infrastructure.md) (1)<br>• [Packfile-based Git networking](/entities/packfile-based-git-networking.md) (1) |
| [Replica Synchronization Mechanism](/concepts/replica-synchronization-mechanism.md) |  | • [DRBD block-level replication](/entities/drbd-block-level-replication.md) (1) |
| [Repository Placement and Read Routing](/concepts/repository-placement-and-read-routing.md) |  | • [External routing-database placement](/entities/external-routing-database-placement.md) (1) |
