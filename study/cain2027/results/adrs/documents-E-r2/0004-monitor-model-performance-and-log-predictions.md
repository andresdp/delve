# Monitor model performance and log predictions

* System: Large-scale document classification

## Context and Problem Statement

Operators need to see when classification quality drifts. Monitoring needs to capture model performance as well as the data and predictions needed to investigate changes.

## Decision Drivers

* Detect quality drift
* Operator visibility

## Considered Options

* Model performance monitoring (`v:22.1`)
* Monitoring or logging data and predictions (`v:22.2`)
* No in-production monitoring (`v:22.3`)

## Decision Outcome

Chosen option: "Model performance monitoring" (`v:22.1`).

Model performance monitoring directly addresses the brief’s need to see quality drift. Logging data and predictions is a useful complementary practice, but the design-space check permits one value per dimension, so only performance monitoring is selected (d:22).

### Consequences

* Define and track classification performance measures.
* Logging details and retention remain to be designed.

## Pros and Cons of the Options

### Model performance monitoring

* Good, because Tracks model performance
* Good, because Supports drift visibility
* Bad, because Needs performance measures
* Sources: `d:22`, `v:22.1`

### Monitoring or logging data and predictions

* Good, because Records inputs and predictions
* Good, because Supports investigation
* Bad, because Requires log storage
* Sources: `d:22`, `v:22.2`

### No in-production monitoring

* Good, because No monitoring overhead
* Bad, because Cannot meet drift visibility need
* Sources: `d:22`, `v:22.3`
