# Serve transaction scores through a real-time model service

* System: Card-fraud scoring service

## Context and Problem Statement

Fraud scores must be available before authorization, so scheduled batch output cannot meet the brief. The workspace distinguishes distributed microservice serving from local service/API serving. (d:5)

## Decision Drivers

* Pre-authorization scoring
* Tens of milliseconds
* Peak availability

## Considered Options

* Microservice based model serving (`v:5.1`)
* Local service/API based model serving (`v:5.2`)
* Data batch based model serving (`v:5.3`)

## Decision Outcome

Chosen option: "Microservice based model serving" (`v:5.1`).

Real-time distributed serving matches the authorization deadline and can scale apart from other application components during peaks. The point check returned no warnings, though it was unattested. (d:5, v:5.1)

### Consequences

* The request path depends on network and service health.
* Capacity planning must cover peak transaction load.

## Pros and Cons of the Options

### Microservice based model serving

* Good, because Real-time scores
* Good, because Independent capacity
* Bad, because Network dependency
* Bad, because Distributed operations
* Sources: `d:5`, `v:5.1`

### Local service/API based model serving

* Good, because Real-time scores
* Good, because Local call path
* Bad, because Less independent scaling
* Bad, because Shares host resources
* Sources: `d:5`, `v:5.2`

### Data batch based model serving

* Good, because Scheduled processing
* Good, because Writes scores to storage
* Bad, because Not available per transaction
* Bad, because Stale results
* Sources: `d:5`, `v:5.3`
