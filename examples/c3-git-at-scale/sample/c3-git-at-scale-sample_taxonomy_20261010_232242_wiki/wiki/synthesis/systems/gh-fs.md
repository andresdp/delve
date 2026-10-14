---
title: GitHub filesystem distribution
type: system
code: GH-FS
organization: GitHub
dimensions: 3
tags:
- system
---

# GitHub filesystem distribution

GitHub before Spokes: NFS, GFS and DRBD filesystem distribution, then single-copy RPC fileservers.

Values supported by passages whose primary system is `GH-FS` (passage → system map).

| Dimension | Values (passages) |
|---|---|
| [[concepts/client-repository-and-working-tree-scaling|Client Repository and Working-Tree Scaling]] | • [[entities/rails-monolith|Rails monolith]] (1) |
| [[concepts/replica-topology-and-persistence|Replica Topology and Persistence]] | • [[entities/disk-repository-warm-cache|Disk repository warm cache]] (1)<br>• [[entities/filesystem-block-level-replication|Filesystem block-level replication]] (1) |
| [[concepts/repository-storage-representation|Repository Storage Representation]] | • [[entities/single-machine-repository-storage|Single-machine repository storage]] (2)<br>• [[entities/centralized-repository-hosting|Centralized repository hosting]] (1)<br>• [[entities/dedicated-fileserver-repository-hosting|Dedicated fileserver repository hosting]] (1)<br>• [[entities/delta-compressed-packfile-storage|Delta-compressed packfile storage]] (1)<br>• [[entities/filesystem-level-repository-distribution|Filesystem-level repository distribution]] (1)<br>• [[entities/nfs-based-centralized-repository-storage|NFS-based centralized repository storage]] (1)<br>• [[entities/packfile-size-minimizing-layout|Packfile size-minimizing layout]] (1)<br>• [[entities/whole-file-local-repository-caching|Whole-file local repository caching]] (1) |

## Attested design points

[[designs/p005|P005]], [[designs/p011|P011]]
