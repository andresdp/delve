# What should be monitored in production?

* System: On-device visual inspection

## Context and Problem Statement

Models operate on cameras that may be offline, so central observation cannot be assumed. Monitoring should still help detect quality problems and diagnose releases.

## Decision Drivers

* Reliable production
* Network independence
* Tight budget

## Considered Options

* Model performance monitoring (`v:22.1`)
* Monitoring or logging data and predictions (`v:22.2`)
* No in-production monitoring (`v:22.3`)

## Decision Outcome

Chosen option: "Model performance monitoring" (`v:22.1`).

Reliable production decides the choice: observe model performance to identify regressions after releases. This gives up immediate centralized visibility when devices are disconnected.

### Consequences

* Collect performance signals locally and report them when connectivity returns.
* Choose domain-specific quality measures, which the design space does not specify.

## Pros and Cons of the Options

### Model performance monitoring

* Good, because Reliable production: tracks model quality measures
* Bad, because Network independence: offline devices may delay reporting
* Sources: `d:22`, `v:22.1`

### Monitoring or logging data and predictions

* Good, because Diagnosis: captures inputs and outputs
* Bad, because Tight budget: storage and review costs can grow
* Sources: `d:22`, `v:22.2`

### No in-production monitoring

* Good, because Tight budget: avoids monitoring infrastructure
* Bad, because Reliable production: quality regressions may go unnoticed
* Sources: `d:22`, `v:22.3`
