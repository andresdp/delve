# Microservice based model serving

*How to serve scores?*

* System: Card-fraud scoring service

## Context and Problem Statement

Scores must return online before authorization, including during transaction peaks. The design space distinguishes real-time distributed service and local service patterns (d:5).

## Decision Drivers

* online scoring
* peak traffic

## Considered Options

* Microservice based model serving (`v:5.1`)
* Local service/API based model serving (`v:5.2`)

## Decision Outcome

Chosen option: "Microservice based model serving" (`v:5.1`).

A distributed real-time scoring service supports independent capacity management for peaks; its latency must be validated against the brief’s tens-of-milliseconds budget (d:5, d:26).

### Consequences

* Provide redundant service capacity.
* Include network and feature lookup time in latency budgets.

## Pros and Cons of the Options

### Microservice based model serving

* Good, because Real-time interface
* Good, because Independent scaling
* Bad, because Network overhead
* Bad, because Service dependency
* Sources: `d:5`, `v:5.1`

### Local service/API based model serving

* Good, because Local call path
* Good, because Lower network overhead
* Bad, because Tighter coupling
* Bad, because Shared capacity
* Sources: `d:5`, `v:5.2`
