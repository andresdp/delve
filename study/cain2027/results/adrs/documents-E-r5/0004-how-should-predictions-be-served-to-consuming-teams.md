# How should predictions be served to consuming teams?

* System: Large-scale document classification

## Context and Problem Statement

Several teams consume classification results. The brief does not require synchronous responses, so scheduled batch scoring and stored outputs are a suitable starting point.

## Decision Drivers

* multiple consuming teams
* high volume
* unspecified latency

## Considered Options

* Data batch based model serving (`v:5.3`)
* Microservice based model serving (`v:5.1`)
* Hybrid online/offline model serving (`v:5.5`)

## Decision Outcome

Chosen option: "Data batch based model serving" (`v:5.3`).

Batch serving matches the selected processing approach and gives multiple teams stored results to consume. The checked point had no warnings and no attesting sources.

### Consequences

* Define result storage and access contracts.
* Consumers may see results only after each scoring run.

## Pros and Cons of the Options

### Data batch based model serving

* Good, because writes results to storage
* Good, because fits scheduled workloads
* Bad, because results are not immediate
* Sources: `d:5`, `v:5.3`

### Microservice based model serving

* Good, because real-time predictions
* Good, because distributed service access
* Bad, because requires online serving capacity
* Sources: `d:5`, `v:5.1`

### Hybrid online/offline model serving

* Good, because supports online and batch use
* Good, because serves varied latency needs
* Bad, because operates two serving paths
* Sources: `d:5`, `v:5.5`
