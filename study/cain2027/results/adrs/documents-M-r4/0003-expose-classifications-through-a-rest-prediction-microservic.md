# Expose classifications through a REST prediction microservice

* System: Large-scale document classification

## Context and Problem Statement

Several teams consume classification results, so the system needs a consistent integration boundary. The brief does not specify their existing interfaces.

## Decision Drivers

* Multiple consumer teams
* Shared classification results

## Considered Options

* REST prediction microservice (`v:29.1`)
* gRPC model interface (`v:29.7`)

## Decision Outcome

Chosen option: "REST prediction microservice" (`v:29.1`).

REST provides an API boundary for the teams consuming results, without assuming they share a particular runtime. The checked design point had no warnings but was unattested as a complete combination.

### Consequences

* The API contract and versioning need definition.
* Batch result access patterns remain to be specified.

## Pros and Cons of the Options

### REST prediction microservice

* Good, because API-backed integration
* Good, because Separates consumers from model runtime
* Bad, because Requires service operations
* Sources: `s01_p05`, `s02_p10`, `s16_p03`

### gRPC model interface

* Good, because Supports independently deployed models
* Good, because Clear service interface
* Bad, because Consumer compatibility is unknown
* Sources: `s19_p14`, `s21_p10`
