# Prediction serving mode

* System: Card-fraud scoring service

## Context and Problem Statement

Every transaction needs a score before authorization, so scoring must use current request context within tens of milliseconds.

## Decision Drivers

* Tens-of-ms latency
* Fresh transaction context
* Peak availability

## Considered Options

* Online computation serving (`v:31.5`)
* Scheduled batch prediction deployment (`v:31.3`)
* Precomputed-result fallback (`v:31.7`)

## Decision Outcome

Chosen option: "Online computation serving" (`v:31.5`).

Request-time scoring best fits transaction authorization. The checked design point had no warnings, though no sources attest to the full combination; the batch rival also had no warnings and was likewise unattested.

### Consequences

* Feature retrieval and scoring must fit the latency budget.
* Define fallback behavior for unavailable or slow dependencies.

## Pros and Cons of the Options

### Online computation serving

* Good, because Uses current context
* Good, because Fits request-time scoring
* Bad, because Depends on timely feature retrieval
* Sources: `s02_p02`, `s04_p10`

### Scheduled batch prediction deployment

* Good, because Scores ahead of demand
* Good, because Supports batch workloads
* Bad, because Results may be stale
* Bad, because Does not score each live transaction
* Sources: `s02_p02`, `s19_p14`

### Precomputed-result fallback

* Good, because Can preserve availability
* Good, because Avoids slow online work
* Bad, because May return stale results
* Bad, because Needs fallback data
* Sources: `s09_p11`, `s12_p03`
