# Inference in the scoring service

*Where should model inference run?*

* System: Card-fraud scoring service

## Context and Problem Statement

The scoring service must return results within tens of milliseconds. Inference placement affects network overhead and how independently model capacity can be scaled.

## Decision Drivers

* Tens-of-milliseconds latency
* Peak availability

## Considered Options

* Inference in the scoring service
* Separate model-serving service

## Decision Outcome

Chosen option: "Inference in the scoring service".

Co-located inference avoids an extra network call on a tight latency path. This favors predictable response time, while limiting independent scaling of model-serving capacity.

### Consequences

* Scoring and inference capacity scale together.
* Model runtime changes require scoring-service deployment.

## Pros and Cons of the Options

### Inference in the scoring service

* Good, because Avoids inference network hop
* Good, because One request boundary
* Bad, because Couples model runtime to service

### Separate model-serving service

* Good, because Independent scaling
* Good, because Isolated model runtime
* Bad, because Adds network hop
* Bad, because Adds service dependency
