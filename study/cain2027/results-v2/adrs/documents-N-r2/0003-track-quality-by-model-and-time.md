# Track quality by model and time

* System: Large-scale document classification

## Context and Problem Statement

Operators need to see when classification quality drifts. The brief does not specify the source or timeliness of quality labels.

## Decision Drivers

* Quality: detect drift
* Operations: operator visibility

## Considered Options

* Monitor labeled outcomes by model version
* Monitor input and prediction distributions

## Decision Outcome

Chosen option: "Monitor labeled outcomes by model version".

Detecting classification quality drift decides the choice; outcome measurement gives stronger evidence but sacrifices timeliness when labels arrive late.

### Consequences

* Label collection and linkage are required.
* Operators need thresholds and an alert workflow.

## Pros and Cons of the Options

### Monitor labeled outcomes by model version

* Good, because Quality: measures classification outcomes
* Good, because Operations: supports version comparisons
* Bad, because Latency: depends on label arrival
* Bad, because Data: requires trustworthy labels

### Monitor input and prediction distributions

* Good, because Latency: signals without labels
* Good, because Operations: detects distribution shifts
* Bad, because Quality: proxy can miss errors
* Bad, because Quality: shifts may be harmless
