# What production model information should be monitored and tracked?

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors need the model version and features behind each score; production tracking can capture usage, inputs, outputs, and interpretability information. The design space separates performance monitoring, logging, tracking, or no monitoring (d:22).

## Decision Drivers

* Audit traceability
* Peak availability

## Considered Options

* Model in-production tracking (`v:22.4`)
* Monitoring or logging data and predictions (`v:22.2`)
* Model performance monitoring (`v:22.1`)
* No in-production monitoring (`v:22.3`)

## Decision Outcome

Chosen option: "Model in-production tracking" (`v:22.4`).

Audit traceability decides: tracking usage, inputs, and outputs provides a basis for linking scores to the model and features used. This increases record-retention and management costs.

### Consequences

* Each score needs a durable record of model version and feature inputs.
* Tracking data needs access controls and retention rules.

## Pros and Cons of the Options

### Model in-production tracking

* Good, because Traceability: track model usage, inputs, and outputs
* Good, because Availability: supports operational visibility
* Bad, because Cost: retain and manage score records
* Sources: `d:22`, `v:22.4`

### Monitoring or logging data and predictions

* Good, because Traceability: log inputs and predictions
* Bad, because Availability: limited model-specific tracking
* Sources: `d:22`, `v:22.2`

### Model performance monitoring

* Good, because Availability: observe model performance
* Bad, because Traceability: does not alone link inputs to scores
* Sources: `d:22`, `v:22.1`

### No in-production monitoring

* Bad, because Traceability: no production score trail
* Bad, because Availability: operational issues less visible
* Sources: `d:22`, `v:22.3`
