# Persist features in a feature store

* System: Card-fraud scoring service

## Context and Problem Statement

Scoring needs access to transaction features during the live request. Feature persistence is a relevant design choice for the selected real-time serving approach.

## Decision Drivers

* Fast feature access
* Scoring inputs

## Considered Options

* Feature store (`v:4.1`)
* Store features in data stores without specific support (`v:4.2`)

## Decision Outcome

Chosen option: "Feature store" (`v:4.1`).

The feature store is the more directly aligned option for serving features alongside the real-time scoring service. The design point reported no warnings, though the workspace provides no evidence about latency or operational tradeoffs for this choice.

### Consequences

* Operate a feature persistence and access path.
* Verify that feature retrieval fits the scoring latency budget.

## Pros and Cons of the Options

### Feature store

* Good, because Purpose-built feature access
* Bad, because Additional system to operate
* Sources: `d:4`, `v:4.1`

### Store features in data stores without specific support

* Good, because Uses existing data stores
* Bad, because Feature-specific behavior unspecified
* Sources: `d:4`, `v:4.2`
