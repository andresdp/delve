# Prediction mode

* System: Card-fraud scoring service

## Context and Problem Statement

Every card must be scored before authorization, so predictions must be computed during the transaction request.

## Decision Drivers

* Latency: tens of milliseconds
* Availability: peak traffic

## Considered Options

* Online computation serving (`v:31.5`)
* Precomputed offline serving (`v:31.6`)

## Decision Outcome

Chosen option: "Online computation serving" (`v:31.5`).

Online computation best serves the required per-transaction decision within tens of milliseconds; it gives up the simpler, prepared path of offline scoring. The sources “Architecting a Machine Learning Pipeline” and “System Architectures for Personalization and Recommendation” describe online and precomputed approaches.

### Consequences

* Serve each transaction on a live scoring path.
* Keep feature retrieval and model execution within the latency budget.

## Pros and Cons of the Options

### Online computation serving

* Good, because Latency: scores current request context
* Bad, because Availability: depends on live serving path
* Sources: `s02_p02`, `s02_p13`, `s04_p10`

### Precomputed offline serving

* Good, because Availability: prepared results can be served quickly
* Bad, because Latency: may miss the transaction's current context
* Sources: `s02_p13`, `s12_p02`, `s19_p08`
