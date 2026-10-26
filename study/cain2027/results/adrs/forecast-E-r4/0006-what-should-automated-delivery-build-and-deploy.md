# What should automated delivery build and deploy?

* System: Retail demand forecasting

## Context and Problem Statement

Delivery automation should support model experimentation while keeping the forecasting pipeline itself reliable.

## Decision Drivers

* Fast model iteration
* Reliable weekly run
* Small team

## Considered Options

* Build, test, and deploy machine learning pipelines and components needed during pipeline runs (`v:25.2`)
* Build, test, and deploy models to be served and other system components (`v:25.1`)
* No automated deployment (`v:25.3`)

## Decision Outcome

Chosen option: "Build, test, and deploy machine learning pipelines and components needed during pipeline runs" (`v:25.2`).

Automating pipeline and component delivery directly supports dependable weekly runs; the design point check had no warnings and no attested sources.

### Consequences

* Pipeline code and runtime components are versioned and released.
* A change can be staged before the scheduled production run.

## Pros and Cons of the Options

### Build, test, and deploy machine learning pipelines and components needed during pipeline runs

* Good, because Keeps run components deployable
* Good, because Supports pipeline changes
* Bad, because Requires component release management
* Sources: `d:25`, `v:25.2`

### Build, test, and deploy models to be served and other system components

* Good, because Automates model delivery
* Bad, because Does not directly cover pipeline components
* Sources: `d:25`, `v:25.1`

### No automated deployment

* Bad, because Manual deployment slows iteration
* Sources: `d:25`, `v:25.3`
