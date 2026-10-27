# Automate model delivery with a CI/CD pipeline

* System: On-device visual inspection

## Context and Problem Statement

Models are retrained weekly and pushed to devices. Automating the build and delivery steps can reduce recurring manual work for a small team.

## Decision Drivers

* Weekly model releases
* Small team
* Disconnected devices

## Considered Options

* CI/CD pipeline (`v:8.1`)
* Build and Deployment scripts (`v:8.2`)

## Decision Outcome

Chosen option: "CI/CD pipeline" (`v:8.1`).

A pipeline can make weekly releases repeatable; delivery to disconnected devices requires a separate offline distribution mechanism (d:8, v:8.1).

### Consequences

* Maintain pipeline credentials and release configuration.
* Prepare signed or otherwise verified model packages for device delivery.

## Pros and Cons of the Options

### CI/CD pipeline

* Good, because Repeatable delivery
* Good, because Less manual effort
* Bad, because Pipeline upkeep
* Sources: `d:8`, `v:8.1`

### Build and Deployment scripts

* Good, because Low initial setup
* Bad, because Manual execution
* Bad, because Less integrated checks
* Sources: `d:8`, `v:8.2`
