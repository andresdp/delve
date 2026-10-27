# Build, test, and deploy ML pipelines and components

*How should changes reach production?*

* System: Retail demand forecasting

## Context and Problem Statement

The brief asks for fast delivery of model ideas without breaking the weekly run. Automated delivery of pipeline components supports iteration, with model promotion controlled by quality checks.

## Decision Drivers

* Fast iteration
* Weekly run stability
* Small team

## Considered Options

* Build, test, and deploy ML pipelines and components (`v:25.2`)
* Build, test, and deploy models and system components (`v:25.1`)
* No automated deployment (`v:25.3`)

## Decision Outcome

Chosen option: "Build, test, and deploy ML pipelines and components" (`v:25.2`).

Automating delivery of pipeline code and components shortens iteration while keeping weekly execution reproducible (d:25, v:25.2).

### Consequences

* Releases require pipeline checks.
* Promotion rules remain a separate control.

## Pros and Cons of the Options

### Build, test, and deploy ML pipelines and components

* Good, because Speeds component updates
* Good, because Repeatable releases
* Bad, because Requires CI setup
* Sources: `d:25`, `v:25.2`

### Build, test, and deploy models and system components

* Good, because Automates model release
* Bad, because Can couple release to run
* Sources: `d:25`, `v:25.1`

### No automated deployment

* Good, because Fewer release tools
* Bad, because Slower iteration
* Sources: `d:25`, `v:25.3`
