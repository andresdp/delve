# Where should model inference run?

* System: Card-fraud scoring service

## Context and Problem Statement

Inference is on the authorization path, so model execution contributes directly to the response time.

## Decision Drivers

* Tens-of-ms latency
* Pre-authorization scoring

## Considered Options

* In-process model runtime
* Separate model-serving service

## Decision Outcome

Chosen option: "In-process model runtime".

Running inference in the scoring service avoids an extra network call on a latency-sensitive path.

### Consequences

* Model and service releases must be coordinated.
* Inference resource use can affect request handling.

## Pros and Cons of the Options

### In-process model runtime

* Good, because Avoids network hop
* Good, because Simple request path
* Bad, because Model runtime shares service resources
* Bad, because Model rollout tied to service

### Separate model-serving service

* Good, because Independent model deployment
* Good, because Isolated inference resources
* Bad, because Adds network hop
* Bad, because Extra dependency
