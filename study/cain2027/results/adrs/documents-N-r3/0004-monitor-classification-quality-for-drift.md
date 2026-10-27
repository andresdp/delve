# Monitor classification quality for drift

* System: Large-scale document classification

## Context and Problem Statement

Operators need to see when classification quality drifts, making ongoing quality monitoring necessary.

## Decision Drivers

* Drift visibility
* Operator awareness

## Considered Options

* Quality monitoring with operator alerts
* Periodic manual review

## Decision Outcome

Chosen option: "Quality monitoring with operator alerts".

Continuous monitoring can surface quality changes to operators sooner than periodic manual review.

### Consequences

* Requires representative quality measurements
* Operators need a response process

## Pros and Cons of the Options

### Quality monitoring with operator alerts

* Good, because Drift visibility
* Good, because Supports timely response
* Bad, because Needs quality signals
* Bad, because Alert tuning required

### Periodic manual review

* Good, because Human judgment
* Good, because Simple initial setup
* Bad, because Slow detection
* Bad, because Review effort grows with volume
