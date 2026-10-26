# Automate model delivery

* System: On-device visual inspection

## Context and Problem Statement

A model trained centrally must be pushed to devices that may be offline. The design space covers automated integration and delivery approaches (d:8).

## Decision Drivers

* Offline inference
* Weekly retraining
* Small team and tight budget

## Considered Options

* CI/CD pipeline (`v:8.1`)
* Build and Deployment scripts (`v:8.2`)
* No integration or delivery automation (`v:8.4`)

## Decision Outcome

Chosen option: "CI/CD pipeline" (`v:8.1`).

Weekly retraining and team size decide the choice: a CI/CD pipeline can make model releases repeatable. Offline devices still require a separate rollout path for periods without connectivity.

### Consequences

* Automate model packaging and release checks.
* Provide a mechanism to stage releases for disconnected devices.

## Pros and Cons of the Options

### CI/CD pipeline

* Good, because Weekly retraining: automates delivery steps
* Good, because Small team: repeatable release workflow
* Bad, because Offline inference: device rollout still needs connectivity or staging
* Sources: `d:8`, `v:8.1`

### Build and Deployment scripts

* Good, because Cost: small initial setup
* Bad, because Small team: manual release operation
* Sources: `d:8`, `v:8.2`

### No integration or delivery automation

* Good, because Cost: no automation setup
* Bad, because Weekly retraining: manual delivery burden
* Sources: `d:8`, `v:8.4`
