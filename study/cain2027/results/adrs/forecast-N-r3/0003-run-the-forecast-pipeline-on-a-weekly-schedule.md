# Run the forecast pipeline on a weekly schedule

* System: Retail demand forecasting

## Context and Problem Statement

Demand is forecast weekly, and the production run must complete reliably without slowing model development.

## Decision Drivers

* Weekly run
* Safe production changes

## Considered Options

* Scheduled batch pipeline
* Manual execution

## Decision Outcome

Chosen option: "Scheduled batch pipeline".

A scheduled batch run matches the weekly forecast cadence and removes routine execution from the data scientists' manual workload.

### Consequences

* Configure and monitor the weekly trigger.
* Failed runs need a recovery procedure.

## Pros and Cons of the Options

### Scheduled batch pipeline

* Good, because Matches forecast cadence
* Good, because Isolates run from development
* Bad, because Results update on schedule
* Bad, because Needs run monitoring

### Manual execution

* Good, because Simple initial setup
* Good, because Operator controls timing
* Bad, because Human-dependent cadence
* Bad, because More run inconsistency
