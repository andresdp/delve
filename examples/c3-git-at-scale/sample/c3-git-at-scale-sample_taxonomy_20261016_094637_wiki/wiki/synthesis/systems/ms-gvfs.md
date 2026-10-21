---
type: System
title: Microsoft VFS for Git (GVFS)
description: Virtualized filesystem on the client and the GVFS protocol with cache servers.
code: MS-GVFS
organization: Microsoft
dimensions: 1
tags:
- system
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Microsoft VFS for Git (GVFS)

Virtualized filesystem on the client and the GVFS protocol with cache servers.

Values adopted by passages whose primary system is `MS-GVFS` (passage → system map), and the alternatives they considered and rejected. ⚠ marks a dimension where the system adopts several values: values of a dimension should be alternatives.

| Dimension | Adopted (passages) | Considered and rejected |
|---|---|---|
| [Large-Repository Object Acquisition](/concepts/large-repository-object-acquisition.md) ⚠ | • [GVFS demand-driven transfer](/entities/gvfs-demand-driven-transfer.md) (1)<br>• [GVFS without cache infrastructure](/entities/gvfs-without-cache-infrastructure.md) (1)<br>• [Partial clone transfer](/entities/partial-clone-transfer.md) (1)<br>• [Standard-Git GVFS protocol support](/entities/standard-git-gvfs-protocol-support.md) (1) |  |
