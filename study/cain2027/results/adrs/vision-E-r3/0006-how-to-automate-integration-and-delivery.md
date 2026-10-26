# How to automate integration and delivery?

* System: On-device visual inspection

## Context and Problem Statement

Models are retrained weekly and pushed to devices, while the team and infrastructure budget are limited. Delivery automation can connect builds with deployment steps.

## Decision Drivers

* Weekly releases
* Small team
* Tight budget

## Considered Options

* Build and Deployment scripts (`v:8.2`)
* CI/CD pipeline (`v:8.1`)
* No integration or delivery automation (`v:8.4`)

## Decision Outcome

Chosen option: "Build and Deployment scripts" (`v:8.2`).

Scripts offer a lightweight way to automate deployment steps under a tight budget, with manual triggering acceptable for a weekly cadence. The design point has no warnings, but no attesting sources.

### Consequences

* Provide a repeatable deployment script.
* Coordinate device updates when connectivity is available.

## Pros and Cons of the Options

### Build and Deployment scripts

* Good, because Automates deployment steps
* Good, because Lightweight starting point
* Bad, because Requires manual execution
* Sources: `d:8`, `v:8.2`

### CI/CD pipeline

* Good, because Automates delivery flow
* Bad, because Needs pipeline setup
* Sources: `d:8`, `v:8.1`

### No integration or delivery automation

* Good, because No automation setup
* Bad, because Repeats manual release work
* Sources: `d:8`, `v:8.4`
