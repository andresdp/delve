# Serve predictions locally on each line

* System: On-device visual inspection

## Context and Problem Statement

Cameras need defect predictions while devices may have no network access. The design space offers local, distributed and batch serving options (d:5).

## Decision Drivers

* Offline inference
* Small team and tight budget

## Considered Options

* Local service/API based model serving (`v:5.2`)
* Microservice based model serving (`v:5.1`)

## Decision Outcome

Chosen option: "Local service/API based model serving" (`v:5.2`).

Offline inference decides the choice: a local service can run without network access. This gives up centralized serving and adds local deployment upkeep.

### Consequences

* Package the model with a local prediction endpoint.
* Manage model copies on production devices.

## Pros and Cons of the Options

### Local service/API based model serving

* Good, because Offline inference: serves locally
* Good, because Cost: avoids distributed serving
* Bad, because Small team: local deployment upkeep
* Sources: `d:5`, `v:5.2`

### Microservice based model serving

* Good, because Small team: centralized serving
* Bad, because Offline inference: needs connectivity
* Sources: `d:5`, `v:5.1`
