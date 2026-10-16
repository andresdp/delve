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

- [[designs/p011|P011]] (GH-SPOKES): Replica Topology: Three-replica repository replication; Replica State Comparison: Incremental XOR checksum maintenance
- [[designs/p016|P016]] (MS-SCALAR): Compaction Maintenance Technique: Background incremental maintenance; Client Repository Performance Strategy: Custom Git client extensions
- [[designs/p022|P022]] (CUR-CONT): Replica Synchronization Mechanism: Git-level distribution; Replica Write Coordination: Strict-majority coordinated writes
- [[designs/p023|P023]] (CUR-CONT): Repository Placement and Read Routing: Stale-routing recovery; Replica Write Coordination: Consensus-free write acceptance

### Novel (4)

- [[designs/p002|P002]]: Replica State Comparison: Checksum-based replica state comparison; Client Repository Performance Strategy: Custom Git client extensions
- [[designs/p014|P014]]: Repository Placement and Read Routing: Stateless repository placement; Replica State Comparison: Incremental XOR checksum maintenance
- [[designs/p018|P018]]: Replica State Comparison: Full checksum recomputation; Large-Repository Object Acquisition: Partial clone transfer
- [[designs/p020|P020]]: Compaction Maintenance Technique: Loose-object cleanup; Replica Write Coordination: Orchestrated push fan-out

### Control (4)

- [[designs/p006|P006]] (misplaced_value): Repository Placement and Read Routing: Explicit repository-location tracking; Replica Synchronization Mechanism: Full checksum recomputation
- [[designs/p008|P008]] (misplaced_value): Compaction Maintenance Technique: Loose-object cleanup; Client Repository Performance Strategy: GVFS demand-driven transfer
- [[designs/p015|P015]] (rejected_value): Replica Topology: Single-extra-copy replication; Replica State Comparison: Incremental XOR checksum maintenance
- [[designs/p021|P021]] (rejected_value): Replica Topology: Single-extra-copy replication; Replica Synchronization Mechanism: Git-level distribution

## k = 3

### Attested (4)

- [[designs/p001|P001]] (CUR-CONT): Compaction Maintenance Technique: Background incremental maintenance; Repository Placement and Read Routing: Stateless repository placement; Replica Topology: Three-replica repository replication
- [[designs/p005|P005]] (GH-SPOKES): Repository Placement and Read Routing: Explicit repository-location tracking; Replica Synchronization Mechanism: Git-level distribution; Replica State Comparison: Checksum-based replica state comparison
- [[designs/p009|P009]] (MS-SCALAR): Compaction Maintenance Technique: Background incremental maintenance; Large-Repository Object Acquisition: GVFS without cache infrastructure; Client Repository Performance Strategy: Preserved visible branch references during background fetch
- [[designs/p012|P012]] (CUR-CONT): Replica Topology: Three-replica repository replication; Replica Synchronization Mechanism: Git-level distribution; Replica Write Coordination: Consensus-free write acceptance

### Novel (4)

- [[designs/p003|P003]]: Replica Write Coordination: Orchestrated push fan-out; Large-Repository Object Acquisition: Standard-Git GVFS protocol support; Client Repository Performance Strategy: Hidden remote-reference namespace
- [[designs/p007|P007]]: Compaction Maintenance Technique: Loose-object cleanup; Repository Placement and Read Routing: Stateless repository placement; Replica Synchronization Mechanism: Packfile-level application replication
- [[designs/p010|P010]]: Compaction Maintenance Technique: Loose-object cleanup; Repository Placement and Read Routing: Rendezvous-hashed repository routing; Replica Topology: Three-replica repository replication
- [[designs/p019|P019]]: Replica State Comparison: Checksum-based replica state comparison; Replica Write Coordination: Rollback of non-majority writes; Client Repository Performance Strategy: Single-file index stream I/O

### Control (4)

- [[designs/p004|P004]] (misplaced_value): Repository Placement and Read Routing: Preserved visible branch references during background fetch; Replica Synchronization Mechanism: Packfile-level application replication; Replica State Comparison: Checksum-based replica state comparison
- [[designs/p013|P013]] (rejected_value): Repository Placement and Read Routing: Per-server repository location tracking; Replica Write Coordination: Per-write voting without a primary; Large-Repository Object Acquisition: Partial clone transfer
- [[designs/p017|P017]] (misplaced_value): Replica Synchronization Mechanism: Git-level distribution; Large-Repository Object Acquisition: Standard-Git GVFS protocol support; Client Repository Performance Strategy: Closest sufficiently fresh replica routing
- [[designs/p024|P024]] (rejected_value): Compaction Maintenance Technique: Single-pack full repacking; Replica Topology: Three-replica repository replication; Replica Synchronization Mechanism: Spokes repository replication
