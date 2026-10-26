# Persist model version and feature snapshot with each score

*What score evidence should be retained?*

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors must later be able to identify the model version and features that produced each score. Retaining that evidence supports reconstruction but adds storage and handling costs.

## Decision Drivers

* Auditability
* Low latency

## Considered Options

* Persist model version and feature snapshot with each score
* Persist model version and feature reference
* Persist model version only

## Decision Outcome

Chosen option: "Persist model version and feature snapshot with each score".

Auditability is a stated requirement, and a snapshot gives the strongest evidence; this accepts additional write and storage costs that may affect latency.

### Consequences

* Store a durable per-score record with model identity and features.
* Measure evidence-write time against the latency budget.

## Pros and Cons of the Options

### Persist model version and feature snapshot with each score

* Good, because Auditability: preserves inputs and model identity
* Bad, because Low latency: adds write work on the scoring path

### Persist model version and feature reference

* Good, because Low latency: stores less data per score
* Bad, because Auditability: depends on referenced features remaining available

### Persist model version only

* Good, because Low latency: minimal evidence write
* Bad, because Auditability: cannot identify the features used
