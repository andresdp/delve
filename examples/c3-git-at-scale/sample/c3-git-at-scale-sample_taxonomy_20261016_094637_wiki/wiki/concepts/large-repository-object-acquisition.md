---
title: Large-Repository Object Acquisition
type: dimension
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
- '[[synthesis/systems/gh-fs|GitHub filesystem distribution]]'
- '[[synthesis/systems/goog-dht|Google JGit on a DHT]]'
- '[[synthesis/systems/ms-gvfs|Microsoft VFS for Git (GVFS)]]'
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
---

# Large-Repository Object Acquisition

How clients obtain Git data for very large repositories, contrasting complete transfer with demand-driven, server-assisted acquisition.

## Values

| Value | Status | Passages |
|---|---|---|
| [[entities/gvfs-demand-driven-transfer|GVFS demand-driven transfer]] | accepted | 7 |
| [[entities/gvfs-style-object-download-cache-servers|GVFS-style object-download cache servers]] | accepted | 2 |
| [[entities/partial-clone-transfer|Partial clone transfer]] | accepted | 3 |
| [[entities/gvfs-without-cache-infrastructure|GVFS without cache infrastructure]] | mixed | 3 |
| [[entities/packfile-based-git-networking|Packfile-based Git networking]] | mixed | 4 |
| [[entities/standard-git-gvfs-protocol-support|Standard-Git GVFS protocol support]] | mixed | 5 |
| [[entities/complete-object-transfer|Complete object transfer]] | outcome | 1 |
| [[entities/packfile-transfer-availability-limitation|Packfile transfer availability limitation]] | outcome | 1 |
| [[entities/repository-size-threshold-for-gvfs-deployment|Repository-size threshold for GVFS deployment]] | outcome | 1 |

## Exclusivity

The values of a dimension are alternatives, so each system should adopt one of them. **1 of 3 systems** adopt one value (or a declared hybrid): exclusivity 0.33.

Values adopted together:

- [[entities/gvfs-demand-driven-transfer|GVFS demand-driven transfer]] and [[entities/partial-clone-transfer|Partial clone transfer]]: [[synthesis/systems/ms-gvfs|Microsoft VFS for Git (GVFS)]], [[synthesis/systems/ms-scalar|Microsoft Scalar]]
- [[entities/gvfs-demand-driven-transfer|GVFS demand-driven transfer]] and [[entities/standard-git-gvfs-protocol-support|Standard-Git GVFS protocol support]]: [[synthesis/systems/ms-gvfs|Microsoft VFS for Git (GVFS)]], [[synthesis/systems/ms-scalar|Microsoft Scalar]]
- [[entities/gvfs-demand-driven-transfer|GVFS demand-driven transfer]] and [[entities/gvfs-without-cache-infrastructure|GVFS without cache infrastructure]]: [[synthesis/systems/ms-gvfs|Microsoft VFS for Git (GVFS)]], [[synthesis/systems/ms-scalar|Microsoft Scalar]]
- [[entities/partial-clone-transfer|Partial clone transfer]] and [[entities/standard-git-gvfs-protocol-support|Standard-Git GVFS protocol support]]: [[synthesis/systems/ms-gvfs|Microsoft VFS for Git (GVFS)]], [[synthesis/systems/ms-scalar|Microsoft Scalar]]
- [[entities/partial-clone-transfer|Partial clone transfer]] and [[entities/gvfs-without-cache-infrastructure|GVFS without cache infrastructure]]: [[synthesis/systems/ms-gvfs|Microsoft VFS for Git (GVFS)]], [[synthesis/systems/ms-scalar|Microsoft Scalar]]
- 10 more pair(s)

*The sources combine this dimension's values in many different ways (few shared combinations): the dimension may group several concerns.*

## Evidence

23 open codes from 10 passages in 3 sources.

**Core dimension:** yes ★ (3 sources, 4 systems; core = ≥ 2 sources or ≥ 2 systems).
