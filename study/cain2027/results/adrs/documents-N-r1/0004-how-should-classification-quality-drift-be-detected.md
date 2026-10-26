# How should classification quality drift be detected?

* System: Large-scale document classification

## Context and Problem Statement

Operators need to see when classification quality drifts. Detection requires comparing current behavior with a reference or quality signal over time.

## Decision Drivers

* Quality drift visibility
* Operator awareness

## Considered Options

* Monitor labeled outcomes against a quality baseline
* Monitor input and prediction distributions

## Decision Outcome

Chosen option: "Monitor labeled outcomes against a quality baseline".

Labeled outcomes provide a direct quality signal for detecting drift. Distribution monitoring can complement this, but alone it cannot establish that classification quality has worsened.

### Consequences

* A labeling or outcome feedback path is required.
* Operators need thresholds and alert handling.

## Pros and Cons of the Options

### Monitor labeled outcomes against a quality baseline

* Good, because Measures classification quality
* Good, because Supports trend detection
* Bad, because Needs reliable labels
* Bad, because Feedback may be delayed

### Monitor input and prediction distributions

* Good, because Can detect shifts quickly
* Good, because Does not require immediate labels
* Bad, because Indirect quality signal
* Bad, because May produce false alarms
