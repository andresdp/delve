# What should production monitoring cover?

* System: On-device visual inspection

## Context and Problem Statement

Devices may lack network access, while production images and predictions can change between weekly training runs. Monitoring and retraining triggers are represented as combinable practices in this low-exclusivity dimension.

## Decision Drivers

* Offline operation
* Safe weekly updates
* Small team

## Considered Options

* Input and feature-drift monitoring (`v:6.2`)
* Service-health and data-quality monitoring (`v:6.23`)
* Passive production operation (`v:6.4`)

## Decision Outcome

Chosen option: "Input and feature-drift monitoring" (`v:6.2`).

Safe weekly updates decide the choice: observe input shifts between training runs, accepting the work of maintaining baselines. “MLOps: Continuous delivery and automation pipelines in machine learning” and “Machine Learning Monitoring: What It Is, and What We Are Missing” support data and feature monitoring; collect summaries locally and synchronize when devices reconnect.

### Consequences

* Buffer monitoring data locally during network outages.
* Define a lightweight path to review drift and image quality changes.

## Pros and Cons of the Options

### Input and feature-drift monitoring

* Good, because Offline operation: drift summaries can be collected locally
* Bad, because Small team: baselines and alerts need maintenance
* Sources: `s06_p08`, `s23_p03`

### Service-health and data-quality monitoring

* Good, because Safe weekly updates: surfaces runtime and input problems
* Bad, because Offline operation: centralized visibility is delayed
* Sources: `s04_p02`, `s22_p11`

### Passive production operation

* Good, because Small team: minimal monitoring overhead
* Bad, because Safe weekly updates: failures may stay unnoticed
