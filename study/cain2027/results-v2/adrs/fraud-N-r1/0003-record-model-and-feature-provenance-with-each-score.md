# Record model and feature provenance with each score

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors need to know which model version and which features produced each transaction score. That evidence must remain associated with the individual score for later review.

## Decision Drivers

* Audit explainability
* Reproducibility

## Considered Options

* Persist model version and scoring features per score
* Persist scores and model version only

## Decision Outcome

Chosen option: "Persist model version and scoring features per score".

Audit explainability decides the choice because the brief specifically requires the features behind each score. This costs additional storage and request-path work.

### Consequences

* Each score record includes its model version and feature values.
* Storage and write volume grow with transaction volume.

## Pros and Cons of the Options

### Persist model version and scoring features per score

* Good, because Audit explainability: each score has its model and features
* Good, because Reproducibility: scoring inputs can be reviewed later
* Bad, because Low latency: persistence adds work to the request path

### Persist scores and model version only

* Good, because Low latency: stores less data per score
* Bad, because Audit explainability: cannot establish which features produced a score
* Bad, because Reproducibility: original scoring inputs are missing
