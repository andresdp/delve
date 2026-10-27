# Track classification quality over time

* System: Large-scale document classification

## Context and Problem Statement

Operators need to see when classification quality drifts. The system therefore needs to collect quality signals and present their trends to operators.

## Decision Drivers

* Quality drift visibility
* Operator oversight

## Considered Options

* Quality metrics with trend dashboards
* Periodic manual quality reviews

## Decision Outcome

Chosen option: "Quality metrics with trend dashboards".

Continuous metrics and trends give operators a timely view of quality changes at this scale.

### Consequences

* Quality measurements and reference labels are needed.
* Drift thresholds and response procedures remain to be set.

## Pros and Cons of the Options

### Quality metrics with trend dashboards

* Good, because Visible trends
* Good, because Supports alerting
* Bad, because Needs quality signals
* Bad, because Thresholds require tuning

### Periodic manual quality reviews

* Good, because Human judgment
* Good, because Low instrumentation
* Bad, because Slow detection
* Bad, because Labor intensive
