# Expose scoring through a REST prediction microservice

* System: Card-fraud scoring service

## Context and Problem Statement

The authorization system needs a request-response interface to obtain a fraud score. A service boundary allows the scorer to be operated independently.

## Decision Drivers

* Synchronous authorization
* Independent model serving

## Considered Options

* REST prediction microservice (`v:29.1`)
* gRPC model interface (`v:29.7`)

## Decision Outcome

Chosen option: "REST prediction microservice" (`v:29.1`).

A REST prediction service provides the synchronous application interface described in “How to power up your product by machine learning with python microservice, pt. 1.” The brief does not specify a client ecosystem that would favor gRPC.

### Consequences

* Define request and response contracts for authorization.
* Include service overhead in latency measurements.

## Pros and Cons of the Options

### REST prediction microservice

* Good, because Direct application integration
* Good, because Independent deployment
* Bad, because Network overhead
* Bad, because Requires API operations
* Sources: `s01_p05`, `s01_p08`, `s02_p05`

### gRPC model interface

* Good, because Supports independent model service
* Good, because Typed service contract
* Bad, because Requires client compatibility
* Bad, because Adds interface management
* Sources: `s19_p14`, `s21_p10`
