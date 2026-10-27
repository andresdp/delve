# Use deployment scripts for weekly model releases

* System: On-device visual inspection

## Context and Problem Statement

The model is retrained weekly and needs a repeatable path from training output to production devices. The team is small and the infrastructure budget is tight.

## Decision Drivers

* Weekly retraining
* Small team
* Tight budget

## Considered Options

* Build and Deployment scripts (`v:8.2`)
* CI/CD pipeline (`v:8.1`)

## Decision Outcome

Chosen option: "Build and Deployment scripts" (`v:8.2`).

Scripts can automate the weekly build and rollout with limited infrastructure; this fits the team and budget constraints better than a continuously automated pipeline (d:8, v:8.2).

### Consequences

* Schedule and monitor script execution.
* Document recovery and release steps.

## Pros and Cons of the Options

### Build and Deployment scripts

* Good, because Low infrastructure needs
* Good, because Automates repeatable steps
* Bad, because Less continuous automation
* Bad, because Requires operational discipline
* Sources: `d:8`, `v:8.2`

### CI/CD pipeline

* Good, because Automated release workflow
* Good, because Repeatable integration
* Bad, because Pipeline setup and upkeep
* Bad, because May exceed team needs
* Sources: `d:8`, `v:8.1`
