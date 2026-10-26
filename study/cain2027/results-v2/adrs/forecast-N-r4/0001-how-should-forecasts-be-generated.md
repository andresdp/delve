# How should forecasts be generated?

* System: Retail demand forecasting

## Context and Problem Statement

Weekly demand must be forecast for each store and product, and the pipeline is owned end to end by a small data science team.

## Decision Drivers

* Weekly run reliability
* Fast model iteration
* End-to-end ownership

## Considered Options

* One batch pipeline for training and forecasting
* Separate training and forecast pipelines

## Decision Outcome

Chosen option: "Separate training and forecast pipelines".

Weekly run reliability decides the choice: isolate production forecasting from model development, while accepting extra operational components.

### Consequences

* Training and forecasting need a shared model handoff.
* The small team must maintain two workflows.

## Pros and Cons of the Options

### One batch pipeline for training and forecasting

* Good, because Weekly run reliability: one scheduled path
* Good, because End-to-end ownership: fewer components
* Bad, because Fast model iteration: changes can disrupt runs

### Separate training and forecast pipelines

* Good, because Weekly run reliability: isolate forecast execution
* Good, because Fast model iteration: train models independently
* Bad, because End-to-end ownership: more components to operate
