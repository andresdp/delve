# Serve scores through a real-time microservice

* System: Card-fraud scoring service

## Context and Problem Statement

Fraud scores must be returned as part of transaction authorization. Scheduled batch scoring cannot meet that request path.

## Decision Drivers

* Real-time scores
* Peak availability

## Considered Options

* Microservice based model serving (`v:5.1`)
* Local service/API based model serving (`v:5.2`)
* Data batch based model serving (`v:5.3`)

## Decision Outcome

Chosen option: "Microservice based model serving" (`v:5.1`).

The design space describes this option as real-time delivery through a distributed service, which fits pre-authorization scoring. The batch rival point returned no warnings, but its scheduled processing does not meet the brief’s latency need.

### Consequences

* Scale and monitor the serving service during peaks.
* Account for service-call latency in the authorization path.

## Pros and Cons of the Options

### Microservice based model serving

* Good, because Real-time distributed service
* Bad, because Network and service operations
* Sources: `d:5`, `v:5.1`

### Local service/API based model serving

* Good, because Local API access
* Bad, because Deployment locality constraints
* Sources: `d:5`, `v:5.2`

### Data batch based model serving

* Good, because Scheduled scoring
* Bad, because Not request-time
* Sources: `d:5`, `v:5.3`
