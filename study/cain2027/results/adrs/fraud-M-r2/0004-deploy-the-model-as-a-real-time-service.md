# Deploy the model as a real-time service

* System: Card-fraud scoring service

## Context and Problem Statement

Each transaction needs a fraud score before authorization, so inference must be available online. A model service separates scoring from the payment application.

## Decision Drivers

* Online scoring
* Authorization integration

## Considered Options

* Model-as-a-service deployment (`v:30.3`)
* Model-as-dependency deployment (`v:30.18`)

## Decision Outcome

Chosen option: "Model-as-a-service deployment" (`v:30.3`).

Choose a real-time model service to provide online scoring while keeping the model separately deployable. “Productionizing Machine Learning with a Microservices Architecture” and “Three Levels of ML Software” support this deployment approach; the checked point had no warnings but was unattested.

### Consequences

* Include service communication in the latency budget.
* Operate the model service as a critical authorization dependency.

## Pros and Cons of the Options

### Model-as-a-service deployment

* Good, because Real-time predictions
* Good, because Separate deployable service
* Bad, because Adds a network hop
* Sources: `s01_p06`, `s04_p01`

### Model-as-dependency deployment

* Good, because Avoids inference network hop
* Good, because Packaged with application
* Bad, because Tighter application coupling
* Sources: `s09_p05`, `s16_p05`
