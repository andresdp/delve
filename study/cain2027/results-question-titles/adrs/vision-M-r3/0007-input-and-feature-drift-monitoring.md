# Input and feature-drift monitoring

*What should production monitoring cover?*

* System: On-device visual inspection

## Context and Problem Statement

Devices may be disconnected, while inspection quality and input conditions can change. Monitoring should include changes in inputs and service health; the brief does not state that labels are available at inference time.

## Decision Drivers

* Intermittent network
* Model quality
* Small team

## Considered Options

* Input and feature-drift monitoring (`v:6.2`)
* Real-time prediction-quality monitoring (`v:6.1`)

## Decision Outcome

Chosen option: "Input and feature-drift monitoring" (`v:6.2`).

Choose input and feature monitoring as the feasible initial signal when network access and fresh ground truth are uncertain. “Productionizing Machine Learning with a Microservices Architecture” and “MLOps: Continuous delivery and automation pipelines in machine learning” support drift monitoring; monitoring choices can be combined because this dimension has zero exclusivity.

### Consequences

* Collect device observations for later central review.
* Add quality monitoring when labels become available.

## Pros and Cons of the Options

### Input and feature-drift monitoring

* Good, because Surfaces input changes
* Good, because Can run without immediate labels
* Bad, because Drift does not prove quality loss
* Bad, because Requires baselines and thresholds
* Sources: `s04_p03`, `s04_p12`, `s06_p02`

### Real-time prediction-quality monitoring

* Good, because Measures prediction quality
* Good, because Can expose degradation
* Bad, because Needs timely ground truth
* Bad, because Connectivity may delay reporting
* Sources: `s24_p01`, `s24_p07`
