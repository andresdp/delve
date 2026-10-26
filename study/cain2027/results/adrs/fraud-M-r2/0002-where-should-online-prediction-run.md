# Where should online prediction run?

* System: Card-fraud scoring service

## Context and Problem Statement

The system must handle transaction peaks while scoring each transaction before authorization. A separately deployed model service can scale independently of payment applications.

## Decision Drivers

* Peak availability
* Online scoring
* Independent scaling

## Considered Options

* Model-as-a-service deployment (`v:30.3`)
* Monolithic application architecture (`v:30.2`)

## Decision Outcome

Chosen option: "Model-as-a-service deployment" (`v:30.3`).

A dedicated real-time model service supports independent capacity management during peaks. “Productionizing Machine Learning with a Microservices Architecture” and “Three Levels of ML Software” document this approach.

### Consequences

* Operate the model endpoint as a production service.
* Scale its capacity with transaction demand.

## Pros and Cons of the Options

### Model-as-a-service deployment

* Good, because Independent deployment
* Good, because Real-time integration
* Bad, because Adds service operations
* Sources: `s04_p10`, `s19_p08`

### Monolithic application architecture

* Good, because Fewer service boundaries
* Bad, because Couples model and application releases
* Sources: `s03_p01`
