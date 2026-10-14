---
title: Microsoft VFS for Git (GVFS)
type: system
code: MS-GVFS
organization: Microsoft
dimensions: 2
tags:
- system
---

# Microsoft VFS for Git (GVFS)

Virtualized filesystem on the client and the GVFS protocol with cache servers.

Values supported by passages whose primary system is `MS-GVFS` (passage → system map).

| Dimension | Values (passages) |
|---|---|
| [[concepts/client-repository-and-working-tree-scaling|Client Repository and Working-Tree Scaling]] | • [[entities/default-sparse-clone-initialization|Default sparse clone initialization]] (1)<br>• [[entities/gvfs-protocol-standardization|GVFS protocol standardization]] (1)<br>• [[entities/on-demand-object-retrieval|On-demand object retrieval]] (1)<br>• [[entities/rails-monolith|Rails monolith]] (1)<br>• [[entities/sparse-checkout-working-tree|Sparse-checkout working tree]] (1) |
| [[concepts/repository-service-scaling|Repository Service Scaling]] | • [[entities/centralized-missing-object-dependency|Centralized missing-object dependency]] (1)<br>• [[entities/co-located-transfer-cache-proxy|Co-located transfer cache proxy]] (1) |

## Attested design points

[[designs/p023|P023]]
