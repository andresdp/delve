---
title: Microsoft VFS for Git (GVFS)
type: system
code: MS-GVFS
organization: Microsoft
dimensions: 3
tags:
- system
---

# Microsoft VFS for Git (GVFS)

Virtualized filesystem on the client and the GVFS protocol with cache servers.

Values supported by passages whose primary system is `MS-GVFS` (passage → system map).

| Dimension | Values (passages) |
|---|---|
| [[concepts/client-repository-workload-scaling|Client Repository Workload Scaling]] | • [[entities/central-server-on-demand-object-retrieval|Central-server on-demand object retrieval]] (1)<br>• [[entities/gvfs-object-transfer-protocol|GVFS object-transfer protocol]] (1)<br>• [[entities/sparse-checkout|Sparse checkout]] (1) |
| [[concepts/git-hosting-and-acceleration-integration|Git Hosting and Acceleration Integration]] | • [[entities/co-located-gvfs-cache-infrastructure|Co-located GVFS cache infrastructure]] (1)<br>• [[entities/git-protocol-without-gvfs-cache-infrastructure|Git protocol without GVFS cache infrastructure]] (1) |
| [[concepts/replica-failure-repair-and-failover|Replica Failure Repair and Failover]] | • [[entities/co-located-object-cache-proxy-routing|Co-located object-cache proxy routing]] (1) |

## Attested design points

[[designs/p009|P009]], [[designs/p023|P023]]
