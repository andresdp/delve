# Data batch based model serving

*How should predictions be served?*

* System: Large-scale document classification

## Context and Problem Statement

Several teams consume classification results, and the brief specifies neither synchronous access nor a latency target. The design space includes scheduled batch output and real-time service options (d:5).

## Decision Drivers

* Team consumption
* Seasonal peak scale

## Considered Options

* Data batch based model serving (`v:5.3`)
* Microservice based model serving (`v:5.1`)

## Decision Outcome

Chosen option: "Data batch based model serving" (`v:5.3`).

Seasonal peak scale decides the choice given the lack of an immediate-response requirement. This gives up real-time access in favor of scheduled stored results.

### Consequences

* Consumers need access to the results store.
* Freshness follows the serving schedule.

## Pros and Cons of the Options

### Data batch based model serving

* Good, because Seasonal peak scale: write scheduled prediction batches to storage
* Bad, because Team consumption: results are available only after runs
* Sources: `d:5`, `v:5.3`

### Microservice based model serving

* Good, because Team consumption: teams can request real-time predictions
* Bad, because Seasonal peak scale: service capacity must absorb demand peaks
* Sources: `d:5`, `v:5.1`
