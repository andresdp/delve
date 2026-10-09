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

- [[designs/p011|P011]] (GH-SPOKES): Write Coordination and Replica Consistency: Per-write voting protocol; Git Hosting and Acceleration Integration: Native Git repository integration
- [[designs/p016|P016]] (GOOG-DHT): Client Repository Workload Scaling: DAG-dependent repository traversal; Git Hosting and Acceleration Integration: JGit repository abstraction for distributed storage
- [[designs/p022|P022]] (CUR-CONT): Replica Failure Repair and Failover: Arbitrary replica read scale-out; Git Hosting and Acceleration Integration: Proven engineering and operational philosophy
- [[designs/p023|P023]] (MS-GVFS): Replica Failure Repair and Failover: Co-located object-cache proxy routing; Git Hosting and Acceleration Integration: Git protocol without GVFS cache infrastructure

### Novel (4)

- [[designs/p002|P002]]: Repository Replica Placement: Three-replica repository placement; Git Hosting and Acceleration Integration: Offline development capability
- [[designs/p014|P014]]: Repository Replica Placement: Multi-rack repository replication; Client Repository Workload Scaling: DAG-dependent repository traversal
- [[designs/p018|P018]]: Client Repository Workload Scaling: Combined repository maintenance command; Git Hosting and Acceleration Integration: Offline development capability
- [[designs/p020|P020]]: Write Coordination and Replica Consistency: Local NVMe Git repository; Git Hosting and Acceleration Integration: Core Git eventual performance path

### Control (4)

- [[designs/p006|P006]] (misplaced_value): Repository Replica Placement: External repository-machine routing database; Client Repository Workload Scaling: DAG-dependent repository traversal
- [[designs/p008|P008]] (misplaced_value): Write Coordination and Replica Consistency: Primary-only repository compaction; Client Repository Workload Scaling: Advisory replica demotion
- [[designs/p015|P015]] (rejected_value): Repository Replica Placement: HTTP daemon over on-disk repository; Write Coordination and Replica Consistency: Cross-region replica coordination
- [[designs/p021|P021]] (rejected_value): Write Coordination and Replica Consistency: Git-level distribution; Client Repository Workload Scaling: Virtualized filesystem population

## k = 3

### Attested (4)

- [[designs/p001|P001]] (MS-SCALAR): Write Coordination and Replica Consistency: Incremental geometric repository compaction; Client Repository Workload Scaling: Foreground automatic garbage collection; Git Hosting and Acceleration Integration: User-controlled maintenance suspension
- [[designs/p005|P005]] (GH-SPOKES): Repository Replica Placement: Multi-server repository replication; Replica Failure Repair and Failover: Per-application-server failure views; Git Hosting and Acceleration Integration: Forked Git implementation
- [[designs/p009|P009]] (MS-GVFS): Replica Failure Repair and Failover: Co-located object-cache proxy routing; Client Repository Workload Scaling: GVFS object-transfer protocol; Git Hosting and Acceleration Integration: Co-located GVFS cache infrastructure
- [[designs/p012|P012]] (CUR-CONT): Write Coordination and Replica Consistency: Durability-before-acknowledgment; Replica Failure Repair and Failover: Arbitrary replica read scale-out; Git Hosting and Acceleration Integration: Continuous infrastructure evolution

### Novel (4)

- [[designs/p003|P003]]: Repository Replica Placement: Replica trimming for lightly used repositories; Client Repository Workload Scaling: GVFS object-transfer protocol; Git Hosting and Acceleration Integration: Centralized Git hosting architecture
- [[designs/p007|P007]]: Write Coordination and Replica Consistency: Batched WAL persistence; Replica Failure Repair and Failover: Failure-aware request routing; Git Hosting and Acceleration Integration: Offline development capability
- [[designs/p010|P010]]: Repository Replica Placement: Multi-disk repository placement; Client Repository Workload Scaling: Hourly background fetches; Git Hosting and Acceleration Integration: Custom Git client dependency
- [[designs/p019|P019]]: Replica Failure Repair and Failover: Per-application-server failure views; Client Repository Workload Scaling: Hidden-reference background fetch; Git Hosting and Acceleration Integration: Custom Git client dependency

### Control (4)

- [[designs/p004|P004]] (misplaced_value): Repository Replica Placement: Periodic repository compaction; Replica Failure Repair and Failover: Combined heartbeat and real-traffic detection; Git Hosting and Acceleration Integration: Packfile-level repository distribution
- [[designs/p013|P013]] (rejected_value): Repository Replica Placement: Multi-rack repository replication; Client Repository Workload Scaling: Suppressed ahead-behind status calculation; Git Hosting and Acceleration Integration: GVFS without cache infrastructure
- [[designs/p017|P017]] (misplaced_value): Repository Replica Placement: Multi-rack repository replication; Replica Failure Repair and Failover: Centralized Git hosting architecture; Client Repository Workload Scaling: Partial clone
- [[designs/p024|P024]] (rejected_value): Write Coordination and Replica Consistency: Local NVMe Git repository; Client Repository Workload Scaling: Foreground maintenance execution; Git Hosting and Acceleration Integration: Git-level repository access redesign
