# Monitor classification quality over time

* System: Large-scale document classification

## Context and Problem Statement

Operators need to see when classification quality drifts. The system therefore needs ongoing quality monitoring with an operator-visible signal.

## Decision Drivers

* Quality drift visibility
* Operator needs

## Considered Options

* Quality metrics and drift dashboard
* Periodic manual review

## Decision Outcome

Chosen option: "Quality metrics and drift dashboard".

A dashboard gives operators a recurring view of quality changes and makes drift easier to spot than periodic review alone.

### Consequences

* Quality indicators and thresholds need definition.
* Dashboard alerts require an operational owner.

## Pros and Cons of the Options

### Quality metrics and drift dashboard

* Good, because Visible trends
* Good, because Supports investigation
* Bad, because Needs quality signals

### Periodic manual review

* Good, because Human judgment
* Bad, because Delayed detection
* Bad, because Manual effort
