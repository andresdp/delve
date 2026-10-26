# How should the system retain evidence for score audits?

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors must be able to identify the model version and features behind each decision. Production tracking and data versioning provide relevant design-space options, but the space does not define a complete audit record.

## Decision Drivers

* model-version traceability
* feature traceability
* auditor review

## Considered Options

* Model in-production tracking (`v:22.4`)
* Monitoring or logging data and predictions (`v:22.2`)
* Data version repository (`v:11.1`)

## Decision Outcome

Chosen option: "Model in-production tracking" (`v:22.4`).

It covers usage, inputs, outputs, and interpretability, making it the closest listed option for later score review; pair each decision record with the model version and feature values or immutable references. (d:22, v:22.4)

### Consequences

* Retain model version and feature evidence per score.
* Set retention and access controls for audit records.

## Pros and Cons of the Options

### Model in-production tracking

* Good, because tracks usage and inputs
* Good, because tracks outputs and interpretability
* Bad, because added storage
* Bad, because sensitive records need controls
* Sources: `d:22`, `v:22.4`

### Monitoring or logging data and predictions

* Good, because records inputs and predictions
* Good, because supports operational review
* Bad, because may omit model lineage
* Bad, because log volume
* Sources: `d:22`, `v:22.2`

### Data version repository

* Good, because versions training data
* Good, because supports reproducibility
* Bad, because does not alone identify online features
* Bad, because added repository
* Sources: `d:11`, `v:11.1`
