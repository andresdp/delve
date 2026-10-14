---
title: Design points
type: synthesis
seed: 42
attest_by: primary
tags:
- synthesis
- design-points
---

# Design points

Design points combine one value from each of k dimensions, sampled with a fixed seed (`benchmark/design_points.py`). **Attested**: one system supports every value. **Novel**: no system supports them all; exploring such combinations is a purpose of the design space. **Control**: built to fail (a rejected value, or a value from another dimension).

## k = 2

### Attested (4)

- [[designs/p011|P011]] (GH-FS): Replica Topology and Persistence: Disk repository warm cache; Client Repository and Working-Tree Scaling: Rails monolith
- [[designs/p016|P016]] (GH-SPOKES): Replica Topology and Persistence: Cross-rack replica placement; Write Commitment and Consistency: Permanent data-loss resistance
- [[designs/p022|P022]] (CUR-CONT): Replica Topology and Persistence: ETag-validated replica freshness; Write Commitment and Consistency: Linearized repository operations
- [[designs/p023|P023]] (MS-GVFS): Repository Service Scaling: Co-located transfer cache proxy; Client Repository and Working-Tree Scaling: GVFS protocol standardization

### Novel (4)

- [[designs/p002|P002]]: Client Repository and Working-Tree Scaling: Incremental bounded pack repacking; Repository Storage Representation: Filesystem-level repository distribution
- [[designs/p014|P014]]: Client Repository and Working-Tree Scaling: Built-in filesystem monitor; Repository Storage Representation: Git-level distribution
- [[designs/p018|P018]]: Client Repository and Working-Tree Scaling: Compressed Git index; Write Commitment and Consistency: Consensus-free arbitrary repository primaries
- [[designs/p020|P020]]: Replica Topology and Persistence: ETag-validated replica freshness; Client Repository and Working-Tree Scaling: Git-aware custom filesystem watcher

### Control (4)

- [[designs/p006|P006]] (misplaced_value): Repository Service Scaling: Three-replica repository topology; Client Repository and Working-Tree Scaling: Two-phase repack and expire
- [[designs/p008|P008]] (misplaced_value): Replica Topology and Persistence: GVFS deployment without cache infrastructure; Write Commitment and Consistency: Majority-exclusive write locking
- [[designs/p015|P015]] (rejected_value): Repository Service Scaling: Core Git upstreaming; Client Repository and Working-Tree Scaling: Single-pack full repacking
- [[designs/p021|P021]] (rejected_value): Write Commitment and Consistency: Majority-exclusive write locking; Repository Storage Representation: Object-level repository distribution

## k = 3

### Attested (4)

- [[designs/p001|P001]] (MS-SCALAR): Replica Topology and Persistence: On-demand repository materialization; Repository Service Scaling: Explicit repository registration; Repository Storage Representation: Delta-compressed packfile storage
- [[designs/p005|P005]] (GH-FS): Replica Topology and Persistence: Disk repository warm cache; Client Repository and Working-Tree Scaling: Rails monolith; Repository Storage Representation: Centralized repository hosting
- [[designs/p009|P009]] (GH-SPOKES): Replica Topology and Persistence: Arbitrary replica-based read scaling; Repository Service Scaling: Priority scheduling for user updates; Write Commitment and Consistency: Atomic reference-update rollback
- [[designs/p012|P012]] (CUR-CONT): Repository Service Scaling: Migration-friendly repository platform; Client Repository and Working-Tree Scaling: Background Git object-database maintenance; Write Commitment and Consistency: WAL durability before push acknowledgement

### Novel (4)

- [[designs/p003|P003]]: Replica Topology and Persistence: Cross-rack replica placement; Repository Service Scaling: Quiesced rolling server reboot; Client Repository and Working-Tree Scaling: Compressed Git index
- [[designs/p007|P007]]: Repository Service Scaling: Quiesced read admission; Client Repository and Working-Tree Scaling: Small-pack batch selection; Repository Storage Representation: Application layer over unmodified Git
- [[designs/p010|P010]]: Replica Topology and Persistence: S3 Express object-storage substrate; Write Commitment and Consistency: Consistency and partition tolerance priority; Repository Storage Representation: Centralized repository hosting
- [[designs/p019|P019]]: Client Repository and Working-Tree Scaling: Non-virtualized large-repository support; Write Commitment and Consistency: Deterministic replica transaction results; Repository Storage Representation: Packfile-based Git networking

### Control (4)

- [[designs/p004|P004]] (misplaced_value): Replica Topology and Persistence: Incremental reachable-commit graph; Write Commitment and Consistency: Synchronous write commitment; Repository Storage Representation: Packfile-based Git networking
- [[designs/p013|P013]] (rejected_value): Replica Topology and Persistence: Co-located filesystem replica placement; Repository Service Scaling: Checksum-guided repository repair scheduling; Write Commitment and Consistency: Consensus-free arbitrary repository primaries
- [[designs/p017|P017]] (misplaced_value): Replica Topology and Persistence: Proxy-mediated repository replication; Repository Service Scaling: Three-failure offline threshold; Write Commitment and Consistency: JGit repository-storage abstraction
- [[designs/p024|P024]] (rejected_value): Repository Service Scaling: Foreground automatic garbage collection; Write Commitment and Consistency: Automatic replica repair; Repository Storage Representation: Centralized repository hosting
