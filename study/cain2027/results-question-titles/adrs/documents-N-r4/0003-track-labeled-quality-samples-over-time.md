# Track labeled quality samples over time

*How should classification quality drift be detected?*

* System: Large-scale document classification

## Context and Problem Statement

Operators need visibility when classification quality drifts. The system therefore needs ongoing quality signals and a way to surface changes for review.

## Decision Drivers

* Quality drift visibility
* Operator oversight

## Considered Options

* Monitor operational metrics only
* Track labeled quality samples over time

## Decision Outcome

Chosen option: "Track labeled quality samples over time".

Operational metrics alone cannot show whether claim types are being assigned correctly. Tracking labeled samples over time gives operators a direct quality signal for detecting drift.

### Consequences

* Arrange a source of reviewed labels.
* Define alert thresholds and review ownership.

## Pros and Cons of the Options

### Monitor operational metrics only

* Good, because Low measurement overhead
* Good, because Reuses service metrics
* Bad, because Does not measure correctness
* Bad, because Quality regressions may go unseen

### Track labeled quality samples over time

* Good, because Measures classification quality
* Good, because Supports trend alerts
* Bad, because Needs reviewed labels
* Bad, because Feedback may arrive late
