# Automate the recurring ML workflow

* System: On-device visual inspection

## Context and Problem Statement

Weekly training and distribution are recurring work for a small team, so lifecycle tasks should run through a repeatable workflow.

## Decision Drivers

* Weekly retraining
* Small team
* Tight budget

## Considered Options

* Automated ML lifecycle workflows (`v:38.1`)
* Composable DataOps-centered ML toolchain (`v:38.2`)
* Production engineering and DevOps omission (`v:38.4`)

## Decision Outcome

Chosen option: "Automated ML lifecycle workflows" (`v:38.1`).

Automating recurring training and release tasks reduces manual effort across the weekly lifecycle. The checked point combines this with edge inference and schedule-based training, but was unattested; the rival cloud-service and drift-triggered point was also unattested, so evidence does not establish either as a complete system pattern.

### Consequences

* Build and maintain the training and release workflow.
* Keep the automation scope proportionate to the team and budget.

## Pros and Cons of the Options

### Automated ML lifecycle workflows

* Good, because Automates recurring work
* Good, because Covers deployment workflow
* Bad, because Requires initial setup
* Bad, because Needs operational upkeep
* Sources: `s22_p03`, `s22_p04`, `s25_p01`

### Composable DataOps-centered ML toolchain

* Good, because Replaceable components
* Good, because Composable workflow
* Bad, because Integration overhead
* Bad, because Mixed evidence
* Sources: `s22_p03`

### Production engineering and DevOps omission

* Good, because Less setup initially
* Bad, because Manual recurring work
* Bad, because Rejected approach
* Sources: `s29_p02`
