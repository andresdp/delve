# Deploy the scorer as a model-as-a-service

* System: Card-fraud scoring service

## Context and Problem Statement

Transaction scoring must remain available as traffic changes, with the model deployable independently from payment application code.

## Decision Drivers

* Peak availability
* Online scoring
* Independent deployment

## Considered Options

* Model-as-a-service deployment (`v:30.3`)
* Monolithic application architecture (`v:30.2`)

## Decision Outcome

Chosen option: "Model-as-a-service deployment" (`v:30.3`).

A real-time model service integrates with product applications and supports a separate deployment boundary suited to scaling the scorer for peaks (Productionizing Machine Learning with a Microservices Architecture; MLOps: Continuous delivery and automation pipelines in machine learning).

### Consequences

* Operate and scale the serving service separately.
* Coordinate compatibility between model and caller versions.

## Pros and Cons of the Options

### Model-as-a-service deployment

* Good, because Real-time service integration
* Good, because Independent release path
* Bad, because Requires service operations
* Sources: `s01_p06`, `s04_p01`, `s06_p13`

### Monolithic application architecture

* Good, because Single deployment unit
* Bad, because Ties model release to application
* Sources: `s03_p01`, `s16_p06`
