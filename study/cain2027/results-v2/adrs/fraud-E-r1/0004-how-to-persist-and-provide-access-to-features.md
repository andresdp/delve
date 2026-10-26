# How to persist and provide access to features?

* System: Card-fraud scoring service

## Context and Problem Statement

The scorer needs transaction features during the online request, and auditors need to know which features contributed to a score (d:4, d:22).

## Decision Drivers

* Tens-of-ms latency
* Audit traceability

## Considered Options

* Feature store (`v:4.1`)
* Store features in data stores without specific support (`v:4.2`)

## Decision Outcome

Chosen option: "Feature store" (`v:4.1`).

Tens-of-ms latency decides the choice: a feature store gives the serving path a focused feature access pattern; it still requires recording the feature values or references for each score.

### Consequences

* Design online feature access for the latency budget.
* Capture the features used with each scored transaction.

## Pros and Cons of the Options

### Feature store

* Good, because Latency: dedicated feature access
* Bad, because Audit traceability: requires recorded feature references
* Sources: `d:4`, `v:4.1`

### Store features in data stores without specific support

* Good, because Audit traceability: use existing storage
* Bad, because Latency: access may vary across stores
* Sources: `d:4`, `v:4.2`
