# Track inputs and outputs in production

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors must be able to reconstruct which model version and features produced a score. The design space distinguishes model tracking from logging data and predictions (d:22).

## Decision Drivers

* Audit traceability
* Scoring latency

## Considered Options

* Model in-production tracking (`v:22.4`)
* Monitoring or logging data and predictions (`v:22.2`)
* No in-production monitoring (`v:22.3`)

## Decision Outcome

Chosen option: "Model in-production tracking" (`v:22.4`).

Audit traceability decides in favor of tracking model usage, inputs, and outputs; synchronous tracking overhead must be controlled to protect latency.

### Consequences

* Persist model version and feature references with each score.
* Tracking storage and retention add operational cost.

## Pros and Cons of the Options

### Model in-production tracking

* Good, because Audit traceability: tracks usage, inputs, and outputs
* Bad, because Scoring latency: synchronous tracking may add overhead
* Sources: `d:22`, `v:22.4`

### Monitoring or logging data and predictions

* Good, because Scoring latency: logging can be decoupled from scoring
* Bad, because Audit traceability: logs may omit model-specific details
* Sources: `d:22`, `v:22.2`

### No in-production monitoring

* Good, because Scoring latency: avoids monitoring overhead
* Bad, because Audit traceability: lacks production records
* Sources: `d:22`, `v:22.3`
