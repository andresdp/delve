# Monitor input drift and model quality in production

* System: Large-scale document classification

## Context and Problem Statement

Operators need to see when classification quality drifts. The brief does not say whether labels arrive promptly, so input drift can be observed before labeled quality measures are available.

## Decision Drivers

* Quality drift visibility
* Operational awareness

## Considered Options

* Input and feature-drift monitoring (`v:6.2`)
* Real-time prediction-quality monitoring (`v:6.1`)
* Passive production operation (`v:6.4`)

## Decision Outcome

Chosen option: "Input and feature-drift monitoring" (`v:6.2`).

Input-drift monitoring addresses the stated need for drift visibility without assuming timely ground-truth labels. In the design space, monitoring practices are alternatives within one dimension; the checked point therefore flagged combining drift monitoring with a retraining trigger as two values of that dimension.

### Consequences

* Surface drift signals to operators.
* Set investigation thresholds and ownership.

## Pros and Cons of the Options

### Input and feature-drift monitoring

* Good, because Detects changing inputs
* Good, because Does not require immediate labels
* Bad, because Drift does not prove quality loss
* Sources: `s04_p03`, `s06_p02`

### Real-time prediction-quality monitoring

* Good, because Tracks measured quality
* Good, because Supports rapid detection
* Bad, because Depends on label availability
* Sources: `s01_p06`, `s04_p12`

### Passive production operation

* Good, because Lower monitoring effort
* Bad, because No active drift visibility
* Sources: `s13_p10`
