# Scheduled batch prediction deployment

*How should predictions be served?*

* System: Large-scale document classification

## Context and Problem Statement

Millions of documents arrive per day, and several teams consume classifications. The brief gives no per-document response-time requirement.

## Decision Drivers

* Daily volume
* Multiple consumers
* Unspecified latency

## Considered Options

* Scheduled batch prediction deployment (`v:31.3`)
* Online computation serving (`v:31.5`)

## Decision Outcome

Chosen option: "Scheduled batch prediction deployment" (`v:31.3`).

Scheduled batch scoring fits the stated daily volume and shared result consumption without an identified real-time need. The scalable pipeline patterns in “Architecting a Machine Learning Pipeline” and “Scalable Software and Big Data Architecture” support this option.

### Consequences

* Persist classifications for consuming teams.
* Set batch cadence and freshness expectations.
* Support replay when classification jobs fail.

## Pros and Cons of the Options

### Scheduled batch prediction deployment

* Good, because Writes results for consumers
* Good, because Supports batch throughput
* Bad, because Results arrive on a schedule
* Sources: `s02_p02`, `s02_p12`, `s02_p13`

### Online computation serving

* Good, because Fresh per-request results
* Good, because Supports interactive use
* Bad, because Requires online capacity
* Bad, because Latency sensitive
* Sources: `s02_p02`, `s04_p10`
