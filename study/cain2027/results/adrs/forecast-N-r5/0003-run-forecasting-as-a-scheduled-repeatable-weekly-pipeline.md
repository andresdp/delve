# Run forecasting as a scheduled, repeatable weekly pipeline

* System: Retail demand forecasting

## Context and Problem Statement

Forecasts are needed weekly, and the pipeline is owned end to end by a small team. A repeatable pipeline makes that recurring work operationally manageable.

## Decision Drivers

* Weekly run
* Three-person team
* End-to-end ownership

## Considered Options

* Scheduled pipeline with explicit stages
* Manual scripts run each week

## Decision Outcome

Chosen option: "Scheduled pipeline with explicit stages".

A weekly recurring task benefits from consistent execution and clear failure points, especially with a small team responsible for the whole pipeline.

### Consequences

* Stages need defined inputs and outputs.
* The team must maintain scheduling and run visibility.

## Pros and Cons of the Options

### Scheduled pipeline with explicit stages

* Good, because Repeatable execution
* Good, because Failures are visible
* Bad, because Needs orchestration
* Bad, because Requires stage contracts

### Manual scripts run each week

* Good, because Quick to start
* Good, because Flexible
* Bad, because Error-prone repetition
* Bad, because Harder handoffs
