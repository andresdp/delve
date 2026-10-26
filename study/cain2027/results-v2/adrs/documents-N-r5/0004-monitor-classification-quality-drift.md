# Monitor classification quality drift

* System: Large-scale document classification

## Context and Problem Statement

Operators need to see when classification quality drifts. Monitoring should expose changes in quality over time, rather than relying only on service health signals.

## Decision Drivers

* Quality drift visibility

## Considered Options

* Track labeled quality metrics over time
* Track input and prediction distributions

## Decision Outcome

Chosen option: "Track labeled quality metrics over time".

Quality drift visibility decides the choice: labeled metrics directly measure classification outcomes. This gives up immediate signals when labels are delayed and requires representative labels.

### Consequences

* A labeled sample or outcomes feed is needed.
* Metric definitions and alert thresholds remain to be set.

## Pros and Cons of the Options

### Track labeled quality metrics over time

* Good, because Quality drift visibility: measures outcome quality
* Good, because Quality drift visibility: supports trend comparison
* Bad, because Operations: depends on representative labeled data
* Bad, because Latency: labels may arrive after predictions

### Track input and prediction distributions

* Good, because Quality drift visibility: signals distribution changes quickly
* Good, because Operations: no labels required
* Bad, because Quality drift visibility: distribution change does not prove quality loss
* Bad, because Operations: thresholds can produce noisy alerts
