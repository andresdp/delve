# How should production quality be monitored?

* System: Large-scale document classification

## Context and Problem Statement

Operators need to see when classification quality drifts. The design space includes performance monitoring and logging data and predictions as production monitoring options (d:22).

## Decision Drivers

* Quality drift visibility
* Millions of documents/day

## Considered Options

* Model performance monitoring (`v:22.1`)
* Monitoring or logging data and predictions (`v:22.2`)

## Decision Outcome

Chosen option: "Model performance monitoring" (`v:22.1`).

Drift visibility decides the choice: monitor model performance directly, accepting that useful measures and labels must be available. The design space treats these as alternatives, though the brief does not rule out combining them.

### Consequences

* Define performance measures and alert thresholds.
* Arrange access to labels or other quality signals.

## Pros and Cons of the Options

### Model performance monitoring

* Good, because Quality: observe model performance measures
* Bad, because Quality: requires suitable measures and labels
* Sources: `d:22`, `v:22.1`

### Monitoring or logging data and predictions

* Good, because Quality: retain data and predictions for analysis
* Bad, because Scale: logging creates storage and processing load
* Sources: `d:22`, `v:22.2`
