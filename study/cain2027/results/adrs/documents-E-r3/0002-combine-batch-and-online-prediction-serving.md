# Combine batch and online prediction serving

* System: Large-scale document classification

## Context and Problem Statement

Several teams consume classification results, while the brief does not specify how quickly each team needs them. The design space offers batch, online, and hybrid serving (d:5).

## Decision Drivers

* Multiple consuming teams
* Millions of daily predictions
* Unspecified result latency

## Considered Options

* Hybrid online/offline model serving (`v:5.5`)
* Data batch based model serving (`v:5.3`)
* Microservice based model serving (`v:5.1`)

## Decision Outcome

Chosen option: "Hybrid online/offline model serving" (`v:5.5`).

The hybrid option supports batch processing at high volume while leaving room for consumers that need online predictions. The checked design point had no warnings, but no combination was attested by sources.

### Consequences

* Define which consumers use each serving path.
* Maintain consistency across prediction access paths.

## Pros and Cons of the Options

### Hybrid online/offline model serving

* Good, because Supports batch and online access
* Good, because Accommodates varied consumers
* Bad, because Adds serving paths to operate
* Sources: `d:5`, `v:5.5`

### Data batch based model serving

* Good, because Processes large batches
* Good, because Writes results to storage
* Bad, because Results are not immediate
* Sources: `d:5`, `v:5.3`

### Microservice based model serving

* Good, because Real-time predictions
* Good, because Distributed service
* Bad, because Per-document requests at scale
* Sources: `d:5`, `v:5.1`
