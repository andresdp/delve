# Feature serving storage

* System: Card-fraud scoring service

## Context and Problem Statement

The scorer needs fast feature reads, while auditors need a durable record of the features used. One storage path may not serve both access patterns well.

## Decision Drivers

* Tens-of-milliseconds latency
* Audit traceability

## Considered Options

* Online/offline feature-store architecture (`v:43.4`)
* Central analytical ML data platform (`v:43.1`)

## Decision Outcome

Chosen option: "Online/offline feature-store architecture" (`v:43.4`).

Latency decides the choice: online features serve the scoring request, with durable offline data supporting traceability. The cost is keeping the online and offline representations consistent.

### Consequences

* Record feature versions or snapshots for each score.
* Maintain synchronization between online and durable feature stores.

## Pros and Cons of the Options

### Online/offline feature-store architecture

* Good, because Low latency: online store serves inference features
* Good, because Audit traceability: offline store preserves feature data
* Bad, because Low latency: feature synchronization adds work
* Bad, because Audit traceability: storage lineage must be maintained
* Sources: `s06_p09`, `s21_p09`

### Central analytical ML data platform

* Good, because Audit traceability: shared platform exposes prepared data
* Good, because Cost: consolidates analytical data workflows
* Bad, because Low latency: analytical reads may be too slow
* Bad, because Audit traceability: inference-time feature snapshot is not explicit
* Sources: `s01_p05`, `s09_p08`
