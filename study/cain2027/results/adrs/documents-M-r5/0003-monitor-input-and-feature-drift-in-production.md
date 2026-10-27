# Monitor input and feature drift in production

* System: Large-scale document classification

## Context and Problem Statement

Operators need visibility into quality drift, and changes in incoming documents can affect classifier behavior. Monitoring practices can be combined because this dimension has low exclusivity in the design space.

## Decision Drivers

* Quality drift visibility
* Changing input volume

## Considered Options

* Input and feature-drift monitoring (`v:6.2`)
* Real-time prediction-quality monitoring (`v:6.1`)

## Decision Outcome

Chosen option: "Input and feature-drift monitoring" (`v:6.2`).

Drift monitoring provides operators a direct signal when incoming data changes; “Productionizing Machine Learning with a Microservices Architecture” and Google Cloud’s “MLOps: Continuous delivery and automation pipelines in machine learning” support monitoring inputs and features. Add prediction-quality monitoring when labels become available; it is compatible as a combined practice, though the point checker accepts only one value per dimension and the batch-plus-drift-plus-elastic point was unattested.

### Consequences

* Monitoring needs baselines for expected inputs.
* Drift alerts require investigation before retraining.

## Pros and Cons of the Options

### Input and feature-drift monitoring

* Good, because Surfaces changing input patterns
* Good, because Can identify schema anomalies
* Bad, because Drift does not prove quality loss
* Sources: `s04_p03`, `s06_p02`, `s23_p03`

### Real-time prediction-quality monitoring

* Good, because Tracks prediction quality
* Good, because Shows model behavior after serving
* Bad, because Quality measurement depends on labels
* Bad, because Quality issues may appear after delay
* Sources: `s04_p02`, `s06_p06`, `s23_p04`
