---
title: Repository Storage Representation
type: dimension
id: '9'
core: true
values: 18
candidate_values: 17
outcomes: 1
evidence:
  codes: 31
  documents: 12
  sources: 3
relations:
- affects [[concepts/write-commitment-and-consistency|Write Commitment and Consistency]]
tags:
- dimension
- core
systems:
- '[[synthesis/systems/cur-cont|Cursor Continuity and Origin]]'
- '[[synthesis/systems/gh-fs|GitHub filesystem distribution]]'
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
- '[[synthesis/systems/goog-dht|Google JGit on a DHT]]'
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
---

# Repository Storage Representation

Which repository hosting substrate, access form, and Git storage representation is used?

## Values

| Value | Status | Passages |
|---|---|---|
| [[entities/application-layer-over-unmodified-git|Application layer over unmodified Git]] | accepted | 1 |
| [[entities/centralized-repository-hosting|Centralized repository hosting]] | accepted | 3 |
| [[entities/delta-compressed-packfile-storage|Delta-compressed packfile storage]] | accepted | 2 |
| [[entities/filesystem-level-repository-distribution|Filesystem-level repository distribution]] | accepted | 2 |
| [[entities/jgit-repository-storage-abstraction|JGit repository-storage abstraction]] | accepted | 1 |
| [[entities/packfile-size-minimizing-layout|Packfile size-minimizing layout]] | accepted | 1 |
| [[entities/packfile-based-git-networking|Packfile-based Git networking]] | accepted | 3 |
| [[entities/packfile-based-repository-storage|Packfile-based repository storage]] | accepted | 2 |
| [[entities/plain-git-repositories-on-local-nvme|Plain Git repositories on local NVMe]] | accepted | 2 |
| [[entities/single-machine-repository-storage|Single-machine repository storage]] | accepted | 4 |
| [[entities/dht-backed-git-object-storage|DHT-backed Git object storage]] | mixed | 2 |
| [[entities/dedicated-fileserver-repository-hosting|Dedicated fileserver repository hosting]] | mixed | 2 |
| [[entities/git-level-distribution|Git-level distribution]] | mixed | 2 |
| [[entities/nfs-based-centralized-repository-storage|NFS-based centralized repository storage]] | rejected | 1 |
| [[entities/object-level-repository-distribution|Object-level repository distribution]] | rejected | 1 |
| [[entities/repository-data-transformation|Repository-data transformation]] | rejected | 1 |
| [[entities/whole-file-local-repository-caching|Whole-file local repository caching]] | rejected | 1 |
| [[entities/networked-filesystem-repository-access|Networked-filesystem repository access]] | outcome | 1 |

## Relations

How to read them: [[relations|Relations between dimensions]].

### From this dimension

- Choices on this dimension affect the outcomes of [[concepts/write-commitment-and-consistency|Write Commitment and Consistency]]. *Replica count and placement determine whether quorum or synchronous durability requirements can be met and influence capacity and latency.*

### To this dimension

- [[concepts/repository-service-scaling|Repository Service Scaling]] requires this dimension to be decided first. *Synchronized read routing, replica health decisions, and geo-distributed serving depend on knowing replica locations and topology.*
- [[concepts/client-repository-and-working-tree-scaling|Client Repository and Working-Tree Scaling]] requires this dimension to be decided first. *Client clone, index, and maintenance mechanisms depend on the repository representation exposed to clients.*

## Evidence

31 open codes from 12 passages in 3 sources.

**Core dimension:** yes ★ (3 sources, 5 systems; core = ≥ 2 sources or ≥ 2 systems).
