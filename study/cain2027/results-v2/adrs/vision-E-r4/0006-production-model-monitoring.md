# Production model monitoring

* System: On-device visual inspection

## Context and Problem Statement

Cameras may operate disconnected, so the system needs a way to assess whether deployed models continue to perform well.

## Decision Drivers

* Defect detection quality
* Offline operation
* Tight budget

## Considered Options

* Model performance monitoring (`v:22.1`)
* Monitoring or logging data and predictions (`v:22.2`)
* No in-production monitoring (`v:22.3`)

## Decision Outcome

Chosen option: "Monitoring or logging data and predictions" (`v:22.2`).

Offline operation decides the choice: log inputs and predictions locally for later review and monitoring. The trade-off is device storage and the effort needed to inspect collected logs.

### Consequences

* Provide bounded local log storage and a collection path.
* Use reviewed labels to assess model performance.

## Pros and Cons of the Options

### Model performance monitoring

* Good, because Defect detection quality: tracks model performance
* Bad, because Offline operation: central monitoring may be delayed
* Sources: `d:22`, `v:22.1`

### Monitoring or logging data and predictions

* Good, because Offline operation: device logs can be collected later
* Bad, because Tight budget: logs require storage and review
* Sources: `d:22`, `v:22.2`

### No in-production monitoring

* Good, because Tight budget: avoids monitoring infrastructure
* Bad, because Defect detection quality: degradation can go unnoticed
* Sources: `d:22`, `v:22.3`
