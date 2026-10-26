# Track classification quality by model and prompt version

* System: Large-scale document classification

## Context and Problem Statement

Operators need to see when quality drifts. Recording the model and prompt version with results makes observed changes traceable to classifier changes.

## Decision Drivers

* Detect quality drift
* Millions of documents per day

## Considered Options

* Versioned results with drift dashboards and alerts
* Monitor only aggregate operational metrics

## Decision Outcome

Chosen option: "Versioned results with drift dashboards and alerts".

The need to detect quality drift decides in favor of quality monitoring and version attribution; this requires suitable quality signals, which the brief does not define.

### Consequences

* Persist model and prompt versions with each result.
* Define drift thresholds and alert ownership.

## Pros and Cons of the Options

### Versioned results with drift dashboards and alerts

* Good, because Drift: relate changes to model versions
* Good, because Scale: aggregate quality signals
* Bad, because Drift: needs quality signals or review labels

### Monitor only aggregate operational metrics

* Good, because Scale: low monitoring overhead
* Bad, because Drift: misses quality degradation
* Bad, because Drift: cannot attribute changes
