# Online computation serving

*When should transaction predictions be computed?*

* System: Card-fraud scoring service

## Context and Problem Statement

A fraud score must reflect the current transaction and be returned before authorization. Periodic predictions cannot provide that request-time freshness.

## Decision Drivers

* Current transaction context
* Authorization-time response

## Considered Options

* Online computation serving (`v:31.5`)
* Precomputed offline serving (`v:31.6`)

## Decision Outcome

Chosen option: "Online computation serving" (`v:31.5`).

Request-time computation fits transaction-specific fraud scoring. “Architecting a Machine Learning Pipeline” and “Productionizing Machine Learning with a Microservices Architecture” describe online serving; the design point check returned no warnings, though the combination was unattested.

### Consequences

* Keep request-path feature retrieval within the latency budget.
* Online dependencies affect scoring availability.

## Pros and Cons of the Options

### Online computation serving

* Good, because Uses current context
* Good, because Returns score per request
* Bad, because Latency depends on online dependencies
* Sources: `s02_p02`, `s04_p10`

### Precomputed offline serving

* Good, because Fast result lookup
* Good, because Moves computation off request path
* Bad, because Can become stale
* Bad, because Cannot score unseen transactions
* Sources: `s12_p02`
