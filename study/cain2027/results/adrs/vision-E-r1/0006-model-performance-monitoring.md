# Model performance monitoring

*How should the deployed model be monitored?*

* System: On-device visual inspection

## Context and Problem Statement

The brief does not specify how devices report status, and network access may be absent. The design space includes model performance monitoring and logging data and predictions.

## Decision Drivers

* production inspection
* intermittent network
* model quality

## Considered Options

* Model performance monitoring (`v:22.1`)
* Monitoring or logging data and predictions (`v:22.2`)

## Decision Outcome

Chosen option: "Model performance monitoring" (`v:22.1`).

Monitoring performance focuses on whether the model remains suitable for inspection. The checked combination had no warnings, but no attesting sources.

### Consequences

* Define performance indicators for inspection quality.
* Plan for collecting or reviewing signals from offline devices.

## Pros and Cons of the Options

### Model performance monitoring

* Good, because tracks model performance
* Bad, because needs usable performance signals
* Sources: `d:22`, `v:22.1`

### Monitoring or logging data and predictions

* Good, because records inputs and outputs
* Bad, because requires storage and review
* Sources: `d:22`, `v:22.2`
