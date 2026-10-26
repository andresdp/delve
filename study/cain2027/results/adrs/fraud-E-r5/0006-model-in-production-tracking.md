# Model in-production tracking

*How to monitor and track production scoring?*

* System: Card-fraud scoring service

## Context and Problem Statement

The system must remain available during peaks and provide auditors with model and feature provenance for each score. The design space treats monitoring and tracking as alternatives in one dimension (d:22).

## Decision Drivers

* peak availability
* audit trail

## Considered Options

* Model in-production tracking (`v:22.4`)
* No in-production monitoring (`v:22.3`)

## Decision Outcome

Chosen option: "Model in-production tracking" (`v:22.4`).

Production tracking aligns directly with the required model and feature audit trail and can capture the usage and inputs behind each score (d:22).

### Consequences

* Log model version, transaction reference, and feature evidence per score.
* Set retention and access controls for audit records.

## Pros and Cons of the Options

### Model in-production tracking

* Good, because Tracks usage and inputs
* Good, because Supports interpretability records
* Bad, because Telemetry volume
* Bad, because Retention cost
* Sources: `d:22`, `v:22.4`

### No in-production monitoring

* Good, because No monitoring overhead
* Good, because Less instrumentation
* Bad, because Limited incident insight
* Bad, because Missing score lineage
* Sources: `d:22`, `v:22.3`
