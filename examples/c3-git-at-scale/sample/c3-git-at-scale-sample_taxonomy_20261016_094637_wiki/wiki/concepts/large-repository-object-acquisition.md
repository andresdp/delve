---
type: Design Decision
title: Large-Repository Object Acquisition
description: How clients obtain Git data for very large repositories, contrasting complete transfer with demand-driven, server-assisted acquisition.
id: '6'
core: true
values: 9
candidate_values: 6
outcomes: 3
evidence:
  codes: 23
  documents: 10
  sources: 3
relations: []
tags:
- dimension
- core
exclusivity: 0.33
systems:
- /synthesis/systems/gh-fs.md
- /synthesis/systems/goog-dht.md
- /synthesis/systems/ms-gvfs.md
- /synthesis/systems/ms-scalar.md
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Large-Repository Object Acquisition

How clients obtain Git data for very large repositories, contrasting complete transfer with demand-driven, server-assisted acquisition.

## Values

| Value | Status | Passages |
|---|---|---|
| [GVFS demand-driven transfer](/entities/gvfs-demand-driven-transfer.md) | accepted | 7 |
| [GVFS-style object-download cache servers](/entities/gvfs-style-object-download-cache-servers.md) | accepted | 2 |
| [Partial clone transfer](/entities/partial-clone-transfer.md) | accepted | 3 |
| [GVFS without cache infrastructure](/entities/gvfs-without-cache-infrastructure.md) | mixed | 3 |
| [Packfile-based Git networking](/entities/packfile-based-git-networking.md) | mixed | 4 |
| [Standard-Git GVFS protocol support](/entities/standard-git-gvfs-protocol-support.md) | mixed | 5 |
| [Complete object transfer](/entities/complete-object-transfer.md) | outcome | 1 |
| [Packfile transfer availability limitation](/entities/packfile-transfer-availability-limitation.md) | outcome | 1 |
| [Repository-size threshold for GVFS deployment](/entities/repository-size-threshold-for-gvfs-deployment.md) | outcome | 1 |

## Exclusivity

The values of a dimension are alternatives, so each system should adopt one of them. **1 of 3 systems** adopt one value (or a declared hybrid): exclusivity 0.33.

Values adopted together:

- [GVFS demand-driven transfer](/entities/gvfs-demand-driven-transfer.md) and [Partial clone transfer](/entities/partial-clone-transfer.md): [Microsoft VFS for Git (GVFS)](/synthesis/systems/ms-gvfs.md), [Microsoft Scalar](/synthesis/systems/ms-scalar.md)
- [GVFS demand-driven transfer](/entities/gvfs-demand-driven-transfer.md) and [Standard-Git GVFS protocol support](/entities/standard-git-gvfs-protocol-support.md): [Microsoft VFS for Git (GVFS)](/synthesis/systems/ms-gvfs.md), [Microsoft Scalar](/synthesis/systems/ms-scalar.md)
- [GVFS demand-driven transfer](/entities/gvfs-demand-driven-transfer.md) and [GVFS without cache infrastructure](/entities/gvfs-without-cache-infrastructure.md): [Microsoft VFS for Git (GVFS)](/synthesis/systems/ms-gvfs.md), [Microsoft Scalar](/synthesis/systems/ms-scalar.md)
- [Partial clone transfer](/entities/partial-clone-transfer.md) and [Standard-Git GVFS protocol support](/entities/standard-git-gvfs-protocol-support.md): [Microsoft VFS for Git (GVFS)](/synthesis/systems/ms-gvfs.md), [Microsoft Scalar](/synthesis/systems/ms-scalar.md)
- [Partial clone transfer](/entities/partial-clone-transfer.md) and [GVFS without cache infrastructure](/entities/gvfs-without-cache-infrastructure.md): [Microsoft VFS for Git (GVFS)](/synthesis/systems/ms-gvfs.md), [Microsoft Scalar](/synthesis/systems/ms-scalar.md)
- 10 more pair(s)

*The sources combine this dimension's values in many different ways (few shared combinations): the dimension may group several concerns.*

## Evidence

23 open codes from 10 passages in 3 sources.

**Core dimension:** yes ★ (3 sources, 4 systems; core = ≥ 2 sources or ≥ 2 systems).
