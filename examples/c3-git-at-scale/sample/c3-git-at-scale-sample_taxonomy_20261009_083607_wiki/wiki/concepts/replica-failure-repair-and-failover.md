---
title: Replica Failure Repair and Failover
type: dimension
id: '3'
core: true
values: 36
candidate_values: 31
outcomes: 5
evidence:
  codes: 50
  documents: 13
  sources: 4
relations:
- consequence [[concepts/repository-replica-placement|Repository Replica Placement]]
- consequence [[concepts/client-repository-workload-scaling|Client Repository Workload Scaling]]
tags:
- dimension
- core
systems:
- '[[synthesis/systems/cur-cont|Cursor Continuity and Origin]]'
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
- '[[synthesis/systems/ms-gvfs|Microsoft VFS for Git (GVFS)]]'
---

# Replica Failure Repair and Failover

How are unhealthy replicas detected, repaired, isolated, and bypassed during failures or maintenance?

## Values

| Value | Status | Passages |
|---|---|---|
| [[entities/advisory-replica-demotion|Advisory replica demotion]] | accepted | 1 |
| [[entities/arbitrary-replica-read-scale-out|Arbitrary replica read scale-out]] | accepted | 1 |
| [[entities/automatic-replica-repair|Automatic replica repair]] | accepted | 4 |
| [[entities/bounded-concurrent-reboots|Bounded concurrent reboots]] | accepted | 1 |
| [[entities/co-located-object-cache-proxy-routing|Co-located object-cache proxy routing]] | accepted | 1 |
| [[entities/combined-heartbeat-and-real-traffic-detection|Combined heartbeat and real-traffic detection]] | accepted | 2 |
| [[entities/consecutive-request-failure-quarantine-threshold|Consecutive request-failure quarantine threshold]] | accepted | 1 |
| [[entities/continued-write-replication-during-quiescence|Continued write replication during quiescence]] | accepted | 1 |
| [[entities/external-repository-machine-routing-database|External repository-machine routing database]] | accepted | 1 |
| [[entities/failure-aware-request-routing|Failure-aware request routing]] | accepted | 1 |
| [[entities/failure-handling-reuse-for-maintenance|Failure-handling reuse for maintenance]] | accepted | 1 |
| [[entities/incremental-replica-state-checksum-verification|Incremental replica-state checksum verification]] | accepted | 2 |
| [[entities/mxn-failure-detection-model|MxN failure-detection model]] | accepted | 1 |
| [[entities/n-to-n-replica-reconstruction|N-to-N replica reconstruction]] | accepted | 1 |
| [[entities/operation-failure-based-primary-failure-detection|Operation-failure-based primary failure detection]] | accepted | 1 |
| [[entities/ordered-multi-replica-failover|Ordered multi-replica failover]] | accepted | 1 |
| [[entities/per-application-server-failure-detection|Per-application-server failure detection]] | accepted | 1 |
| [[entities/per-application-server-failure-views|Per-application-server failure views]] | accepted | 1 |
| [[entities/periodic-replica-count-reconciliation|Periodic replica-count reconciliation]] | accepted | 3 |
| [[entities/pet-style-repository-operations|Pet-style repository operations]] | accepted | 1 |
| [[entities/pre-reboot-server-quiescence|Pre-reboot server quiescence]] | accepted | 3 |
| [[entities/rpc-failover-monitoring|RPC failover monitoring]] | accepted | 2 |
| [[entities/rack-level-maintenance-sequencing|Rack-level maintenance sequencing]] | accepted | 1 |
| [[entities/rolling-reboot-testing|Rolling reboot testing]] | accepted | 1 |
| [[entities/single-replica-read-routing|Single-replica read routing]] | accepted | 1 |
| [[entities/unhealthy-replica-isolation|Unhealthy-replica isolation]] | accepted | 1 |
| [[entities/immediate-server-reboot|Immediate server reboot]] | mixed | 2 |
| [[entities/supplemental-heartbeat-recovery-signals|Supplemental heartbeat recovery signals]] | mixed | 2 |
| [[entities/chaos-monkey-server-testing|Chaos-monkey server testing]] | rejected | 1 |
| [[entities/heartbeat-based-primary-failure-detection|Heartbeat-based primary failure detection]] | rejected | 2 |
| [[entities/unplanned-server-unplugging|Unplanned server unplugging]] | rejected | 1 |
| [[entities/false-offline-marking-of-healthy-replicas|False offline marking of healthy replicas]] | outcome | 2 |
| [[entities/localized-application-server-failure-impact|Localized application-server failure impact]] | outcome | 1 |
| [[entities/lost-clone-progress-after-shutdown|Lost clone progress after shutdown]] | outcome | 1 |
| [[entities/rpc-failover-graph-fault-visibility|RPC-failover graph fault visibility]] | outcome | 1 |
| [[entities/two-copy-failure-degradation|Two-copy failure degradation]] | outcome | 2 |

## Relations

- consequence → [[concepts/repository-replica-placement|Repository Replica Placement]]: Replica coordination choices determine whether remaining replicas can continue reads and majority-based writes during server absence.
- consequence → [[concepts/client-repository-workload-scaling|Client Repository Workload Scaling]]: Maintenance and failure handling directly affect whether large client fetches and clones complete without losing transferred progress.
- ← constrains from [[concepts/repository-replica-placement|Repository Replica Placement]]
- ← constrains from [[concepts/client-repository-workload-scaling|Client Repository Workload Scaling]]

## Evidence

50 open codes from 13 passages in 4 sources.

**Core dimension:** yes ★ (4 sources, 3 systems; core = ≥ 2 sources or ≥ 2 systems).
