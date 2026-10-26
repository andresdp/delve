# How should classification quality drift be surfaced?

* System: Large-scale document classification

## Context and Problem Statement

Operators need to see when classification quality drifts. This requires ongoing quality signals and a way to make changes visible to operators.

## Decision Drivers

* Operators need drift visibility

## Considered Options

* Monitor labeled outcomes over time
* Monitor input and prediction statistics

## Decision Outcome

Chosen option: "Monitor labeled outcomes over time".

Operator visibility into classification quality decides the choice: labeled outcomes measure quality directly. This gives up early warning when labels are delayed or unavailable.

### Consequences

* Label availability affects detection delay.
* Operators need a view of quality over time.

## Pros and Cons of the Options

### Monitor labeled outcomes over time

* Good, because Drift visibility: measures observed quality
* Bad, because Drift visibility: depends on labeled outcomes

### Monitor input and prediction statistics

* Good, because Drift visibility: signals can be available early
* Bad, because Drift visibility: proxy signals do not confirm quality
