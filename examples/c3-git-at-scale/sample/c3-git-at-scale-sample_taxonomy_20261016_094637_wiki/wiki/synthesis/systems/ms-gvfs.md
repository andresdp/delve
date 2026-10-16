---
title: Microsoft VFS for Git (GVFS)
type: system
code: MS-GVFS
organization: Microsoft
dimensions: 1
tags:
- system
---

# Microsoft VFS for Git (GVFS)

Virtualized filesystem on the client and the GVFS protocol with cache servers.

Values adopted by passages whose primary system is `MS-GVFS` (passage → system map), and the alternatives they considered and rejected. ⚠ marks a dimension where the system adopts several values: values of a dimension should be alternatives.

| Dimension | Adopted (passages) | Considered and rejected |
|---|---|---|
| [[concepts/large-repository-object-acquisition|Large-Repository Object Acquisition]] ⚠ | • [[entities/gvfs-demand-driven-transfer|GVFS demand-driven transfer]] (1)<br>• [[entities/gvfs-without-cache-infrastructure|GVFS without cache infrastructure]] (1)<br>• [[entities/partial-clone-transfer|Partial clone transfer]] (1)<br>• [[entities/standard-git-gvfs-protocol-support|Standard-Git GVFS protocol support]] (1) |  |
