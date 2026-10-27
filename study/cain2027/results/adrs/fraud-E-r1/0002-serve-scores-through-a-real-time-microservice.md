# Serve scores through a real-time microservice

* System: Card-fraud scoring service

## Context and Problem Statement

The payment flow needs a score for each transaction before authorization, so scheduled batch scoring does not fit.

## Decision Drivers

* Tens of milliseconds
* Per-transaction scores
* Peak availability

## Considered Options

* Microservice based model serving (`v:5.1`)
* Local service/API based model serving (`v:5.2`)
* Data batch based model serving (`v:5.3`)

## Decision Outcome

Chosen option: "Microservice based model serving" (`v:5.1`).

Real-time service delivery matches the authorization deadline; the batch alternative cannot return scores in that flow (d:5, v:5.1, v:5.3).

### Consequences

* The authorization path depends on the scoring service.
* Peak capacity and response time need operational attention.

## Pros and Cons of the Options

### Microservice based model serving

* Good, because Real-time scoring
* Good, because Distributed service
* Bad, because Network call in scoring path
* Sources: `d:5`, `v:5.1`

### Local service/API based model serving

* Good, because Local access
* Good, because Avoids remote service hop
* Bad, because Less deployment separation
* Sources: `d:5`, `v:5.2`

### Data batch based model serving

* Good, because Scheduled processing
* Good, because Writes scores to storage
* Bad, because Does not meet per-transaction timing
* Sources: `d:5`, `v:5.3`
