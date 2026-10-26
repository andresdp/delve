# Metrics with sampled case review

*How should the system expose quality drift?*

* System: Large-scale document classification

## Context and Problem Statement

Operators need to see when classification quality drifts. Input and output metrics can flag changes, while reviewed examples help check whether quality has actually changed.

## Decision Drivers

* Quality drift: operator visibility
* High volume: millions per day

## Considered Options

* Aggregate input and output metrics
* Sampled case review
* Metrics with sampled case review

## Decision Outcome

Chosen option: "Metrics with sampled case review".

Operator visibility decides the choice: metrics can surface broad changes and sampled reviews provide case-level evidence. The trade-off is ongoing review effort, with samples unable to represent every case.

### Consequences

* Choose metrics and sampling rules.
* Provide operators with a review workflow.
* Plan for review effort as volume changes.

## Pros and Cons of the Options

### Aggregate input and output metrics

* Good, because High volume: inexpensive to compute at scale
* Bad, because Quality drift: metrics are indirect quality signals

### Sampled case review

* Good, because Quality drift: operators inspect actual classifications
* Bad, because High volume: samples cover only a fraction of cases

### Metrics with sampled case review

* Good, because Quality drift: combines broad signals with case inspection
* Bad, because High volume: review requires sampling and operator effort
