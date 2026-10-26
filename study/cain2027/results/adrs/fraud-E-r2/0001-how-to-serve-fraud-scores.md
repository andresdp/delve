# How to serve fraud scores?

* System: Card-fraud scoring service

## Context and Problem Statement

Each transaction needs a score before authorization, within tens of milliseconds, including during peaks.

## Decision Drivers

* Low latency
* Peak availability

## Considered Options

* Microservice based model serving (`v:5.1`)
* Local service/API based model serving (`v:5.2`)
* Data batch based model serving (`v:5.3`)

## Decision Outcome

Chosen option: "Microservice based model serving" (`v:5.1`).

The design space describes microservice serving as real-time distributed scoring, which fits transaction-time scoring and peak demand better than batch serving (d:5, v:5.1, v:5.3). The checked combination had no warnings, though it was unattested; its rival also had no warnings and was unattested.

### Consequences

* Scale scoring service independently.
* Keep the authorization path dependent on scoring availability.

## Pros and Cons of the Options

### Microservice based model serving

* Good, because Online scoring
* Good, because Independent scaling
* Bad, because Network hop
* Bad, because Service dependency
* Sources: `d:5`, `v:5.1`

### Local service/API based model serving

* Good, because Online scoring
* Good, because Fewer network hops
* Bad, because Tighter application coupling
* Bad, because Scaling tied to callers
* Sources: `d:5`, `v:5.2`

### Data batch based model serving

* Good, because Scheduled processing
* Good, because Writes scores to storage
* Bad, because Not transaction-time scoring
* Sources: `d:5`, `v:5.3`
