# Monitor service health and data quality in production

* System: Large-scale document classification

## Context and Problem Statement

Operators need to see when classification quality drifts. Monitoring data quality and service health provides operational context for investigating such changes.

## Decision Drivers

* Detect quality drift
* Operator visibility

## Considered Options

* Service-health and data-quality monitoring (`v:6.23`)
* Real-time prediction-quality monitoring (`v:6.1`)

## Decision Outcome

Chosen option: "Service-health and data-quality monitoring" (`v:6.23`).

This option covers data shifts alongside service health, matching the drift visibility and operator needs. The design point check had no warnings; it does not attest this whole system combination.

### Consequences

* Define drift indicators and alert thresholds.
* Prediction-quality metrics and their label availability need separate definition.

## Pros and Cons of the Options

### Service-health and data-quality monitoring

* Good, because Tracks data shifts and quality
* Good, because Includes service health
* Bad, because Does not alone define quality metrics
* Sources: `s04_p02`, `s06_p02`, `s22_p04`

### Real-time prediction-quality monitoring

* Good, because Tracks prediction quality
* Good, because Supports prompt detection
* Bad, because Requires timely labels
* Bad, because Does not alone cover service health
* Sources: `s04_p12`, `s06_p06`, `s23_p03`
