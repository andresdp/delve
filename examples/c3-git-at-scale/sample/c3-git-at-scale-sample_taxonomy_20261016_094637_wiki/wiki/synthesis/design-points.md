---
type: Synthesis
title: Design points
seed: 42
attest_by: primary
tags:
- synthesis
- design-points
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Design points

Design points combine one value from each of k dimensions, sampled with a fixed seed (`benchmark/design_points.py`). **Attested**: one system supports every value. **Novel**: no system supports them all; exploring such combinations is a purpose of the design space. **Control**: built to fail (a rejected value, or a value from another dimension).

## k = 2

### Attested (4)

- [P011](/designs/p011.md) (GH-SPOKES): Replica Topology: Three-replica repository replication; Replica State Comparison: Incremental XOR checksum maintenance
- [P016](/designs/p016.md) (MS-SCALAR): Compaction Maintenance Technique: Background incremental maintenance; Client Repository Performance Strategy: Custom Git client extensions
- [P022](/designs/p022.md) (CUR-CONT): Replica Synchronization Mechanism: Git-level distribution; Replica Write Coordination: Strict-majority coordinated writes
- [P023](/designs/p023.md) (CUR-CONT): Repository Placement and Read Routing: Stale-routing recovery; Replica Write Coordination: Consensus-free write acceptance

### Novel (4)

- [P002](/designs/p002.md): Replica State Comparison: Checksum-based replica state comparison; Client Repository Performance Strategy: Custom Git client extensions
- [P014](/designs/p014.md): Repository Placement and Read Routing: Stateless repository placement; Replica State Comparison: Incremental XOR checksum maintenance
- [P018](/designs/p018.md): Replica State Comparison: Full checksum recomputation; Large-Repository Object Acquisition: Partial clone transfer
- [P020](/designs/p020.md): Compaction Maintenance Technique: Loose-object cleanup; Replica Write Coordination: Orchestrated push fan-out

### Control (4)

- [P006](/designs/p006.md) (misplaced_value): Repository Placement and Read Routing: Explicit repository-location tracking; Replica Synchronization Mechanism: Full checksum recomputation
- [P008](/designs/p008.md) (misplaced_value): Compaction Maintenance Technique: Loose-object cleanup; Client Repository Performance Strategy: GVFS demand-driven transfer
- [P015](/designs/p015.md) (rejected_value): Replica Topology: Single-extra-copy replication; Replica State Comparison: Incremental XOR checksum maintenance
- [P021](/designs/p021.md) (rejected_value): Replica Topology: Single-extra-copy replication; Replica Synchronization Mechanism: Git-level distribution

## k = 3

### Attested (4)

- [P001](/designs/p001.md) (CUR-CONT): Compaction Maintenance Technique: Background incremental maintenance; Repository Placement and Read Routing: Stateless repository placement; Replica Topology: Three-replica repository replication
- [P005](/designs/p005.md) (GH-SPOKES): Repository Placement and Read Routing: Explicit repository-location tracking; Replica Synchronization Mechanism: Git-level distribution; Replica State Comparison: Checksum-based replica state comparison
- [P009](/designs/p009.md) (MS-SCALAR): Compaction Maintenance Technique: Background incremental maintenance; Large-Repository Object Acquisition: GVFS without cache infrastructure; Client Repository Performance Strategy: Preserved visible branch references during background fetch
- [P012](/designs/p012.md) (CUR-CONT): Replica Topology: Three-replica repository replication; Replica Synchronization Mechanism: Git-level distribution; Replica Write Coordination: Consensus-free write acceptance

### Novel (4)

- [P003](/designs/p003.md): Replica Write Coordination: Orchestrated push fan-out; Large-Repository Object Acquisition: Standard-Git GVFS protocol support; Client Repository Performance Strategy: Hidden remote-reference namespace
- [P007](/designs/p007.md): Compaction Maintenance Technique: Loose-object cleanup; Repository Placement and Read Routing: Stateless repository placement; Replica Synchronization Mechanism: Packfile-level application replication
- [P010](/designs/p010.md): Compaction Maintenance Technique: Loose-object cleanup; Repository Placement and Read Routing: Rendezvous-hashed repository routing; Replica Topology: Three-replica repository replication
- [P019](/designs/p019.md): Replica State Comparison: Checksum-based replica state comparison; Replica Write Coordination: Rollback of non-majority writes; Client Repository Performance Strategy: Single-file index stream I/O

### Control (4)

- [P004](/designs/p004.md) (misplaced_value): Repository Placement and Read Routing: Preserved visible branch references during background fetch; Replica Synchronization Mechanism: Packfile-level application replication; Replica State Comparison: Checksum-based replica state comparison
- [P013](/designs/p013.md) (rejected_value): Repository Placement and Read Routing: Per-server repository location tracking; Replica Write Coordination: Per-write voting without a primary; Large-Repository Object Acquisition: Partial clone transfer
- [P017](/designs/p017.md) (misplaced_value): Replica Synchronization Mechanism: Git-level distribution; Large-Repository Object Acquisition: Standard-Git GVFS protocol support; Client Repository Performance Strategy: Closest sufficiently fresh replica routing
- [P024](/designs/p024.md) (rejected_value): Compaction Maintenance Technique: Single-pack full repacking; Replica Topology: Three-replica repository replication; Replica Synchronization Mechanism: Spokes repository replication
