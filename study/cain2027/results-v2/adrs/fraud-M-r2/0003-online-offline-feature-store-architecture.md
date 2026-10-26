# Online/offline feature-store architecture

*How should inference features be stored and retrieved?*

* System: Card-fraud scoring service

## Context and Problem Statement

The scorer needs low-latency features while auditors need the model and feature inputs associated with each score to be recoverable later.

## Decision Drivers

* Latency: fast feature access
* Auditability: recoverable inputs

## Considered Options

* Online/offline feature-store architecture (`v:43.4`)
* Central analytical ML data platform (`v:43.1`)

## Decision Outcome

Chosen option: "Online/offline feature-store architecture" (`v:43.4`).

Low-latency feature access decides the choice, while the durable store supports later traceability and training reuse. This costs more operationally and makes the online store a serving dependency.

### Consequences

* Maintain consistent feature definitions across stores.
* Retain the feature data needed to reconstruct scored requests.

## Pros and Cons of the Options

### Online/offline feature-store architecture

* Good, because Latency: online store serves inference features
* Good, because Auditability: durable store supports reuse
* Bad, because Cost: requires complementary storage
* Bad, because Availability: online store is a runtime dependency
* Sources: `s06_p09`, `s21_p09`

### Central analytical ML data platform

* Good, because Auditability: shared prepared data
* Good, because Cost: consolidates analytical storage
* Bad, because Latency: analytical access may not suit scoring
* Bad, because Availability: inference depends on shared platform
