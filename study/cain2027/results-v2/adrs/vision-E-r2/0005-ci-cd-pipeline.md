# CI/CD pipeline

*How should model delivery be automated?*

* System: On-device visual inspection

## Context and Problem Statement

Models are retrained weekly and pushed to cameras that may be disconnected. A small team and tight infrastructure budget favor repeatable automation without a large platform.

## Decision Drivers

* Weekly delivery
* Tight budget
* Network independence

## Considered Options

* CI/CD pipeline (`v:8.1`)
* Build and Deployment scripts (`v:8.2`)
* Machine learning orchestrator (`v:8.3`)

## Decision Outcome

Chosen option: "CI/CD pipeline" (`v:8.1`).

Weekly delivery decides the choice: CI/CD makes repeated model packaging and release steps consistent. The trade-off is pipeline upkeep, while delivery to disconnected cameras remains a separate design problem.

### Consequences

* Automate model build and release validation.
* The pipeline does not itself define how disconnected devices receive updates.

## Pros and Cons of the Options

### CI/CD pipeline

* Good, because Weekly delivery: automates repeatable build and deployment steps
* Bad, because Network independence: device delivery still needs an offline-capable mechanism
* Bad, because Tight budget: pipeline maintenance has a cost
* Sources: `d:8`, `v:8.1`

### Build and Deployment scripts

* Good, because Tight budget: straightforward automation
* Bad, because Weekly delivery: manual execution can become error-prone
* Sources: `d:8`, `v:8.2`

### Machine learning orchestrator

* Good, because Weekly delivery: coordinates multiple pipelines and components
* Bad, because Tight budget: adds platform complexity
* Sources: `d:8`, `v:8.3`
