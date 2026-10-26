# Production monitoring

* System: Card-fraud scoring service

## Context and Problem Statement

The system must keep serving at peak and later explain which features were used. Monitoring inputs and feature behavior can reveal changes that threaten score quality or indicate a changed scoring context.

## Decision Drivers

* Peak availability
* Audit traceability

## Considered Options

* Input and feature-drift monitoring (`v:6.2`)
* Service-health and data-quality monitoring (`v:6.23`)
* Passive production operation (`v:6.4`)

## Decision Outcome

Chosen option: "Input and feature-drift monitoring" (`v:6.2`).

Audit traceability decides in favor of monitoring feature inputs and their changes. This requires operational effort; monitoring alone does not prove which exact feature values produced an individual score.

### Consequences

* Track feature schemas and distributions in production.
* Store per-score feature identifiers with the model version.

## Pros and Cons of the Options

### Input and feature-drift monitoring

* Good, because Audit traceability: detects feature changes
* Good, because Peak availability: surfaces input anomalies
* Bad, because Peak availability: monitoring adds operational work
* Sources: `s04_p03`, `s06_p02`

### Service-health and data-quality monitoring

* Good, because Peak availability: tracks latency and uptime
* Good, because Audit traceability: observes data quality
* Bad, because Audit traceability: does not by itself link each score to its features
* Sources: `s04_p02`, `s22_p04`

### Passive production operation

* Good, because Peak availability: no monitoring load
* Bad, because Peak availability: failures may go unseen
* Bad, because Audit traceability: no active visibility
