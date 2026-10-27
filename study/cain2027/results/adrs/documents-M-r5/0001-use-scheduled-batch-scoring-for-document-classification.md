# Use scheduled batch scoring for document classification

* System: Large-scale document classification

## Context and Problem Statement

The system classifies millions of documents daily, and several teams consume its results. The brief gives no requirement for request-time predictions.

## Decision Drivers

* High daily volume
* Multiple result consumers

## Considered Options

* Scheduled batch prediction deployment (`v:31.3`)
* Online computation serving (`v:31.5`)

## Decision Outcome

Chosen option: "Scheduled batch prediction deployment" (`v:31.3`).

It fits the stated volume and shared result consumption. Netflix’s “System Architectures for Personalization and Recommendation” and “Scalable Software and Big Data Architecture” describe scheduled scoring and stored results; the checked rival point using online serving was attested by one source, while this combination was unattested.

### Consequences

* Consumers read completed scoring outputs.
* Classification freshness depends on the scoring schedule.

## Pros and Cons of the Options

### Scheduled batch prediction deployment

* Good, because Scales scoring in scheduled runs
* Good, because Writes results for downstream use
* Bad, because Results are not immediate
* Sources: `s02_p02`, `s12_p02`, `s15_p04`

### Online computation serving

* Good, because Uses current request context
* Good, because Provides predictions on demand
* Bad, because Adds online serving complexity
* Bad, because Does not match a stated latency need
* Sources: `s04_p10`, `s12_p03`
