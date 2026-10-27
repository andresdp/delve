# Monitor model performance in production

* System: Large-scale document classification

## Context and Problem Statement

Operators need visibility into classification quality drift after deployment.

## Decision Drivers

* Quality drift visibility
* Operational monitoring

## Considered Options

* Model performance monitoring (`v:22.1`)
* No in-production monitoring (`v:22.3`)

## Decision Outcome

Chosen option: "Model performance monitoring" (`v:22.1`).

Performance monitoring directly addresses the stated need to see quality drift and was selected in the checked point (d:22, v:22.1).

### Consequences

* Quality measures must be defined and collected.
* Monitoring needs to surface changes to operators.

## Pros and Cons of the Options

### Model performance monitoring

* Good, because Tracks performance measures
* Good, because Directly addresses quality
* Bad, because Requires quality signals
* Sources: `d:22`, `v:22.1`

### No in-production monitoring

* Good, because No monitoring overhead
* Bad, because Drift is not visible
* Sources: `d:22`, `v:22.3`
