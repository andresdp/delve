# How should classification quality drift be surfaced?

* System: Large-scale document classification

## Context and Problem Statement

Operators need to see when classification quality drifts. The brief does not specify the available quality signals or alerting thresholds.

## Decision Drivers

* Quality drift visibility
* Operator needs

## Considered Options

* Quality monitoring dashboard with alerts
* Periodic manual quality reports

## Decision Outcome

Chosen option: "Quality monitoring dashboard with alerts".

A dashboard with alerts gives operators ongoing visibility and can surface changes sooner than periodic reports, provided suitable quality signals are established.

### Consequences

* Quality signals and alert thresholds must be defined.
* Operators need a process to investigate detected drift.

## Pros and Cons of the Options

### Quality monitoring dashboard with alerts

* Good, because Makes trends visible
* Good, because Can notify operators
* Bad, because Needs quality signals
* Bad, because Thresholds require tuning

### Periodic manual quality reports

* Good, because Simple initial process
* Good, because Supports human review
* Bad, because Slower detection
* Bad, because Requires recurring effort
